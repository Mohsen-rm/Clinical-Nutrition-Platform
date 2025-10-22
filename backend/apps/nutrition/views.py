from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Disease, NutritionPlan, WhatsAppMessage
from .serializers import (
    DiseaseSerializer, NutritionPlanSerializer, CreateNutritionPlanSerializer,
    WhatsAppMessageSerializer, SendWhatsAppMessageSerializer
)


class DiseasesView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get list of all diseases"""
        diseases = Disease.objects.all()
        serializer = DiseaseSerializer(diseases, many=True)
        return Response({
            'diseases': serializer.data
        }, status=status.HTTP_200_OK)


class NutritionPlansView(APIView):
    def get(self, request):
        """Get nutrition plans for the current user"""
        if request.user.is_doctor:
            # Doctors can see all plans they created
            plans = NutritionPlan.objects.filter(doctor=request.user)
        else:
            # Patients can only see their own plans
            plans = NutritionPlan.objects.filter(patient=request.user)
        
        serializer = NutritionPlanSerializer(plans, many=True)
        return Response({
            'nutrition_plans': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create a new nutrition plan"""
        serializer = CreateNutritionPlanSerializer(data=request.data)
        if serializer.is_valid():
            # Set patient and doctor
            patient = request.user
            doctor = None
            
            # If a doctor is creating the plan, they can specify the patient
            if request.user.is_doctor:
                patient_id = request.data.get('patient_id')
                if patient_id:
                    try:
                        from apps.accounts.models import User
                        patient = User.objects.get(id=patient_id, user_type='patient')
                    except User.DoesNotExist:
                        return Response({
                            'error': 'Invalid patient ID'
                        }, status=status.HTTP_400_BAD_REQUEST)
                doctor = request.user
            
            # Remove disease_ids from validated_data before creating the object
            validated_data = serializer.validated_data.copy()
            disease_ids = validated_data.pop('disease_ids', [])
            # Handle frontend sending 'diseases' instead of 'disease_ids'
            if not disease_ids:
                disease_ids = validated_data.pop('diseases', [])
            
            nutrition_plan = NutritionPlan.objects.create(
                patient=patient,
                doctor=doctor,
                **validated_data
            )
            
            # Set diseases if provided and apply adjustments
            if disease_ids:
                diseases = Disease.objects.filter(id__in=disease_ids)
                nutrition_plan.diseases.set(diseases)
                nutrition_plan.apply_disease_adjustments()
            
            return Response({
                'message': 'Nutrition plan created successfully',
                'nutrition_plan': NutritionPlanSerializer(nutrition_plan).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NutritionPlanDetailView(APIView):
    def get(self, request, plan_id):
        """Get specific nutrition plan"""
        plan = get_object_or_404(NutritionPlan, id=plan_id)
        
        # Check permissions
        if not (plan.patient == request.user or plan.doctor == request.user):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = NutritionPlanSerializer(plan)
        return Response({
            'nutrition_plan': serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request, plan_id):
        """Update nutrition plan"""
        plan = get_object_or_404(NutritionPlan, id=plan_id)
        
        # Check permissions (only doctor or patient can update)
        if not (plan.patient == request.user or plan.doctor == request.user):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = NutritionPlanSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Nutrition plan updated successfully',
                'nutrition_plan': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def calculate_calories(request):
    """Calculate calories and macros without saving a plan"""
    serializer = CreateNutritionPlanSerializer(data=request.data)
    if serializer.is_valid():
        # Create temporary plan to calculate values
        temp_plan = NutritionPlan(**serializer.validated_data, patient=request.user)
        temp_plan.bmr = temp_plan.calculate_bmr()
        temp_plan.tdee = temp_plan.calculate_tdee()
        temp_plan.target_calories = temp_plan.calculate_target_calories()
        
        # Apply disease adjustments if provided
        disease_ids = serializer.validated_data.get('disease_ids', [])
        if disease_ids:
            diseases = Disease.objects.filter(id__in=disease_ids)
            disease_adjustment = sum(disease.calorie_adjustment for disease in diseases)
            temp_plan.target_calories += disease_adjustment
        
        # Calculate macros
        temp_plan.protein_grams = (temp_plan.target_calories * 0.25) / 4
        temp_plan.carbs_grams = (temp_plan.target_calories * 0.45) / 4
        temp_plan.fat_grams = (temp_plan.target_calories * 0.30) / 9
        
        return Response({
            'bmr': round(temp_plan.bmr, 2),
            'tdee': round(temp_plan.tdee, 2),
            'target_calories': round(temp_plan.target_calories, 2),
            'protein_grams': round(temp_plan.protein_grams, 2),
            'carbs_grams': round(temp_plan.carbs_grams, 2),
            'fat_grams': round(temp_plan.fat_grams, 2)
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WhatsAppMessagesView(APIView):
    def get(self, request):
        """Get WhatsApp message history"""
        messages = WhatsAppMessage.objects.filter(user=request.user)
        serializer = WhatsAppMessageSerializer(messages, many=True)
        return Response({
            'messages': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Send WhatsApp message (demo implementation)"""
        serializer = SendWhatsAppMessageSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            message_content = serializer.validated_data['message']
            
            # Demo implementation - just save the message
            # In production, integrate with WhatsApp Business API
            whatsapp_message = WhatsAppMessage.objects.create(
                user=request.user,
                phone_number=phone_number,
                message_type='outgoing',
                content=message_content,
                status='sent'
            )
            
            # Demo: Auto-reply with nutrition tip
            auto_reply_content = self._generate_nutrition_tip(request.user)
            WhatsAppMessage.objects.create(
                user=request.user,
                phone_number=phone_number,
                message_type='incoming',
                content=auto_reply_content,
                status='delivered'
            )
            
            return Response({
                'message': 'WhatsApp message sent successfully (demo)',
                'sent_message': WhatsAppMessageSerializer(whatsapp_message).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _generate_nutrition_tip(self, user):
        """Generate a nutrition tip based on user's profile"""
        tips = [
            "💧 Remember to drink at least 8 glasses of water daily!",
            "🥗 Include colorful vegetables in every meal for optimal nutrition.",
            "🏃‍♂️ Combine your nutrition plan with regular physical activity.",
            "😴 Get 7-9 hours of sleep for better metabolism and recovery.",
            "🍎 Choose whole foods over processed options when possible.",
        ]
        
        # Try to get user's latest nutrition plan for personalized tips
        try:
            latest_plan = user.nutrition_plans.filter(is_active=True).first()
            if latest_plan:
                if latest_plan.goal == 'lose':
                    return "🎯 Focus on portion control and increase your protein intake to support your weight loss goal!"
                elif latest_plan.goal == 'gain':
                    return "💪 Add healthy calorie-dense foods like nuts, avocados, and lean proteins to support weight gain!"
                else:
                    return "⚖️ Maintain your current healthy eating patterns and stay consistent with your nutrition plan!"
        except:
            pass
        
        import random
        return random.choice(tips)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def nutrition_demo(request):
    """Demo endpoint showing disease-calorie logic"""
    demo_data = {
        'diseases': [
            {
                'name': 'Diabetes Type 2',
                'calorie_adjustment': -200,
                'description': 'Requires reduced calorie intake and controlled carbohydrates'
            },
            {
                'name': 'Hyperthyroidism',
                'calorie_adjustment': +300,
                'description': 'Increased metabolism requires higher calorie intake'
            },
            {
                'name': 'Hypertension',
                'calorie_adjustment': -100,
                'description': 'Moderate calorie reduction with low sodium diet'
            }
        ],
        'sample_calculation': {
            'base_tdee': 2000,
            'diabetes_adjustment': -200,
            'final_target': 1800,
            'explanation': 'Base TDEE of 2000 calories reduced by 200 for diabetes management'
        },
        'whatsapp_integration': {
            'demo_message': 'Send nutrition reminders and tips via WhatsApp',
            'features': [
                'Daily meal reminders',
                'Hydration alerts',
                'Medication reminders',
                'Progress check-ins'
            ]
        }
    }
    
    return Response(demo_data, status=status.HTTP_200_OK)
