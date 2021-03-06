from rest_framework import serializers
from testapp.sailor_modules.DriverRegistrationRequestModel import driver_registartion_request, \
    restaurant_registration_request


# ----- driver registration request serializers -----
class DriverRegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = driver_registartion_request
        fields = '__all__'


# ------ restaurant registration request serializers -------
class RestaurantRegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = restaurant_registration_request
        fields = '__all__'
