from django.forms.models import BaseInlineFormSet
from ovp.apps.channels.models.abstract import ChannelRelationship


class AdminInlineFormSet(BaseInlineFormSet):
    """
    We override BaseInlineFormSet because we need
    to pass the request down to the model save method
    """

    def save(self, commit=True, request=None):
        if not commit:
            self.saved_forms = []

            def save_m2m():
                for form in self.saved_forms:
                    form.save_m2m()
            self.save_m2m = save_m2m

        new_objects = self.save_new_objects(commit, request=request)
        result = self.save_existing_objects(commit) + new_objects
        return result

    def save_new_objects(self, commit=True, request=None):
        self.new_objects = []
        for form in self.extra_forms:
            if not form.has_changed():
                continue
            if self.can_delete and self._should_delete_form(form):
                continue
            self.new_objects.append(
                self.save_new(form, commit=commit, request=request)
            )
            if not commit:
                self.saved_forms.append(form)
        return self.new_objects

    def save_new(self, form, commit=True, request=None):
        # Ensure the latest copy of the related instance is present on each
        # form (it may have been saved after the formset was originally
        # instantiated).
        setattr(form.instance, self.fk.name, self.instance)
        # Use commit=False so we can assign the parent key afterwards, then
        # save the object.
        obj = form.save(commit=False)
        pk_value = getattr(self.instance, self.fk.remote_field.field_name)
        setattr(obj, self.fk.get_attname(), getattr(pk_value, 'pk', pk_value))
        if commit and issubclass(obj.__class__, ChannelRelationship):
            obj.save(object_channel=request.user.channel.slug)
        if commit and not issubclass(obj.__class__, ChannelRelationship):
            obj.save()

        # form.save_m2m() can be called via
        # the formset later on if commit=False
        if commit and hasattr(form, 'save_m2m'):
            form.save_m2m()
        return obj
