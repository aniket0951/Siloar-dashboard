from rest_framework import serializers
from testapp.sailor_modules.DriverRegistrationRequestModel import driver_registartion_request, \
     driver_verification, driver_document_verification


# ----- driver registration request serializers -----
class DriverRegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = driver_registartion_request
        fields = '__all__'





# ------- driver verification serializers -----
class DriverVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = driver_verification
        fields = '__all__'


# ------ driver document verification serializers -----
class DriverDocumentVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = driver_document_verification
        fields = '__all__'
