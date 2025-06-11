from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django_mailbox.models import Mailbox
from django.contrib.auth import get_user_model
from cryptography.fernet import Fernet
from django.utils.module_loading import import_string
import importlib










class UserEmailConfiguration(models.Model):
    """
    Stores email configuration for users.
    
    This model maintains the email provider settings and credentials for each user,
    allowing multiple email configurations per user (e.g., personal and work email).
    """
    
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook'),
        ('yahoo', 'Yahoo Mail'),
        ('other', 'Other IMAP Provider'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='email_configurations'
    )
    provider_type = models.CharField(
        max_length=50,
        choices=PROVIDER_CHOICES,
        help_text="Type of email provider"
    )
    email = models.EmailField(
        help_text="Email address for this configuration"
    )
    credentials = models.JSONField(
        help_text="Encrypted credentials and provider-specific settings"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this email configuration is currently active"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the user's primary email configuration"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    encrypted_password = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ['user', 'email']
        ordering = ['-is_primary', '-created_at']
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configurations"

    def __str__(self):
        return f"{self.user.username} - {self.email} ({self.provider_type})"

    def clean(self):
        """Validate the model instance"""
        super().clean()
        
        # Ensure credentials contain required fields
        if not self.credentials.get('password'):
            raise ValidationError({
                'credentials': 'Password is required in credentials'
            })

        # If setting as primary, ensure no other primary exists for this user
        if self.is_primary:
            existing_primary = UserEmailConfiguration.objects.filter(
                user=self.user,
                is_primary=True
            ).exclude(pk=self.pk).exists()
            
            if existing_primary:
                raise ValidationError(
                    'Another primary email configuration already exists for this user'
                )

    def save(self, *args, **kwargs):
        """Override save to ensure model validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def provider_name(self):
        """Return the human-readable provider name"""
        return dict(self.PROVIDER_CHOICES).get(self.provider_type, self.provider_type)

    def get_provider(self):
        """Get the email provider instance for this configuration"""
        from .services.factory import EmailProviderFactory
        return EmailProviderFactory.get_provider(self.provider_type, self)

    @classmethod
    def get_primary_for_user(cls, user):
        """Get the user's primary email configuration"""
        return cls.objects.filter(
            user=user,
            is_primary=True,
            is_active=True
        ).first()

    def get_password(self):
        """Decrypt and return the password"""
        if not self.encrypted_password:
            return None
            
        try:
            f = Fernet(settings.EMAIL_ENCRYPTION_KEY.encode())
            decrypted_password = f.decrypt(self.encrypted_password.encode())
            return decrypted_password.decode()
        except Exception as e:
            print(f"Error decrypting password: {str(e)}")
            return None
            
    def set_password(self, password):
        """Encrypt and store the password"""
        if not password:
            self.encrypted_password = None
            return
            
        try:
            f = Fernet(settings.EMAIL_ENCRYPTION_KEY.encode())
            self.encrypted_password = f.encrypt(password.encode()).decode()
        except Exception as e:
            print(f"Error encrypting password: {str(e)}")

    
    def get_url_name(self):
        """Returns the URL name for this integration"""
        return 'email_utility:mailbox'
    
    def get_icon_template(self):
        """Returns the path to the icon template"""
        return 'dashboard/icons/email.html'

class MailboxConfiguration(models.Model):
    """
    Links UserEmailConfiguration with django-mailbox and adds additional functionality
    """
    email_config = models.OneToOneField(
        UserEmailConfiguration,
        on_delete=models.CASCADE,
        related_name='mailbox_config'
    )
    mailbox = models.OneToOneField(
        Mailbox,
        on_delete=models.CASCADE,
        related_name='user_config'
    )
    last_sync = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Last time the mailbox was synced"
    )
    sync_enabled = models.BooleanField(
        default=True,
        help_text="Whether automatic syncing is enabled"
    )
    
    # Folder configuration
    custom_folders = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom folder mapping and configuration"
    )
    
    class Meta:
        verbose_name = "Mailbox Configuration"
        verbose_name_plural = "Mailbox Configurations"
        
    def __str__(self):
        return f"Mailbox Config for {self.email_config.email}"
    
    def initialize_mailbox(self):
        """
        Initialize or update the django-mailbox configuration
        based on the email configuration
        """
        if not self.mailbox:
            # Create new mailbox
            self.mailbox = Mailbox.objects.create(
                name=self.email_config.email,
                uri=self._build_uri(),
                active=True
            )
            self.save()
        else:
            # Update existing mailbox
            self.mailbox.uri = self._build_uri()
            self.mailbox.save()
    
    def _build_uri(self):
        """
        Build the mailbox URI based on provider type and credentials
        """
        config = self.email_config
        if config.provider_type == 'gmail':
            return f'imap+ssl://{ config.email }:{ config.get_password() }@imap.gmail.com'
        elif config.provider_type == 'outlook':
            return f'imap+ssl://{ config.email }:{ config.get_password() }@outlook.office365.com'
        # Add more providers as needed
        return None
    
    @property
    def folders(self):
        """
        Get all available folders (default + custom)
        """
        default_folders = {
            'inbox': 'INBOX',
            'sent': 'Sent',
            'drafts': 'Drafts',
            'trash': 'Trash'
        }
        return {**default_folders, **self.custom_folders}

    def add_custom_folder(self, folder_name, imap_folder=None):
        """
        Add a custom folder mapping
        Args:
            folder_name: User-friendly folder name
            imap_folder: Actual IMAP folder name (if different from folder_name)
        """
        if not self.custom_folders:
            self.custom_folders = {}
            
        # If no IMAP folder specified, use sanitized folder name
        if not imap_folder:
            imap_folder = folder_name.replace(' ', '_').upper()
            
        self.custom_folders[folder_name] = imap_folder
        self.save()
        return True
    
    def remove_custom_folder(self, folder_name):
        """
        Remove a custom folder mapping
        """
        if folder_name in self.custom_folders:
            del self.custom_folders[folder_name]
            self.save()
            return True
        return False
    
    def rename_folder(self, old_name, new_name):
        """
        Rename a custom folder
        """
        if old_name in self.custom_folders:
            imap_folder = self.custom_folders[old_name]
            del self.custom_folders[old_name]
            self.custom_folders[new_name] = imap_folder
            self.save()
            return True
        return False
    
    def get_folder_path(self, folder_name):
        """
        Get the IMAP folder path for a given folder name
        """
        if folder_name in self.folders:
            return self.folders[folder_name]
        return None
    
    def sync_folders(self):
        """
        Sync folders with the IMAP server
        Returns list of available folders
        """
        if not self.mailbox:
            return []
            
        try:
            # Get connection from django-mailbox
            connection = self.mailbox.get_connection()
            
            # List all folders on the server
            server_folders = connection.list()[1]
            available_folders = []
            
            for folder_info in server_folders:
                # Parse folder name from IMAP response
                folder_name = folder_info.decode().split('"/"')[-1].strip('"')
                available_folders.append(folder_name)
                
            # Update custom folders if they exist on server
            self.custom_folders = {
                name: path for name, path in self.custom_folders.items()
                if path in available_folders
            }
            self.save()
            
            return available_folders
            
        except Exception as e:
            print(f"Error syncing folders: {str(e)}")
            return []
    
    def is_valid_folder(self, folder_name):
        """
        Check if a folder exists and is accessible
        """
        return folder_name in self.folders
    
    def get_folder_message_count(self, folder_name):
        """
        Get the number of messages in a folder
        """
        if not self.mailbox or not self.is_valid_folder(folder_name):
            return 0
            
        try:
            connection = self.mailbox.get_connection()
            connection.select(self.get_folder_path(folder_name))
            return len(connection.search(None, 'ALL')[1][0].split())
        except Exception as e:
            print(f"Error getting message count: {str(e)}")
            return 0
        





