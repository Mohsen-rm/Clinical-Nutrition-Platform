from rest_framework import serializers
from .models import Disease, NutritionPlan, WhatsAppMessage


class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = ['id', 'name', 'description', 'dietary_restrictions', 'calorie_adjustment']


class NutritionPlanSerializer(serializers.ModelSerializer):
    diseases = DiseaseSerializer(many=True, read_only=True)
    disease_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = NutritionPlan
        fields = [
            'id', 'name', 'age', 'gender', 'height', 'weight', 'activity_level', 'goal',
            'diseases', 'disease_ids', 'allergies', 'medications',
            'bmr', 'tdee', 'target_calories', 'protein_grams', 'carbs_grams', 'fat_grams',
            'meal_plan', 'notes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['bmr', 'tdee', 'target_calories', 'protein_grams', 'carbs_grams', 'fat_grams']
    
    def create(self, validated_data):
        disease_ids = validated_data.pop('disease_ids', [])
        nutrition_plan = NutritionPlan.objects.create(**validated_data)
        
        if disease_ids:
            diseases = Disease.objects.filter(id__in=disease_ids)
            nutrition_plan.diseases.set(diseases)
            nutrition_plan.apply_disease_adjustments()
        
        return nutrition_plan
    
    def update(self, instance, validated_data):
        disease_ids = validated_data.pop('disease_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if disease_ids is not None:
            diseases = Disease.objects.filter(id__in=disease_ids)
            instance.diseases.set(diseases)
            instance.apply_disease_adjustments()
        
        return instance


class CreateNutritionPlanSerializer(serializers.ModelSerializer):
    disease_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    diseases = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    
    class Meta:
        model = NutritionPlan
        fields = [
            'name', 'age', 'gender', 'height', 'weight', 'activity_level', 'goal',
            'disease_ids', 'diseases', 'allergies', 'medications', 'notes'
        ]
    
    def validate_age(self, value):
        if value < 1 or value > 120:
            raise serializers.ValidationError("Age must be between 1 and 120")
        return value
    
    def validate_height(self, value):
        if value < 50 or value > 300:
            raise serializers.ValidationError("Height must be between 50 and 300 cm")
        return value
    
    def validate_weight(self, value):
        if value < 20 or value > 500:
            raise serializers.ValidationError("Weight must be between 20 and 500 kg")
        return value


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessage
        fields = [
            'id', 'phone_number', 'message_type', 'content',
            'whatsapp_message_id', 'status', 'created_at'
        ]
        read_only_fields = ['whatsapp_message_id', 'status']


class SendWhatsAppMessageSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    message = serializers.CharField(max_length=1000)
    
    def validate_phone_number(self, value):
        # Basic phone number validation
        import re
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Invalid phone number format")
        return value
