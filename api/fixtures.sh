#!/bin/bash

script_name=$0
script_full_path=$(dirname "$0")

cd $script_full_path

#echo "Core: "
#python manage.py loaddata addresstypes components address posts
#
#echo "Images: "
#python manage.py loaddata images
#
#echo "Users: "
#python manage.py loaddata users profiles
#
#echo "Organizations: "
#python manage.py loaddata organizations
#
#echo "Project: "
#python manage.py loaddata projects roles works jobs jobdates applies categories projectbookmarks
#
#echo "Catalogue: "
#python manage.py loaddata catalogue
#
## Donations
## TODO: Subscription (finish subscriptions on donations app first)
#echo "Donations: "
#python manage.py loaddata sellers transactions
#
## Faq
#echo "FAQ: "
#python manage.py loaddata faqcategory faq

echo "Notifybox: "
if [ -z ${AWS_ACCESS_KEY_ID+x} ] || [ -z ${AWS_SECRET_ACCESS_KEY+x} ] || [ -z ${AWS_DEFAULT_REGION+x} ] ;
  then
    echo "Warning: not all AWS env variables are set. Creating notifybox app without aws credentials."
    python manage.py create_notifybox_app default myadminsecretkey 2>/dev/null;
  else
    python manage.py create_notifybox_app default myadminsecretkey --set-aws-credentials $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY $AWS_DEFAULT_REGION 2>/dev/null;
fi
if [ $? -ne 0 ]; then
    echo "Failed to create notifybox app. Check if your notifybox is up."
fi
python manage.py import_emails_to_notifybox default "Dev Atados <site@atados.com.br>" 2>/dev/null;
if [ $? -ne 0 ]; then
    echo "Failed to import emails to notifybox. Check if your notifybox is up."
fi
