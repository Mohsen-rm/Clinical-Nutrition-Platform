from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Disease(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    dietary_restrictions = models.TextField(
        help_text=_('Dietary restrictions and recommendations for this disease')
    )
    calorie_adjustment = models.IntegerField(
        default=0,
        help_text=_('Calorie adjustment (+/-) for this disease')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nutrition_disease'
        verbose_name = _('Disease')
        verbose_name_plural = _('Diseases')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class NutritionPlan(models.Model):
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', _('Sedentary (little or no exercise)')),
        ('light', _('Lightly active (light exercise 1-3 days/week)')),
        ('moderate', _('Moderately active (moderate exercise 3-5 days/week)')),
        ('active', _('Very active (hard exercise 6-7 days/week)')),
        ('extra', _('Extra active (very hard exercise, physical job)')),
    ]
    
    GOAL_CHOICES = [
        ('lose', _('Lose Weight')),
        ('maintain', _('Maintain Weight')),
        ('gain', _('Gain Weight')),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nutrition_plans'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_plans',
        null=True,
        blank=True
    )
    
    # Patient information
    age = models.PositiveIntegerField()
    gender = models.CharField(
        max_length=10,
        choices=[('male', _('Male')), ('female', _('Female'))]
    )
    height = models.FloatField(help_text=_('Height in cm'))
    weight = models.FloatField(help_text=_('Weight in kg'))
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    
    # Medical conditions
    diseases = models.ManyToManyField(Disease, blank=True)
    allergies = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    
    # Calculated values
    bmr = models.FloatField(help_text=_('Basal Metabolic Rate'))
    tdee = models.FloatField(help_text=_('Total Daily Energy Expenditure'))
    target_calories = models.FloatField(help_text=_('Target daily calories'))
    
    # Macronutrient breakdown
    protein_grams = models.FloatField()
    carbs_grams = models.FloatField()
    fat_grams = models.FloatField()
    
    # Plan details
    name = models.CharField(max_length=200, blank=True, null=True, help_text=_('Plan name'))
    meal_plan = models.JSONField(
        default=dict,
        help_text=_('Detailed meal plan with foods and portions')
    )
    notes = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nutrition_plan'
        verbose_name = _('Nutrition Plan')
        verbose_name_plural = _('Nutrition Plans')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Nutrition Plan for {self.patient.full_name}"
    
    def calculate_bmr(self):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if self.gender == 'male':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        return bmr
    
    def calculate_tdee(self):
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'extra': 1.9
        }
        return self.bmr * activity_multipliers.get(self.activity_level, 1.2)
    
    def calculate_target_calories(self):
        """Calculate target calories based on goal"""
        if self.goal == 'lose':
            return self.tdee - 500  # 500 calorie deficit for 1lb/week loss
        elif self.goal == 'gain':
            return self.tdee + 500  # 500 calorie surplus for 1lb/week gain
        else:
            return self.tdee  # Maintenance
    
    def save(self, *args, **kwargs):
        # Calculate metabolic values
        self.bmr = self.calculate_bmr()
        self.tdee = self.calculate_tdee()
        self.target_calories = self.calculate_target_calories()
        
        # Calculate macronutrients (example ratios)
        self.protein_grams = (self.target_calories * 0.25) / 4  # 25% protein
        self.carbs_grams = (self.target_calories * 0.45) / 4   # 45% carbs
        self.fat_grams = (self.target_calories * 0.30) / 9     # 30% fat
        
        # Save the object
        super().save(*args, **kwargs)
    
    def apply_disease_adjustments(self):
        """Apply disease-based calorie adjustments after diseases are set"""
        if self.pk and self.diseases.exists():
            disease_adjustment = sum(disease.calorie_adjustment for disease in self.diseases.all())
            if disease_adjustment != 0:
                self.target_calories = self.calculate_target_calories() + disease_adjustment
                # Recalculate macronutrients with adjusted calories
                self.protein_grams = (self.target_calories * 0.25) / 4
                self.carbs_grams = (self.target_calories * 0.45) / 4
                self.fat_grams = (self.target_calories * 0.30) / 9
                # Save with adjusted values
                self.save(update_fields=['target_calories', 'protein_grams', 'carbs_grams', 'fat_grams'])


class WhatsAppMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('incoming', _('Incoming')),
        ('outgoing', _('Outgoing')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='whatsapp_messages'
    )
    phone_number = models.CharField(max_length=20)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    
    # WhatsApp API specific fields
    whatsapp_message_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('sent', _('Sent')),
            ('delivered', _('Delivered')),
            ('read', _('Read')),
            ('failed', _('Failed')),
        ],
        default='sent'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'nutrition_whatsapp_message'
        verbose_name = _('WhatsApp Message')
        verbose_name_plural = _('WhatsApp Messages')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.message_type} message to/from {self.phone_number}"
