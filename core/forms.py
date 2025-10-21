from django import forms
from django.core.mail import send_mail
from django.conf import settings
from .models import SupportRequest


class SupportForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=150)
    message = forms.CharField(widget=forms.Textarea)

    def save(self):
        cleaned = self.cleaned_data

        # Save to DB
        SupportRequest.objects.create(
            name=cleaned["name"],
            email=cleaned["email"],
            subject=cleaned["subject"],
            message=cleaned["message"],
        )

        # Email to admin/support inbox
        subject = f"[Support] {cleaned['subject']}"
        body = (
            f"Name: {cleaned['name']}\n"
            f"Email: {cleaned['email']}\n\n"
            f"Message:\n{cleaned['message']}"
        )
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.SUPPORT_EMAIL],
        )

        # Auto-acknowledge email to user
        ack_subject = "We’ve received your support request"
        ack_message = (
            f"Hi {cleaned['name']},\n\n"
            "Thank you for reaching out to Djangify Support. "
            "Your request has been received and our team will respond within 48 hours (Mon–Fri).\n\n"
            "Here’s a copy of your message:\n"
            f"Subject: {cleaned['subject']}\n"
            f"Message: {cleaned['message']}\n\n"
            "Best regards,\n"
            "The Djangify Support Team"
        )
        send_mail(
            ack_subject,
            ack_message,
            settings.DEFAULT_FROM_EMAIL,
            [cleaned["email"]],
        )
