import json
import requests

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from testapp.sailor_modules.DriverRegistrationRequestModel import driver_registartion_request, \
    restaurant_registration_request, driver_verification, driver_document_verification
from testapp.serilizers.sailor_serlizers import DriverRegistrationRequestSerializer, \
    RestaurantRegistrationRequestSerializer, DriverDocumentVerificationSerializer, DriverVerificationSerializer
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

    # --- get in-progress requests -----
    inprogress_data = driver_registartion_request.objects.filter(account_verification_status=2)
    in_serializer = DriverRegistrationRequestSerializer(inprogress_data, many=True)

    # verifyed_data = driver_registartion_request.objects.filter(account_verification_status=1)
    # verify_serializer = DriverRegistrationRequestSerializer(verifyed_data, many=True)

    # ---- get rejected request or document verification failed ---
    rejected_data = driver_registartion_request.objects.filter(account_verification_status=3)
    reject_serial = DriverRegistrationRequestSerializer(rejected_data, many=True)

    context = {'data': serializers.data, 'inprogress_data': in_serializer.data, 'verifyed_data': serializers.data,
               'reject_data': reject_serial.data}

    return render(request, 'DriverReq.html', context)


def testfunc(request, driverid):
    driver_info = driver_registartion_request.objects.filter(id=driverid)
    serializers = DriverRegistrationRequestSerializer(driver_info, many=True)
    token = str(serializers.data[0]["request_token"])

    account_verification = driver_verification.objects.filter(request_token=token)
    acc_serializer = DriverVerificationSerializer(account_verification, many=True)
    data_list = []
    for i in acc_serializer.data:
        if i['is_basic_verified'] == 1:
            data_list.append({'is_basic_verifyed': True})
        if i['is_address_verified'] == 1 or i['is_address_verified'] is not None:
            data_list.append({'is_address_verifyed': True})
        if i['is_kyc_verified'] == 1 or i['is_kyc_verified'] is not None:
            data_list.append({'is_kyc_verified': True})
        if i['is_vehicle_info_verified'] == 1:
            data_list.append({'is_vehicle_info_verified': True})
        if i['is_vehicle_document_verified'] == 1 or i['is_vehicle_document_verified'] is not None:
            data_list.append({'is_vehicle_document_verified': True})
        if i['is_account_verified'] == 1 or i['is_account_verified'] is not None:
            data_list.append({'is_account_verified': True})

    url = f"http://3.7.18.55/api/getKYCRequestdInfo?request_token={token}"

    r = requests.get(url)
    result = json.loads(r.text)

    for i in result:
        finaldata = i
    context = {'data': serializers.data,
               'finaldata': finaldata,
               'driverid': driverid,
               'verification_status': data_list
               }
    # print(result)
    return render(request, 'otp_verify.html', context)


# --- verify the driver basic information ---
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


# --- verify the driver address information --
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


# --- verify the driver kyc information --
def VerifyKYCDocument(request, doc_name, driverid):
    driver_data = driver_registartion_request.objects.filter(id=driverid)
    serailizer = DriverRegistrationRequestSerializer(driver_data, many=True)
    token = serailizer.data[0]["request_token"]
    if driver_verification.objects.filter(request_token=token).exists():
        if doc_name == "aadhar_front_photo":
            update_verification_state = driver_document_verification.objects.filter(request_token=token).update(
                is_aadhar_front=1)
            if update_verification_state:
                messages.success(request, "Aadhaar Front photo verification successfully")
                return redirect('driverReq')
            else:
                messages.error(request, "Verification failed Please try again...")
                return redirect('driverReq')
        elif doc_name == "aadhar_back_photo":
            update_verification_state = driver_document_verification.objects.filter(request_token=token).update(
                is_aadhar_back=1)
            if update_verification_state:
                messages.success(request, "Aadhaar Back photo verification successfully")
                redirect('driverReq')
            else:
                messages.error(request, "Verification failed Please try again...")
                return redirect('driverReq')
        elif doc_name == "licence_front_photo":
            update_verification_state = driver_document_verification.objects.filter(request_token=token).update(
                is_licence_front=1)
            if update_verification_state:
                messages.success(request, "Licence Front photo verification successfully")
                return redirect('driverReq')
            else:
                messages.error(request, "Verification failed Please try again...")
                return redirect('driverReq')
        elif doc_name == "licence_back_photo":
            update_verification_state = driver_document_verification.objects.filter(request_token=token).update(
                is_licence_back=1)
            if update_verification_state:
                messages.success(request, "Licence Back photo verification successfully")
                return redirect('driverReq')
            else:
                messages.error(request, "Verification failed Please try again...")
                return redirect('driverReq')
        elif doc_name == "passport_size_photo":
            update_verification_state = driver_document_verification.objects.filter(request_token=token).update(
                is_passport_size=1)
            check_doc = driver_document_verification.objects.filter(request_token=token, is_aadhar_front=1,
                                                                    is_aadhar_back=1, is_licence_front=1,
                                                                    is_licence_back=1, is_passport_size=1)
            print(check_doc)
            if update_verification_state:
                messages.success(request, "Passport size photo verification successfully")
                return redirect('driverReq')
            else:
                messages.error(request, "Verification failed Please try again...")
                return redirect('driverReq')

    else:
        messages.error(request, "Please verify the old documents ")
        return redirect('driverReq')


# ----- verify the driver vehicle information ---
def VerifyVehicleInfo(request):
    return HttpResponse("This is Vehicle Info Verification")


# ----- verify the driver vehicle Document --
def VerifyVehicleDocument(request):
    return HttpResponse("This is Vehicle Document Verification")


# --- reject kyc document ---
def RejectKYCDocument(request, doc_name, driverid):
    request_token = driver_registartion_request.objects.filter(id=driverid)
    serilizer = DriverRegistrationRequestSerializer(request_token, many=True)
    token = serilizer.data[0]["request_token"]

    if driver_verification.objects.filter(request_token=token).exists():
        driver_verification.objects.filter(request_token=token).update(request_token=token)
    else:
        driver_verification.objects.create(request_token=token)

    if driver_document_verification.objects.filter(request_token=token).exists():
        return updateRejectDocument(request, token, doc_name)
    else:
        return createRejectionDocument(request, token, doc_name)


def updateRejectDocument(request, token, doc_name):
    if doc_name == "aadhar_front_photo":
        update_rej = driver_document_verification.objects.filter(request_token=token).update(is_aadhar_front=2)
        update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=2)
        if update_rej and update_verification_state:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   aadhaar_front_photo=None, status=3)
            messages.success(request, "Document rejected successfully...Please take review in 24 hours")
            return redirect('driverReq')
        else:
            messages.error(request, "Document rejection failed Please try again ...")
            return redirect('driverReq')
    elif doc_name == "aadhar_back_photo":
        update_rej = driver_document_verification.objects.filter(request_token=token).update(is_aadhar_back=2)
        update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=2)
        if update_rej and update_verification_state:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   aadhar_back_photo=None, status=3)
            messages.success(request, "Document rejected successfully...Please take review in 24 hours")
            return redirect('driverReq')
        else:
            messages.error(request, "Document rejection failed Please try again ...")
            return redirect('driverReq')
    elif doc_name == "licence_front_photo":
        update_rej = driver_document_verification.objects.filter(request_token=token).update(is_licence_front=2)
        update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=2)

        if update_rej and update_verification_state:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   licence_front_photo=None, status=3)
            messages.success(request, "Document rejected successfully...Please take review in 24 hours")
            return redirect('driverReq')
        else:
            messages.error(request, "Document rejection failed Please try again ...")
            return redirect('driverReq')
    elif doc_name == "licence_back_photo":
        update_rej = driver_document_verification.objects.filter(request_token=token).update(is_licence_back=2)
        update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=2)
        if update_rej and update_verification_state:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   licence_back_photo=None, status=3)
            messages.success(request, "Document rejected successfully...Please take review in 24 hours")
            return redirect('driverReq')
        else:
            messages.error(request, "Document rejection failed Please try again ...")
            return redirect('driverReq')
    elif doc_name == "passport_size_photo":
        update_rej = driver_document_verification.objects.filter(request_token=token).update(is_passport_size=2)
        update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=2)

        if update_rej and update_verification_state:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   passport_size_photo=None, status=3)
            messages.success(request, "Document rejected successfully...Please take review in 24 hours")
            return redirect('driverReq')
        else:
            messages.error(request, "Document rejection failed Please try again ...")
            return redirect('driverReq')
    else:
        messages.error(request, "Invalid Document to reject please try again..")
        return redirect('driverReq')


def createRejectionDocument(request, token, doc_name):
    if doc_name == "aadhar_front_photo":
        reject_aadhar_f = driver_document_verification.objects.create(request_token=token, is_aadhar_front=2)
        update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=2)

        if reject_aadhar_f and update_verification_state:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   aadhaar_front_photo=None, status=3)
            messages.success(request, "Document rejected successfully...Please take review in 24 hours")
            return redirect('driverReq')
        else:
            messages.error(request, "Document rejection failed....")
            return redirect('driverReq')
    elif doc_name == "aadhar_back_photo":
        reject_aadhar_f = driver_document_verification.objects.create(request_token=token, is_aadhar_back=2)
        update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=2)

        if reject_aadhar_f and update_verification_state:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   aadhar_back_photo=None, status=3)
            messages.success(request, "Document rejected successfully...")
            return redirect('driverReq')
        else:
            messages.error(request, "Document rejection failed....")
            return redirect('driverReq')

    elif doc_name == "licence_front_photo":
        reject_aadhar_f = driver_document_verification.objects.create(request_token=token, is_licence_front=2)
        update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=2)

        if reject_aadhar_f and update_verification_state:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   licence_front_photo=None, status=3)
            messages.success(request, "Document rejected successfully...")
            return redirect('driverReq')
        else:
            messages.error(request, "Document rejection failed....")
            return redirect('driverReq')

    elif doc_name == "licence_back_photo":
        reject_aadhar_f = driver_document_verification.objects.create(request_token=token, is_licence_back=2)
        update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=2)

        if reject_aadhar_f and update_verification_state:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   licence_back_photo=None, status=3)
            messages.success(request, "Document rejected successfully...")
            return redirect('driverReq')
        else:
            messages.error(request, "Document rejection failed....")
            return redirect('driverReq')

    elif doc_name == "passport_size_photo":
        reject_aadhar_f = driver_document_verification.objects.create(request_token=token, is_passport_size=2)
        update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=2)

        if reject_aadhar_f and update_verification_state:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   passport_size_photo=None, status=3)
            messages.success(request, "Document rejected successfully...")
            return redirect('driverReq')
        else:
            messages.error(request, "Document rejection failed....")
            return redirect('driverReq')
    else:
        messages.error(request, "Invalid Document...")
        return redirect('driverReq')


def ReviewDriverDocument(request, token, driverid):
    if driver_document_verification.objects.filter(request_token=token).exists():
        reject_status = driver_document_verification.objects.filter(request_token=token)
        serilizer = DriverDocumentVerificationSerializer(reject_status, many=True)

        registration_data = driver_registartion_request.objects.filter(request_token=token)
        rej_serializer = DriverRegistrationRequestSerializer(registration_data, many=True)

        if serilizer.data[0]["is_aadhar_front"] == "2":
            if bool(rej_serializer.data[0]["aadhaar_front_photo"]):
                dataa = getAllKYCDocByAPI(token)
                context = {
                    'finaldata': dataa[0]['aadhar_front_photo'],
                    'token': token,
                    'tag': "New upload document :  Aadhaar Front Photo "
                }
                return render(request, 'ReviewRejectedDocs.html', context)
            else:
                messages.error(request,
                               "Aadhar front photo is rejected prevoiusly . New document not upload by user to verify insted of rejected document")
                return render(request, 'ReviewRejectedDocs.html')

        elif serilizer.data[0]["is_aadhar_back"] == "2":
            if bool(rej_serializer.data[0]["aadhaar_back_photo"]):
                dataa = getAllKYCDocByAPI(token)
                context = {
                    'finaldata': dataa[0]['aadhar_back_photo'],
                    'token': token,
                    'tag': "New upload document :  Aadhaar Back Photo "
                }
                return render(request, 'ReviewRejectedDocs.html', context)
            else:
                messages.error(request,
                               "Aadhar Back photo is rejected in last verification. New Document not upload by user to verify insted of rejected")
                return render(request, 'ReviewRejectedDocs.html')

        elif serilizer.data[0]["is_licence_front"] == "2":
            if bool(rej_serializer.data[0]['licence_front_photo']):
                dataa = getAllKYCDocByAPI(token)
                context = {
                    'finaldata': dataa[0]['licence_front_photo'],
                    'token': token,
                    'tag': "New upload document :  Licence Front Photo "
                }
                return render(request, 'ReviewRejectedDocs.html', context)
            else:
                messages.error(request,
                               "Licence Front photo is rejected in last verification. New Document not upload by user to verify insted of rejected")
                return render(request, 'ReviewRejectedDocs.html')

        elif serilizer.data[0]["is_licence_back"] == "2":
            if bool(rej_serializer.data[0]["licence_back_photo"]):
                dataa = getAllKYCDocByAPI(token)
                context = {
                    'finaldata': dataa[0]['licence_back_photo'],
                    'token': token,
                    'tag': "New upload document : Licence Back Photo "
                }
                return render(request, 'ReviewRejectedDocs.html', context)
            else:
                messages.error(request,
                               "Licence Back photo is rejected in last verification. New Document not upload by user to verify insted of rejected")
                return render(request, 'ReviewRejectedDocs.html')

        elif serilizer.data[0]["is_passport_size"] == "2":
            if bool(rej_serializer.data[0]["passport_size_photo"]):
                dataa = getAllKYCDocByAPI(token)
                context = {
                    'finaldata': dataa[0]['passport_size_photo'],
                    'token': token,
                    'tag': "New upload document : Passport Size Photo"
                }
                return render(request, 'ReviewRejectedDocs.html', context)
            else:
                messages.error(request,
                               "Passport Size photo is rejected in last verification. New Document not upload by user to verify insted of rejected")
                return render(request, 'ReviewRejectedDocs.html')
        else:
            messages.error(request, "Invalid Document found Please try again...")
            return render(request, 'ReviewRejectedDocs.html')

    else:
        return JsonResponse("Not found ....... ")


def getAllKYCDocByAPI(token):
    url = f"http://3.7.18.55/api/getKYCRequestdInfo?request_token={token}"
    r = requests.get(url)
    result = json.loads(r.text)

    return result


def MoveDocRejFromInProgress(request, token):
    if driver_verification.objects.filter(request_token=token).exists():
        verification_state = driver_verification.objects.filter(request_token=token)
        serializer = DriverVerificationSerializer(verification_state, many=True)

        if serializer.data[0]["is_basic_verified"] == 2:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
        elif serializer.data[0]["is_address_verified"] == 2:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
        elif serializer.data[0]["is_kyc_verified"] == 2:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
        elif serializer.data[0]["is_vehicle_info_verified"] == 2:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
        elif serializer.data[0]["is_vehicle_document_verified"] == 2:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
        else:
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3)
            return redirect('driverReq')

        return redirect('driverReq')
    else:
        return JsonResponse("token is missing", safe=False)
