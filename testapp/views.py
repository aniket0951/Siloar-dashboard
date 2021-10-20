from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import http.client
import json
import random
from testapp.serilizers.sailor_serlizers import DriverRegistrationRequestSerializer, \
    RestaurantRegistrationRequestSerializer
from testapp.sailor_modules.DriverRegistrationRequestModel import driver_registartion_request, \
    restaurant_registration_request
from django.http import JsonResponse
from rest_framework.decorators import api_view


# Create your views here.
@csrf_exempt
def voilaopen(request):
    params = {'name': 'voila', 'place': 'Baner'}
    return render(request, 'index.html', params)


@csrf_exempt
def remove(request):
    reqParam = request.GET.get('username', 'default')
    password = request.GET.get('password', 'default')
    print(reqParam, password)
    return render(request, 'firstHT.html')
    mobile_number = reqParam
    otp = random.randint(1111, 9999)
    if mobile_number is not None:
        conn = http.client.HTTPConnection("2factor.in")
        APIKEY = "06fe377d-7a20-11ea-9fa5-0200cd936042"
        payload = ""
        headers = {'content-type': "application/x-www-form-urlencoded"}
        conn.request("GET", f"/API/V1/{APIKEY}/SMS/{mobile_number}/{otp}", payload,
                     headers)
        res = conn.getresponse().read()
        logRes = json.loads(res)
        if logRes is not None:
            sendOtpStatus = logRes["Status"]
            if sendOtpStatus == "Error":
                return HttpResponse("Failed to send otp please try again")
            else:
                return HttpResponse("Otp send successfully")
        else:
            return HttpResponse("Please try again")
    else:
        return HttpResponse("Please enter the mobile number its required to login")

    return HttpResponse(reqParam)


def newtry(request):
    new_request = driver_registartion_request.objects.all()
    serializers = DriverRegistrationRequestSerializer(new_request, many=True)
    countRe = driver_registartion_request.objects.all().count()

    # --- restaurant_registration_request ----
    restaurant_request = restaurant_registration_request.objects.all()
    restaurant_serializers = RestaurantRegistrationRequestSerializer(restaurant_request,  many=True)

    restaurant_count = restaurant_registration_request.objects.all().count()
    total_cust = countRe + restaurant_count

    return render(request, 'progress.html', {'driver_req':str(countRe), "restaurant_req_count":str(restaurant_count), 'data': serializers.data, 'total_request': str(total_cust), 'restaurant_req':restaurant_serializers.data})
