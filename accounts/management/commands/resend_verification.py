from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = "Resend verification email to a given user by email"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Email of the user")

    def handle(self, *args, **options):
        email = options["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f"No user found with email {email}")

        # Generate token (same logic you used before — replace if you use a model)
        token = str(uuid.uuid4())

        verification_url = f"{settings.SITE_URL}{reverse('accounts:verify_email', kwargs={'token': token})}"

        subject = "Verify your email"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]

        # Plain text fallback
        text_content = f"Please verify your account by clicking the following link:\n\n{verification_url}"

        # Render HTML template
        html_content = render_to_string(
            "accounts/email/email_verification_email.html",
            {"user": user, "verification_url": verification_url},
        )

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        self.stdout.write(self.style.SUCCESS(f"Verification email sent to {email}"))
