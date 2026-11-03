"""Optional enquiry notification by SMTP.

Baseline G8: From and To are fixed in config, never taken from the form, and the
subject contains no user input. The visitor's details go in the body only.
"""
import logging
import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app

from content import BUDGET_CHOICES, SERVICE_CHOICES

log = logging.getLogger(__name__)


def _send(to_addr, subject, body):
    """Send one plain-text email. From is fixed; subject and To never come from form input (G8)."""
    cfg = current_app.config
    if not (cfg["SMTP_HOST"] and cfg["MAIL_FROM"] and to_addr):
        return False
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg["MAIL_FROM"]
    msg["To"] = to_addr
    msg.set_content(body)
    try:
        context = ssl.create_default_context()  # TLS verified (F8)
        with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=10) as smtp:
            smtp.starttls(context=context)
            if cfg["SMTP_USER"]:
                smtp.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            smtp.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError):
        log.exception("Email could not be sent (%s)", subject)
        return False


def send_setup_link(user, link):
    return _send(user.email, "Your Apex Solutions client account",
                 f"Hello {user.name},\n\nAn Apex Solutions client account has been created for you. "
                 f"Open this link to choose your password. It works once and expires in "
                 f"{current_app.config['SETUP_LINK_HOURS']} hours:\n\n{link}\n\n"
                 "If you were not expecting this, you can ignore this email.\n")


def send_reset_link(user, link):
    return _send(user.email, "Reset your Apex Solutions password",
                 f"Hello {user.name},\n\nUse this link to choose a new password. It works once and expires in "
                 f"{current_app.config['RESET_LINK_MINUTES']} minutes:\n\n{link}\n\n"
                 "If you did not ask for this, you can ignore this email. Your password has not changed.\n")


def notify_new_enquiry(enquiry):
    cfg = current_app.config
    if not (cfg["SMTP_HOST"] and cfg["MAIL_FROM"] and cfg["MAIL_TO"]):
        return False

    services = dict(SERVICE_CHOICES)
    budgets = dict(BUDGET_CHOICES)
    msg = EmailMessage()
    msg["Subject"] = "New website enquiry"
    msg["From"] = cfg["MAIL_FROM"]
    msg["To"] = cfg["MAIL_TO"]
    msg.set_content(
        "A new enquiry was submitted on the website.\n\n"
        f"Reference: {enquiry.id}\n"
        f"Name: {enquiry.name}\n"
        f"Email: {enquiry.email}\n"
        f"Phone: {enquiry.phone or '-'}\n"
        f"Organisation: {enquiry.organisation or '-'}\n"
        f"Service: {services.get(enquiry.service, enquiry.service)}\n"
        f"Budget: {budgets.get(enquiry.budget, enquiry.budget)}\n\n"
        f"{enquiry.message}\n"
    )
    try:
        context = ssl.create_default_context()  # TLS verified (F8)
        with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=10) as smtp:
            smtp.starttls(context=context)
            if cfg["SMTP_USER"]:
                smtp.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            smtp.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError):
        # The enquiry is already saved; log without personal data (J2).
        log.exception("Enquiry notification email failed for reference %s", enquiry.id)
        return False
