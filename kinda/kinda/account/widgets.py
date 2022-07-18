from django.forms import Select, TextInput
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
from django.forms import Textarea
from django_filters import widgets

phone_prefixes = [
    ('+{}'.format(k), '+{}'.format(k)) for
    (k, v) in sorted(COUNTRY_CODE_TO_REGION_CODE.items())]


class PhonePrefixWidget(PhoneNumberPrefixWidget):
    """Uses choices with tuple in a simple form of "+XYZ: +XYZ".

    Workaround for an issue:
    https://github.com/stefanfoulis/django-phonenumber-field/issues/82
    """

    template_name = 'account/snippets/phone_prefix_widget.html'

    def __init__(self, attrs=None):
        widgets = (Select(attrs=attrs, choices=phone_prefixes), TextInput())
        # pylint: disable=bad-super-call
        super(PhoneNumberPrefixWidget, self).__init__(widgets, attrs)


class DatalistTextWidget(Select):
    template_name = "account/snippets/datalist.html"
    input_type = "text"

    def get_context(self, *args):
        context = super(DatalistTextWidget, self).get_context(*args)
        context['widget']['type'] = self.input_type
        return context

    def format_value(self, value):
        value = super(DatalistTextWidget, self).format_value(value)
        return value[0]

class RichTextEditorWidget(Textarea):
    """A WYSIWYG editor widget using medium-editor."""

    def __init__(self, attrs=None):
        default_attrs = {'class': 'rich-text-editor'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

class MoneyRangeWidget(widgets.RangeWidget):
    def __init__(self, attrs=None):
        self.currency = getattr(settings, 'DEFAULT_CURRENCY')
        money_widgets = (MoneyInput(self.currency), MoneyInput(self.currency))
        # pylint: disable=bad-super-call
        super(widgets.RangeWidget, self).__init__(money_widgets, attrs)