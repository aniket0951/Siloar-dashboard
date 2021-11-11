from django.db import models

# Create your models here.
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

