from rest_framework import serializers
from restaurant.models import restaurant_registration_request, restaurant_verification, restaurant_document_verification

# --- Restaurant registration request serializers ---
class RestaurantRegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = restaurant_registration_request
        fields = '__all__'


# ----- restaurant verification serilizer -----
class RestaurantVerificationSerilizer(serializers.ModelSerializer):
    class Meta:
        model = restaurant_verification
        fields = '__all__'


# ---- restuarnt document verification ---- 
class RestaurantDocumentVerificationSerilizer(serializers.ModelSerializer):
    class Meta:
        model = restaurant_document_verification
        fields = '__all__'