"""
Forms for dating app
"""
from django import forms
from .models import Preference


class PreferenceForm(forms.ModelForm):
    """
    Form for creating and updating user matching preferences.
    Includes validation for age range and gender selection.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    # Use checkboxes for gender selection instead of text field
    preferred_genders = forms.MultipleChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text='Select at least one gender preference'
    )

    class Meta:
        model = Preference
        fields = ['min_age', 'max_age', 'preferred_genders', 'max_distance']
        widgets = {
            'min_age': forms.NumberInput(attrs={
                'min': 18, 'max': 99, 'class': 'form-control'
            }),
            'max_age': forms.NumberInput(attrs={
                'min': 18, 'max': 99, 'class': 'form-control'
            }),
            'max_distance': forms.NumberInput(attrs={
                'min': 0, 'class': 'form-control',
                'placeholder': 'Optional (for future geolocation)'
            }),
        }
        help_texts = {
            'min_age': 'Minimum age you want to see (18-99)',
            'max_age': 'Maximum age you want to see (18-99)',
            'max_distance': 'Maximum distance in km (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert comma-separated string to list for existing preferences
        if self.instance and self.instance.pk:
            if self.instance.preferred_genders:
                self.initial['preferred_genders'] = (
                    self.instance.get_preferred_genders_list()
                )

    def clean(self):
        """Validate form data"""
        cleaned_data = super().clean()
        min_age = cleaned_data.get('min_age')
        max_age = cleaned_data.get('max_age')
        preferred_genders = cleaned_data.get('preferred_genders')

        # Validate age range
        if min_age and max_age:
            if min_age >= max_age:
                raise forms.ValidationError({
                    'min_age': 'Minimum age must be less than maximum age.'
                })

        # Validate at least one gender is selected
        if not preferred_genders or len(preferred_genders) == 0:
            raise forms.ValidationError({
                'preferred_genders': 'Please select at least one gender preference.'
            })

        return cleaned_data

    def save(self, commit=True):
        """Convert gender list to comma-separated string before saving"""
        instance = super().save(commit=False)
        preferred_genders = self.cleaned_data.get('preferred_genders', [])
        if preferred_genders:
            instance.preferred_genders = ','.join(preferred_genders)
        else:
            instance.preferred_genders = 'M,F,O'  # Default

        if commit:
            instance.save()
        return instance

