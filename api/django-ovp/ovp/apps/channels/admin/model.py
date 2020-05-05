from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import InlineModelAdmin
from .forms import AdminModelForm
from .formset import AdminInlineFormSet
from jet.admin import CompactInline as BaseCompactInline


class StackedInline(InlineModelAdmin):
    template = 'admin/edit_inline/stacked.html'
    formset = AdminInlineFormSet


class TabularInline(InlineModelAdmin):
    template = 'admin/edit_inline/tabular.html'
    formset = AdminInlineFormSet


class CompactInline(BaseCompactInline):
    formset = AdminInlineFormSet


class ChannelModelAdmin(ModelAdmin):
    form = AdminModelForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(channel=request.user.channel)

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.save()
        else:
            obj.save(object_channel=request.user.channel.slug)

    def save_formset(self, request, form, formset, change):
        formset.save(request=request)
