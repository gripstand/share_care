from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

User = get_user_model()

@receiver(post_save, sender=User)
def send_initial_password_setup_email(sender, instance, created, **kwargs):
    print("Signal `post_save` for User model received.")
    print(f"User instance created: {created}")
    print(f"User has a usable password: {instance.has_usable_password()}")
    if created and not instance.has_usable_password():
        print("Conditions met: User created without a password. Attempting to send email.")
        # The user was just created and has no password set.
        # We'll use Django's built-in token generator to create the reset link
        context = {
            'email': instance.email,
            'domain': settings.DOMAIN_NAME,  # e.g., 'www.your-website.com'
            'site_name': settings.SITE_NAME, # e.g., 'Your Website Name'
            'uid': urlsafe_base64_encode(force_bytes(instance.pk)),
            'user': instance,
            'token': default_token_generator.make_token(instance),
            'protocol': 'http',  # or 'https' in production
        }

        # Render the email content from templates
        email_html_message = render_to_string('registration/initial_password_setup_email.html', context)
        email_plaintext_message = render_to_string('registration/initial_password_setup_email.txt', context)

        # Send the email
        msg = EmailMultiAlternatives(
            f'[{settings.SITE_NAME}] Set up your password',
            email_plaintext_message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email]
        )
    
        msg.attach_alternative(email_html_message, "text/html")
        msg.send()