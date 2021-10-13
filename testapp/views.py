from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import http.client
import json
import random

# Create your views here.
@csrf_exempt
def voilaopen(request):
    params = {'name': 'voila', 'place': 'Baner'}
    return render(request, 'index.html', params)


@csrf_exempt
def remove(request):
    reqParam = request.GET.get('username', 'default')
    password = request.GET.get('password','default')
    print(reqParam,password)
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
    return render(request, 'newtry.html')