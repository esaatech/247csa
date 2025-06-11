from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from email_utility.models import UserEmailConfiguration

class TeamInvitationEmailService:
    @staticmethod
    def send_invitation_email(invitation):
        """
        Send a team invitation email using the system's email configuration
        """
        # Get the sender's email configuration (preferably primary)
        sender_config = UserEmailConfiguration.get_primary_for_user(invitation.invited_by)
        if not sender_config:
            raise ValueError("No email configuration found for the inviting user")

        # Generate the invitation acceptance URL
        accept_url = reverse('team:accept_invitation', kwargs={'invitation_id': invitation.id})
        decline_url = reverse('team:decline_invitation', kwargs={'invitation_id': invitation.id})
        
        # Prepare the email context
        context = {
            'team': invitation.team,
            'inviter': invitation.invited_by,
            'accept_url': accept_url,
            'decline_url': decline_url,
            'expires_at': invitation.expires_at,
        }
        
        # Render the email content from templates
        subject = render_to_string('team/emails/invitation_subject.txt', context).strip()
        body = render_to_string('team/emails/invitation_body.html', context)
        
        # Send the email using the configured provider
        provider = sender_config.get_provider()
        provider.send_message(
            to=invitation.email,
            subject=subject,
            body=body
        )

    @staticmethod
    def send_invitation_cancelled_email(invitation):
        """
        Send notification when invitation is cancelled
        """
        sender_config = UserEmailConfiguration.get_primary_for_user(invitation.invited_by)
        if not sender_config:
            return
            
        context = {
            'team': invitation.team,
            'inviter': invitation.invited_by,
        }
        
        subject = render_to_string('team/emails/invitation_cancelled_subject.txt', context).strip()
        body = render_to_string('team/emails/invitation_cancelled_body.html', context)
        
        provider = sender_config.get_provider()
        provider.send_message(
            to=invitation.email,
            subject=subject,
            body=body
        ) 