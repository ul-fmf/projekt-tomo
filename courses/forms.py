from django import forms
from .models import Course

class CoursesForm(forms.Form):
    courses = forms.ModelMultipleChoiceField(
        label='Moji predmeti',
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    def update_courses(self, user):
        user.courses = self.cleaned_data['courses']
        user.save()
