from django.db import models


# ------- driver registration request module ---------
class driver_registartion_request(models.Model):
    full_name = models.CharField(max_length=40, null=True, blank=True)
    email = models.CharField(max_length=120, null=True, blank=True)
    contact_number = models.CharField(max_length=10, null=True, blank=True)
    date_of_birth = models.CharField(max_length=30, null=True, blank=True)
    house_number = models.CharField(max_length=100, null=True, blank=True)
    building_name = models.CharField(max_length=300, null=True, blank=True)
    street_name = models.CharField(max_length=300, null=True, blank=True)
    landmark = models.CharField(max_length=300, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    district = models.CharField(max_length=200, null=True, blank=True)
    pin_code = models.CharField(max_length=100, null=True, blank=True)
    aadhaar_front_photo = models.CharField(max_length=1010, null=True, blank=True)
    aadhaar_back_photo = models.CharField(max_length=1010, null=True, blank=True)
    licence_front_photo = models.CharField(max_length=1010, null=True, blank=True)
    licence_back_photo = models.CharField(max_length=1010, null=True, blank=True)
    passport_size_photo = models.CharField(max_length=1100, null=True, blank=True)
    vehicle_RTO_registration_number = models.CharField(max_length=100, null=True, blank=True)
    vehicle_rc_number = models.CharField(max_length=400, null=True, blank=True)
    vehicle_colour = models.CharField(max_length=100, null=True, blank=True)
    vehicle_make_year = models.CharField(max_length=100, null=True, blank=True)
    vehicle_type = models.CharField(max_length=100, null=True, blank=True)
    global_vehicle_id = models.IntegerField(null=True, blank=True)
    vehicle_front_photo = models.CharField(max_length=600, null=True, blank=True)
    vehicle_back_photo = models.CharField(max_length=600, null=True, blank=True)
    vehicle_left_photo = models.CharField(max_length=600, null=True, blank=True)
    vehicle_right_photo = models.CharField(max_length=600, null=True, blank=True)
    request_token = models.CharField(max_length=1100, null=True, blank=True)
    status = models.CharField(max_length=110, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vehicle_brand = models.CharField(max_length=1200, null=True, blank=True)
    vehicle_model = models.CharField(max_length=1200, null=True, blank=True)
    account_verification_status = models.CharField(max_length=450, null=True, blank=True)
    pan_card = models.CharField(max_length=445, null=True, blank=True)
    vehicle_rc = models.CharField(max_length=445, null=True, blank=True)
    vehicle_insurance = models.CharField(max_length=445, null=True, blank=True)
    vehicle_permit = models.CharField(max_length=445, null=True, blank=True)
    is_deliver_partner = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        db_table = "driver_registartion_request"


# -------- restaurant registration request --------------------
class restaurant_registration_request(models.Model):
    owner_name = models.CharField(max_length=240, null=True, blank=True)
    owner_contact_no = models.CharField(max_length=240, null=True, blank=True)
    owner_email = models.CharField(max_length=240, null=True, blank=True)
    owner_current_address = models.CharField(max_length=350, null=True, blank=True)
    owner_permanent_address = models.CharField(max_length=350, null=True, blank=True)
    restaurant_name = models.CharField(max_length=210, null=True, blank=True)
    restaurant_email = models.CharField(max_length=210, null=True, blank=True)
    restaurant_contact_no = models.CharField(max_length=40, null=True, blank=True)
    restaurant_opening_time = models.CharField(max_length=120, null=True, blank=True)
    restaurant_close_time = models.CharField(max_length=120, null=True, blank=True)
    restaurant_website = models.CharField(max_length=240, null=True, blank=True)
    restaurant_establishment_year = models.CharField(max_length=40, null=True, blank=True)
    restaurant_cuisines_type = models.CharField(max_length=120, null=True, blank=True)
    restaurant_indoor_photo = models.CharField(max_length=340, null=True, blank=True)
    restaurant_outdoor_photo = models.CharField(max_length=340, null=True, blank=True)
    restaurant_licence_photo = models.CharField(max_length=340, null=True, blank=True)
    request_token = models.CharField(max_length=210, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=11, null=True, blank=True)
    account_verification_status = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        db_table = 'restaurant_registration_request'


# ------- driver verification of provided request ---------
class driver_verification(models.Model):
    id = models.IntegerField(primary_key = True)
    request_token = models.TextField(null=True, blank=True)
    is_basic_verified = models.IntegerField(null=True, blank=True)
    is_address_verified = models.IntegerField(null=True, blank=True)
    is_kyc_verified = models.IntegerField(null=True, blank=True)
    is_vehicle_info_verified = models.IntegerField(null=True, blank=True)
    is_vehicle_document_verified = models.IntegerField(null=True, blank=True)
    is_account_verified = models.IntegerField(null=True, blank=True)
    is_account_rejected = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.request_token

    class Meta:
        managed = True
        db_table = 'driver_verification'


# ------- driver document verification -----------------------
class driver_document_verification(models.Model):
    id = models.IntegerField(primary_key = True)
    request_token = models.TextField(null=True, blank=True)
    is_aadhar_front = models.TextField(null=True, blank=True)
    is_aadhar_back = models.TextField(null=True, blank=True)
    is_licence_front = models.TextField(null=True, blank=True)
    is_licence_back = models.TextField(null=True, blank=True)
    is_passport_size = models.TextField(null=True, blank=True)
    is_vehicle_front = models.TextField(null=True, blank=True)
    is_vehicle_back = models.TextField(null=True, blank=True)
    is_vehicle_left = models.TextField(null=True, blank=True)
    is_vehicle_right = models.TextField(null=True, blank=True)
    is_vehicle_rc = models.TextField(null=True, blank=True)
    is_vehicle_insurance = models.TextField(null=True, blank=True)
    is_vehicle_permit = models.TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'driver_document_verification'
