from django.contrib import admin
from .models import Disease, NutritionPlan, WhatsAppMessage


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'calorie_adjustment', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('calorie_adjustment', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(NutritionPlan)
class NutritionPlanAdmin(admin.ModelAdmin):
    list_display = ('patient_email', 'doctor_email', 'goal', 'target_calories', 'is_active', 'created_at')
    list_filter = ('goal', 'activity_level', 'gender', 'is_active', 'created_at')
    search_fields = ('patient__email', 'doctor__email', 'patient__first_name', 'patient__last_name')
    readonly_fields = ('bmr', 'tdee', 'target_calories', 'protein_grams', 'carbs_grams', 'fat_grams', 'created_at', 'updated_at')
    filter_horizontal = ('diseases',)
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'doctor')
        }),
        ('Physical Data', {
            'fields': ('age', 'gender', 'height', 'weight', 'activity_level', 'goal')
        }),
        ('Medical Information', {
            'fields': ('diseases', 'allergies', 'medications')
        }),
        ('Calculated Values', {
            'fields': ('bmr', 'tdee', 'target_calories', 'protein_grams', 'carbs_grams', 'fat_grams'),
            'classes': ('collapse',)
        }),
        ('Plan Details', {
            'fields': ('meal_plan', 'notes', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def patient_email(self, obj):
        return obj.patient.email
    patient_email.short_description = 'Patient'
    
    def doctor_email(self, obj):
        return obj.doctor.email if obj.doctor else 'Self-created'
    doctor_email.short_description = 'Doctor'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'doctor')


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'phone_number', 'message_type', 'status', 'created_at')
    list_filter = ('message_type', 'status', 'created_at')
    search_fields = ('user__email', 'phone_number', 'content')
    readonly_fields = ('whatsapp_message_id', 'created_at')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
