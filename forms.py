"""Contact form. Server-side validation with allow-listed choices (Baseline C2)."""
import re

from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectChoice
from wtforms import BooleanField, EmailField, SelectField, StringField, TelField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp, ValidationError

from content import BUDGET_CHOICES, SERVICE_CHOICES

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _no_control_chars(form, field):
    if field.data and _CONTROL.search(field.data):
        raise ValidationError("Please remove unusual characters.")


def _single_line(form, field):
    if field.data and ("\n" in field.data or "\r" in field.data):
        raise ValidationError("Please keep this to one line.")


def _strip(value):
    return value.strip() if isinstance(value, str) else value


class ContactForm(FlaskForm):
    name = StringField("Full name", filters=[_strip],
                       validators=[DataRequired("Please enter your name."), Length(2, 120, "Please enter between 2 and 120 characters."), _single_line, _no_control_chars])
    email = EmailField("Email address", filters=[_strip],
                       validators=[DataRequired("Please enter your email."), Email("Please enter a valid email."), Length(max=254), _single_line])
    phone = TelField("Phone or WhatsApp (optional)", filters=[_strip],
                     validators=[Optional(), Length(7, 20), Regexp(r"^\+?[0-9 ()-]{7,20}$", message="Use digits, spaces and an optional +.")])
    organisation = StringField("Organisation (optional)", filters=[_strip],
                               validators=[Optional(), Length(max=160), _single_line, _no_control_chars])
    service = SelectField("What do you need?", choices=[SelectChoice(v, l) for v, l in SERVICE_CHOICES],
                          validators=[DataRequired("Please choose a service.")])
    budget = SelectField("Budget range (excl. VAT)", choices=[SelectChoice(v, l) for v, l in BUDGET_CHOICES],
                         validators=[DataRequired("Please choose a range.")])
    message = TextAreaField("Tell us about the project", filters=[_strip],
                            validators=[DataRequired("Please describe what you need."), Length(20, 3000, "Please write between 20 and 3,000 characters."), _no_control_chars])
    consent = BooleanField("I agree that Apex Solutions may use these details to reply to my enquiry, as described in the privacy notice.",
                           validators=[DataRequired("Please confirm so we can reply.")])
    # Honeypot: hidden from people, filled by naive bots (Baseline G6, first layer).
    website = StringField("Leave this empty", validators=[Optional()])


# --- Accounts and dashboards ---------------------------------------------

from flask_wtf.file import FileField  # noqa: E402
from wtforms import PasswordField  # noqa: E402

from models import Document, Enquiry  # noqa: E402


class LoginForm(FlaskForm):
    email = EmailField("Email address", filters=[_strip], validators=[DataRequired("Enter your email."), Length(max=254)])
    password = PasswordField("Password", validators=[DataRequired("Enter your password."), Length(max=128)])


class ForgotForm(FlaskForm):
    email = EmailField("Email address", filters=[_strip], validators=[DataRequired("Enter your email."), Email("Enter a valid email."), Length(max=254)])


class SetPasswordForm(FlaskForm):
    password = PasswordField("New password", validators=[DataRequired("Choose a password."), Length(max=128)])
    confirm = PasswordField("Repeat new password", validators=[DataRequired("Repeat the password.")])

    def validate_confirm(self, field):
        if field.data != self.password.data:
            raise ValidationError("The two passwords do not match.")


class ChangePasswordForm(SetPasswordForm):
    current = PasswordField("Current password", validators=[DataRequired("Enter your current password."), Length(max=128)])


class ProfileForm(FlaskForm):
    name = StringField("Your name", filters=[_strip], validators=[DataRequired("Enter your name."), Length(2, 120), _single_line, _no_control_chars])
    organisation = StringField("Organisation (optional)", filters=[_strip], validators=[Optional(), Length(max=160), _single_line, _no_control_chars])


class ClientForm(FlaskForm):
    name = StringField("Contact name", filters=[_strip], validators=[DataRequired("Enter a name."), Length(2, 120), _single_line, _no_control_chars])
    email = EmailField("Email address", filters=[_strip], validators=[DataRequired("Enter an email."), Email("Enter a valid email."), Length(max=254)])
    organisation = StringField("Organisation", filters=[_strip], validators=[Optional(), Length(max=160), _single_line, _no_control_chars])


class DocumentForm(FlaskForm):
    title = StringField("Title", filters=[_strip], validators=[DataRequired("Give the document a title."), Length(2, 160), _single_line, _no_control_chars])
    description = TextAreaField("Short description (optional)", filters=[_strip], validators=[Optional(), Length(max=500), _no_control_chars])
    category = SelectField("Category", choices=[SelectChoice(c, c) for c in Document.CATEGORIES])
    visibility = SelectField("Who can download it", choices=[SelectChoice(k, v) for k, v in Document.VISIBILITY.items()])
    client_id = SelectField("Client (when shared with one client)", choices=[], validate_choice=False)
    file = FileField("File (PDF, Word, Excel or PowerPoint)")

    def validate_client_id(self, field):
        if self.visibility.data == "client" and not field.data:
            raise ValidationError("Choose the client to share this document with.")


class DocumentEditForm(DocumentForm):
    file = None


class StatusForm(FlaskForm):
    status = SelectField("Status", choices=[SelectChoice(s, s.capitalize()) for s in Enquiry.STATUSES])


class ConfirmForm(FlaskForm):
    """Empty form used for CSRF-protected buttons (delete, disable, reset link)."""
