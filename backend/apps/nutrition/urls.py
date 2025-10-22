from django.urls import path
from .views import (
    DiseasesView, NutritionPlansView, NutritionPlanDetailView,
    WhatsAppMessagesView, calculate_calories, nutrition_demo
)

urlpatterns = [
    path('diseases/', DiseasesView.as_view(), name='diseases'),
    path('plans/', NutritionPlansView.as_view(), name='nutrition_plans'),
    path('plans/<int:plan_id>/', NutritionPlanDetailView.as_view(), name='nutrition_plan_detail'),
    path('calculate/', calculate_calories, name='calculate_calories'),
    path('whatsapp/', WhatsAppMessagesView.as_view(), name='whatsapp_messages'),
    path('demo/', nutrition_demo, name='nutrition_demo'),
]
