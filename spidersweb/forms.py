from django import forms
from django.core.exceptions import ValidationError

class ScrapyForm(forms.Form):

    start_id = forms.CharField(widget=forms.HiddenInput())
    end_id = forms.CharField(widget=forms.HiddenInput())
        
    city = forms.CharField(label='City', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    state_id = forms.CharField(label='State ID', max_length=2, widget=forms.TextInput(attrs={'class': 'form-control'}),required=True)
    website = forms.URLField(label='Website URL', widget=forms.URLInput(attrs={'class': 'form-control'}),required=True)

    municipality_main_tel_xpath = forms.CharField(
        label='Municipality Main Tel XPath',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    building_department_main_email_xpath = forms.CharField(
        label='Building Department Main Email XPath',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    building_department_main_phone_xpath = forms.CharField(
        label='Building Department Main Phone XPath',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    chief_building_official_name_xpath = forms.CharField(
        label='Chief Building Official Name XPath',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        municipality_main_tel_xpath = cleaned_data.get('municipality_main_tel_xpath')
        building_department_main_email_xpath = cleaned_data.get('building_department_main_email_xpath')
        building_department_main_phone_xpath = cleaned_data.get('building_department_main_phone_xpath')
        chief_building_official_name_xpath = cleaned_data.get('chief_building_official_name_xpath')

        # Check if at least one XPath field is filled
        if not any([municipality_main_tel_xpath, building_department_main_email_xpath,
                    building_department_main_phone_xpath, chief_building_official_name_xpath]):
            raise ValidationError("At least one XPath field must be filled.")

        return cleaned_data