from copy import deepcopy
from django.forms import ChoiceField, ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoBaseUserAdmin
from django.contrib.auth.forms import UserChangeForm as DjangoBaseUserChangeForm, UsernameField
from allauth.account.models import EmailAddress
from allauth.account.forms import ResetPasswordForm


class BaseUserChangeForm(DjangoBaseUserChangeForm):
    email_verification = ChoiceField(
        label=_("Emails & Verification"),
        choices=[
            ('none', "No action taken."),
            ('verify', "Send verification email."),
            ('approve', "Mark email as already verified."),
            ('password', "Mark email verified and send password reset email."),
        ]
    )

    class Meta:
        model = get_user_model()
        fields = "__all__"
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({'autofocus': True})

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email:
            email_check = EmailAddress.objects.filter(email__iexact=email)
            if self.instance.id is not None:
                email_check = email_check.exclude(user=self.instance)
            if email_check.exists():
                raise ValidationError(_("This email is already associated with another user."))
        return email

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get("password")

    def save(self, commit=True):
        if self.instance.id is None:
            self.instance.set_unusable_password()
        return super().save(commit=False)


class BaseUserAdmin(DjangoBaseUserAdmin):
    add_form_template = 'admin/change_form.html'
    add_form = form = BaseUserChangeForm
    add_fieldsets = DjangoBaseUserAdmin.fieldsets
    add_fieldsets[0][1]['fields'] = ('username', 'email', 'email_verification')
    add_fieldsets[1][1]['fields'] = ('first_name', 'last_name')
    fieldsets = deepcopy(add_fieldsets)
    fieldsets[0][1]['fields'] += ('password',)

    def save_model(self, request, user, form, change):
        super().save_model(request, user, form, change)
        if user.email:
            EmailAddress.objects.filter(user=user).update(primary=False)
            email = EmailAddress.objects.filter(email__iexact=user.email).first()

            if not email:
                email = EmailAddress.objects.create(
                    user=user, email=user.email, primary=True, verified=False
                )

            elif not email.primary:
                email.primary = True

            verification = form.cleaned_data['email_verification']
            if verification == 'verify':
                email.send_confirmation(request)

            elif verification == 'approve':
                email.verified = True

            elif verification == 'password':
                email.verified = True
                reset = ResetPasswordForm(data={'email': user.email})
                assert reset.is_valid()
                reset.save(request)

            email.save()

        else:
            EmailAddress.objects.filter(user=user).delete()
