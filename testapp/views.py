import json
import requests

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from testapp.sailor_modules.DriverRegistrationRequestModel import driver_registartion_request, \
    restaurant_registration_request, driver_verification
from testapp.serilizers.sailor_serlizers import DriverRegistrationRequestSerializer, \
    RestaurantRegistrationRequestSerializer, DriverVerificationSerializer
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

    if reqParam != 'aniket@gmail.com':
        messages.error(request, 'You are not authorised User Please try again')
        return redirect('index')
    else:
        messages.success(request, "Success")
        return redirect('index')


def newtry(request):
    new_request = driver_registartion_request.objects.all()
    serializers = DriverRegistrationRequestSerializer(new_request, many=True)
    countRe = driver_registartion_request.objects.all().count()

    # --- restaurant_registration_request ----
    restaurant_request = restaurant_registration_request.objects.all()
    restaurant_serializers = RestaurantRegistrationRequestSerializer(restaurant_request, many=True)

    restaurant_count = restaurant_registration_request.objects.all().count()
    total_cust = countRe + restaurant_count

    return render(request, 'progress.html',
                  {'driver_req': str(countRe), "restaurant_req_count": str(restaurant_count), 'data': serializers.data,
                   'total_request': str(total_cust), 'restaurant_req': restaurant_serializers.data})


def driverReq(request):
    new_request = driver_registartion_request.objects.filter(status=5, account_verification_status=0)
    serializers = DriverRegistrationRequestSerializer(new_request, many=True)
    countRe = driver_registartion_request.objects.all().count()

    # inprogress_data = driver_registartion_request.objects.filter(account_verification_status=2)
    # in_serializer = DriverRegistrationRequestSerializer(inprogress_data, many=True)

    # verifyed_data = driver_registartion_request.objects.filter(account_verification_status=1)
    # verify_serializer = DriverRegistrationRequestSerializer(verifyed_data, many=True)

    context = {'data': serializers.data, 'inprogress_data': serializers.data, 'verifyed_data': serializers.data}

    return render(request, 'DriverReq.html', context)


def testfunc(request, driverid):
    driver_info = driver_registartion_request.objects.filter(id=driverid)
    serializers = DriverRegistrationRequestSerializer(driver_info, many=True)
    token = str(serializers.data[0]["request_token"])

    # account_verification = driver_verification.objects.filter(request_token=token)
    # acc_serializer = DriverVerificationSerializer(account_verification, many=True)
    # data_list = []
    # for i in acc_serializer.data:
    #     if i['is_basic_verified'] ==1 :
    #         data_list.append({'is_basic_verifyed': True })
    #     if i['is_address_verified'] ==1 or i['is_address_verified'] is None:
    #         data_list.append({'is_address_verifyed': True })
    #     if i['is_kyc_verified'] == 1 or i['is_kyc_verified'] is None :
    #         data_list.append({'is_kyc_verified': True })
    #     if i['is_vehicle_info_verified'] == 1:
    #         data_list.append({'is_vehicle_info_verified': True })
    #     if i['is_vehicle_document_verified'] == 1 or i['is_vehicle_document_verified'] is None:
    #         data_list.append({'is_vehicle_document_verified': True})
    #     if i['is_account_verified'] == 1 or i['is_account_verified'] is None:
    #         data_list.append({'is_account_verified': True})
    #     else:
    #         print("not a statement")

    url = f"http://3.7.18.55/api/getKYCRequestdInfo?request_token={token}"

    r = requests.get(url)
    result = json.loads(r.text)

    for i in result:
        finaldata = i
    context = {'data': serializers.data,
               'finaldata': finaldata,
               'driverid': driverid
               }
    # print(result)
    return render(request, 'otp_verify.html', context)


def VerifyBasicInfo(request, token, driverid):
    if driver_verification.objects.filter(request_token=token).exists():
        if driver_verification.objects.filter(request_token=token, is_basic_verified=1).exists():
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
            driver_verification.objects.filter(request_token=token).update(is_basic_verified=1)
            messages.error(request, "Basic Information Already Verified")
            return redirect('handlereq', driverid)
        else:
            verification = driver_verification.objects.filter(request_token=token).update(is_basic_verified=1)
            if verification:
                messages.success(request, "Basic Information Successfully Verified.")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Verification Failed, Please try again...")
                return redirect('handlereq', driverid)
    else:
        basic_verification = driver_verification.objects.create(request_token=token, is_basic_verified=1)
        if basic_verification:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
            messages.success(request, "Basic Information Successfully Verified.")
            return redirect('handlereq', driverid)
        else:
            messages.error(request, "Verification Failed, Please try again...")
            return redirect('handlereq', driverid)


def VerifyAddressInfo(request, token, driverid):
    if driver_verification.objects.filter(request_token=token).exists():
        if driver_verification.objects.filter(request_token=token, is_address_verified=1).exists():
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
            messages.error(request, "Address Information Already Verified. Please check next information")
            return redirect('handlereq', driverid)
        else:
            verification = driver_verification.objects.filter(request_token=token).update(is_address_verified=1)
            if verification:
                driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
                messages.success(request, "Address Information Successfully Verified. Please check next information")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Address Verification Failed, Please try again...")
                return redirect('handlereq', driverid)
    else:
        address_verification = driver_verification.objects.create(request_token=token, is_address_verified=1)
        if address_verification:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
            messages.success(request, "Address Information Successfully Verified. Please check next information")
            return redirect('handlereq', driverid)
        else:
            messages.error(request, "Address Verification Failed, Please try again...")
            return redirect('handlereq', driverid)

    return JsonResponse({'token': token, 'driver': driverid})


def VerifyKYCDocument(request):
    return HttpResponse("This is KYC Verification")


def VerifyVehicleInfo(request):
    return HttpResponse("This is Vehicle Info Verification")


def VerifyVehicleDocument(request):
    return HttpResponse("This is Vehicle Document Verification")
