from django import forms

from accounts.models import StudentProfile
from learning.models import HomeworkSubmission


class StudentProfileForm(forms.Form):
    full_name = forms.CharField(label="To‘liq ism", max_length=150)
    phone = forms.CharField(label="Telefon", max_length=30, required=False)
    bio = forms.CharField(
        label="Bio",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    avatar = forms.ImageField(label="Avatar", required=False)
    date_of_birth = forms.DateField(
        label="Tug‘ilgan sana",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self):
        profile = self.user.profile
        profile.full_name = self.cleaned_data["full_name"].strip()
        profile.phone = (self.cleaned_data.get("phone") or "").strip()
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            profile.avatar = avatar
        profile.save()

        student, _ = StudentProfile.objects.get_or_create(user=self.user)
        student.bio = (self.cleaned_data.get("bio") or "").strip()
        student.date_of_birth = self.cleaned_data.get("date_of_birth")
        student.save()
        return profile


class HomeworkSubmitForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ["answer_text", "attachment"]
        widgets = {"answer_text": forms.Textarea(attrs={"rows": 6})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attachment"].required = False
        self.fields["answer_text"].required = False

    def clean(self):
        cleaned = super().clean()
        if not (cleaned.get("answer_text") or "").strip() and not cleaned.get("attachment"):
            if not (self.instance and self.instance.pk and self.instance.attachment):
                raise forms.ValidationError(
                    "Matn yoki fayl yuklang."
                )
        return cleaned
