from django import forms
from django.utils.translation import gettext as _


class ProfileForm(forms.Form):
    email = forms.EmailField(label=_("Email address"), max_length=150)
    first_name = forms.CharField(label=_("First name"), max_length=150, required=False)
    last_name = forms.CharField(label=_("Last name"), max_length=150, required=False)
    birth_date = forms.DateField(
        label=_("Date of birth"), required=False, widget=forms.DateInput()
    )
    old_password = forms.CharField(
        label=_("Current password"),
        max_length=128,
        required=False,
        widget=forms.PasswordInput(),
    )
    new_password_1 = forms.CharField(
        label=_("New password"),
        max_length=128,
        required=False,
        widget=forms.PasswordInput(),
    )
    new_password_2 = forms.CharField(
        label=_("Repeat password"),
        max_length=128,
        required=False,
        widget=forms.PasswordInput(),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        if self.user:
            self.initial.update(
                {
                    "email": self.user.email,
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "birth_date": self.user.birth_date,
                }
            )

    def clean(self):
        cleaned_data = super().clean()
        old_pw = cleaned_data.get("old_password")
        new_pw_1 = cleaned_data.get("new_password_1")
        new_pw_2 = cleaned_data.get("new_password_2")

        if any([old_pw, new_pw_1, new_pw_2]):
            if not old_pw:
                self.add_error("old_password", _("The current password is required"))
            elif not self.user.check_password(old_pw):
                self.add_error("old_password", _("Wrong password"))
            if not new_pw_1 or not new_pw_2:
                if not new_pw_1:
                    self.add_error("new_password_1", _("Type in the new password"))
                if not new_pw_2:
                    self.add_error("new_password_2", _("Verify your new password"))
            elif new_pw_1 != new_pw_2:
                self.add_error(
                    "new_password_1", _("The passwords typed in are not equal")
                )
                self.add_error(
                    "new_password_2", _("The passwords typed in are not equal")
                )
