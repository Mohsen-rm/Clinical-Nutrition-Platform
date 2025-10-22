from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('doctor', _('Doctor')),
        ('patient', _('Patient')),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='patient',
        help_text=_('Type of user account')
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Phone number for WhatsApp integration')
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether the user has verified their email')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Affiliate fields
    referral_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text=_('Unique referral code for affiliate system')
    )
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='referrals',
        help_text=_('User who referred this user')
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_doctor(self):
        return self.user_type == 'doctor'
    
    @property
    def is_patient(self):
        return self.user_type == 'patient'


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Doctor-specific fields
    license_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Medical license number for doctors')
    )
    specialization = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Medical specialization')
    )
    
    # Patient-specific fields
    height = models.FloatField(
        blank=True,
        null=True,
        help_text=_('Height in cm')
    )
    weight = models.FloatField(
        blank=True,
        null=True,
        help_text=_('Weight in kg')
    )
    medical_conditions = models.TextField(
        blank=True,
        null=True,
        help_text=_('Known medical conditions')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_profile'
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
    
    def __str__(self):
        return f"{self.user.full_name}'s Profile"
