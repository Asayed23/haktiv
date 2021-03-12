from django.utils.translation import ugettext_lazy as _
from django import forms
from ..models import RegisteredUser

class RegisteredUserAdminForm(forms.ModelForm):
    class Meta:
        model = RegisteredUser
        exclude = tuple()
    message = forms.CharField(widget=forms.Textarea(attrs=dict(cols=80, rows=20)), required=False, label=_("Reason (In email)"),
                              help_text=_("Approved / Rejected letter will be added to mail message."))
    def save(self, *args, **kwargs):
        if self.cleaned_data["message"]:
            pass
        return super(RegisteredUserAdminForm, self).save(*args, **kwargs)
    def clean(self):
        if self.cleaned_data["message"]:
            self.cleaned_data["message"] = ""
        return self.cleaned_data
