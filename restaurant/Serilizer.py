from rest_framework import serializers
from restaurant.models import restaurant_registration_request

# --- Restaurant registration request serializers ---
class RestaurantRegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = restaurant_registration_request
        fields = '__all__'