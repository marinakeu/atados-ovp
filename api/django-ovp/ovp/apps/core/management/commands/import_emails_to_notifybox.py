import re
import os
import collections
import logging
import json
from operator import itemgetter
from typing import List
from django.template.loaders.app_directories import get_app_template_dirs
from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.staticfiles import finders
from ovp.apps.core.notifybox import NotifyBoxApi
from ovp.apps.users.models.profile import get_profile_model
from ovp.apps.users.models import User
from ovp.apps.organizations.models import Organization
from ovp.apps.channels.models import ChannelSetting

def get_email_template_dirs(channel: str) -> str:
    channel_filtered = [ x for x in get_app_template_dirs('templates')
                            if 'channels' not in x or f'channels/{channel}' in x ]
    email_template_path = [ os.path.join(x, channel, 'email') for x in channel_filtered ]
    existing_paths = [ x for x in email_template_path if os.path.exists(x) ]
    return list(reversed(existing_paths))

def get_template_list(template_dir: str) -> List[str]:
    return [x[0:-10]
                for x in os.listdir(template_dir)
                if x.endswith('-body.html')
           ]

def load_file(path: str) -> str:
    f = open(path, 'r')
    content = f.read()
    f.close()
    return content

def load_template_file(name: str, dirs: List[str]) -> str:
    content = None
    for template_dir in dirs:
        try:
            content = load_file(os.path.join(template_dir, name))
            break
        except:
            continue
    return content

def extract_template(template: str) -> str:
    pattern = re.compile(r'^{% block content %}(.*){% endblock(?: content)? %}$', re.DOTALL | re.MULTILINE)
    match = pattern.search(template)

    if not match:
        logging.warn('Could not extract template.')
        return template

    return match[1]

def load_base(dir_path: str):
    remove = ['{% load inlinecss %}', '{% endinlinecss %}']
    template = load_template_file('base-body.html', [dir_path])
    for item in remove:
        template = template.replace(item, "")
    return template

def inject_content(base: str, content: str):
    return base.replace(
        '{% block content %}{% endblock %}',
        content
    )

def inject_css(base: str, css: str):
    return base.replace(
        '{% inlinecss "email/base.css" %}',
        f'<style>\n{ css }\n</style>'
    )

def load_template(name: str, dirs: List[str]):
    body = load_template_file(f'{name}-body.html', dirs)
    subject = load_template_file(f'{name}-subject.txt', dirs)
    extracted_body = extract_template(body)
    return (subject, extracted_body)

def convert_to_handlebars(body: str):
    a = re.sub(r'{%\s*if (.*?)\s*%}', r'{{#if \1}}', body)
    b = re.sub(r'{%\s*elif (.*?)\s*%}', r'{{else if \1}}', a)
    c = re.sub(r'{%\s*endif\s*%}', r'{{/if}}', b)
    d = re.sub(r'{%\s*else\s*%}', r'{{else}}', c)
    return d

def get_kind_and_recipient_type(template):
    split = template.split('-')
    if len(split) == 1:
        return template, None
    recipient_type = split[-1]
    kind = "-".join(split[0:-1])

    return kind, recipient_type

def insert_template(email_sender, kind, recipient_type, subject, body, client):
    recipient_type = recipient_type if recipient_type else "default"

    # Create kind
    kind_id, kind_value = itemgetter('id', 'value')(client.getOrCreateKind(kind))

    # Create template
    template_data = {
        "sender": email_sender,
        "subject": subject
    }
    template = client.createOrUpdateTemplate(kind_id, 'email', recipient_type, 'pt-br', json.dumps(template_data), body)

    # Create trigger
    trigger = client.createOrUpdateTrigger(kind_id, template["id"], recipient_type)
    logging.info(f'Kind: ({kind_id}) {kind_value}')
    logging.info(f'Recipient type: {recipient_type}')
    logging.info(f'Template version: {template["version"]}')
    logging.info(f'Trigger: {trigger}')
    logging.info('---')

def import_all(channel: str, email_sender: str, dry_run: bool = True):
    """ Import email templates to notifybox
    """
    access_key = ChannelSetting.objects.get(channel__slug = channel, key="NOTIFYBOX_ACCESS_KEY").value
    secret_key = ChannelSetting.objects.get(channel__slug = channel, key="NOTIFYBOX_SECRET_KEY").value
    client = NotifyBoxApi(access_key, secret_key)

    unwanted = [ 'base', 'userDigest', 'userDigest-aws', 'newsletter' ]
    template_dirs = get_email_template_dirs(channel)
    templates = set()

    for template_dir in template_dirs:
        templates.update(
            [ x for x in get_template_list(template_dir)
                if x not in unwanted ]
        )

    base_template = load_base(template_dirs[0])
    css = load_file(finders.find('email/base.css'))

    for template in templates:
        subject, body = load_template(template, template_dirs)
        body_with_content = inject_content(base_template, body)
        body_with_css = inject_css(body_with_content, css)
        body_handlebars = convert_to_handlebars(body_with_css)
        kind, recipient_type = get_kind_and_recipient_type(template)

        insert_template(email_sender, kind, recipient_type, subject, body_handlebars, client)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'channel',
            help='Channel slug',
            type=str,
        )
        parser.add_argument(
            'email_sender',
            help='Email sender',
            type=str,
        )

    def handle(self, *args, **options):
        # Converts value from verbosity int to logging library
        # level.
        # 1 -> 30 (logging.WARNING)
        # 2 -> 20 (logging.INFO)
        # 3 -> 10 (logging.DEBUG)
        loggingLevel = 40 - (options['verbosity'] * 10)

        logger = logging.getLogger()
        console = logging.StreamHandler()

        logger.setLevel(loggingLevel)
        console.setLevel(loggingLevel)

        logger.addHandler(console)

        import_all(options['channel'], options['email_sender'])
