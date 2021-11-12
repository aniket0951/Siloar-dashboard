import json
import requests
import numpy
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from testapp.sailor_modules.DriverRegistrationRequestModel import driver_registartion_request, \
     driver_verification, driver_document_verification
from testapp.serilizers.sailor_serlizers import DriverRegistrationRequestSerializer, \
    DriverDocumentVerificationSerializer, DriverVerificationSerializer
from rest_framework.decorators import api_view
from restaurant.models import restaurant_registration_request
from restaurant.Serilizer import RestaurantRegistrationRequestSerializer

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

    verifyed_data = driver_registartion_request.objects.filter(account_verification_status=1)
    verify_serializer = DriverRegistrationRequestSerializer(verifyed_data, many=True)

    # ---- get rejected request or document verification failed ---
    rejected_data = driver_registartion_request.objects.filter(account_verification_status=3)
    reject_serial = DriverRegistrationRequestSerializer(rejected_data, many=True)

    context = {'data': serializers.data, 'inprogress_data': in_serializer.data, 'verifyed_data': verify_serializer.data,
               'reject_data': reject_serial.data}
    # print(context)           

    return render(request, 'DriverReq.html', context)


def testfunc(request, driverid):
    driver_info = driver_registartion_request.objects.filter(id=driverid)
    serializers = DriverRegistrationRequestSerializer(driver_info, many=True)
    token = str(serializers.data[0]["request_token"])

    # print("Test fun called", token, driverid)

    document_state = driver_document_verification.objects.filter(request_token=token)
    doc_serilizer = DriverDocumentVerificationSerializer(document_state, many=True)

    # print(doc_serilizer.data)

    dv = driver_verification.objects.filter(request_token=token)
    ds = DriverVerificationSerializer(dv, many=True)

    # print("This is ds data",ds.data)

    url = f"http://3.7.18.55/api/getKYCRequestdInfo?request_token={token}"

    r = requests.get(url)
    result = json.loads(r.text)

    for i in result:
        finaldata = i
    context = {'data': serializers.data,
               'finaldata': finaldata,
               'driverid': driverid,
               'doc_state': doc_serilizer.data,
               'reg_process': ds.data
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
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)

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
            driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)

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
        if driver_document_verification.objects.filter(request_token=token).exists():
            if doc_name == "aadhar_front_photo":
                update_verification_state = driver_document_verification.objects.filter(request_token=token).update(
                    is_aadhar_front=1)
                if update_verification_state:
                    messages.success(request, "Aadhaar Front photo verification successfully")
                    return redirect('handlereq', driverid)
                else:
                    messages.error(request, "Verification failed Please try again...")
                    return redirect('handlereq', driverid)
            elif doc_name == "aadhar_back_photo":
                update_verification_state = driver_document_verification.objects.filter(request_token=token).update(
                    is_aadhar_back=1)
                if update_verification_state:
                    messages.success(request, "Aadhaar Back photo verification successfully")
                    return redirect('handlereq', driverid)
                else:
                    messages.error(request, "Verification failed Please try again...")
                    return redirect('handlereq', driverid)
            elif doc_name == "licence_front_photo":
                update_verification_state = driver_document_verification.objects.filter(request_token=token).update(
                    is_licence_front=1)
                if update_verification_state:
                    messages.success(request, "Licence Front photo verification successfully")
                    return redirect('handlereq', driverid)
                else:
                    messages.error(request, "Verification failed Please try again...")
                    return redirect('handlereq', driverid)
            elif doc_name == "licence_back_photo":
                update_verification_state = driver_document_verification.objects.filter(request_token=token).update(
                    is_licence_back=1)
                if update_verification_state:
                    messages.success(request, "Licence Back photo verification successfully")
                    return redirect('handlereq', driverid)
                else:
                    messages.error(request, "Verification failed Please try again...")
                    return redirect('handlereq', driverid)
            elif doc_name == "passport_size_photo":
                update_verification_state = driver_document_verification.objects.filter(request_token=token).update(
                    is_passport_size=1)
                check_doc = driver_document_verification.objects.filter(request_token=token, is_aadhar_front=1,
                                                                        is_aadhar_back=1, is_licence_front=1,
                                                                        is_licence_back=1, is_passport_size=1)
                
                # read verification process to update kyc verification
                is_verification = driver_document_verification.objects.filter(request_token=token)
                is_ver_serilizer = DriverDocumentVerificationSerializer(is_verification, many=True)

                data_list = []
                for i in is_ver_serilizer.data:
                    data_list.append(i['is_aadhar_front'])
                    data_list.append(i['is_aadhar_back'])
                    data_list.append(i['is_licence_front'])
                    data_list.append(i['is_licence_back'])
                    data_list.append(i['is_passport_size'])

                
                unique_data = (numpy.unique(data_list))
            
                if '2' in unique_data:print("Two is present bhai")
                else:update_verification_state = driver_verification.objects.filter(request_token=token).update(is_kyc_verified=1)
  
                if update_verification_state:
                    messages.success(request, "Passport size photo verification successfully")
                    return redirect('handlereq', driverid)
                else:
                    messages.error(request, "Verification failed Please try again...")
                    return redirect('handlereq', driverid)
        else:
            return CreateUserDocumentVeri(request, doc_name, driverid, token)
    else:
        return CreateUserVerification(request, doc_name, driverid, token)


def CreateUserVerification(request, doc_name, driverid, token):
    create_user = driver_verification.objects.create(request_token=token)
    if create_user:
        return VerifyKYCDocument(request, doc_name, driverid)
    else:
        messages.error(request, "Failed to verify this document please try again.")
        return redirect('driverReq')


def CreateUserDocumentVeri(request, doc_name, driverid, token):
    create_doc_verification = driver_document_verification.objects.create(request_token=token)
    if create_doc_verification:
        return VerifyKYCDocument(request, doc_name, driverid)
    else:
        messages.error(request, "Failed to verify this document please try again.")
        return redirect('driverReq')

    # ----- verify the driver vehicle information ---


def VerifyVehicleInfo(request, token, driverid):
    if driver_verification.objects.filter(request_token=token).exists():
        update_vehicle_info = driver_verification.objects.filter(request_token=token).update(is_vehicle_info_verified=1)

        if update_vehicle_info:
            messages.success(request, "Vehicle Information Verified Successfully...")
            return redirect('handlereq', driverid)
        else:
            messages.error(request, "Failed to Verify Vehicle Information, Please try again...")
            return redirect('handlereq', driverid)
    else:

        result = driver_verification.objects.create(request_token=token, is_vehicle_info_verified=1)

        if result:
            messages.success(request, "Vehicle Information Verified Successfully...")
            return redirect('handlereq', driverid)
        else:
            messages.error(request, "Failed to Verify Vehicle Information, Please try again...")
            return redirect('handlereq', driverid)    



# ----- verify the driver vehicle Document --
def VerifyVehicleDocument(request,doc_name, driverid):
    # get token by driver id from request
    data = driver_registartion_request.objects.filter(id=driverid)
    serilizer = DriverRegistrationRequestSerializer(data, many=True)
    token = serilizer.data[0]["request_token"]
    
    if driver_document_verification.objects.filter(request_token=token).exists():
        if doc_name == "vehicle_front":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_front=1)
            if up_verify_state:
                messages.success(request,"Vehicle Front Image Verification Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to verify this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_back":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_back=1)
            if up_verify_state:
                messages.success(request,"Vehicle Back Image Verification Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to verify this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_left":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_left=1)
            if up_verify_state:
                messages.success(request,"Vehicle Left Image Verification Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to verify this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_right":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_right=1)
            if up_verify_state:
                messages.success(request,"Vehicle Right Image Verification Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to verify this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_rc":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_rc=1)
            if up_verify_state:
                messages.success(request,"Vehicle RC Verification Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to verify this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_insurance":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_insurance=1)
            if up_verify_state:
                messages.success(request,"Vehicle Insurance Verification Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to verify this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_permit":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_permit=1)
            
            # read verification process to update kyc verification
            is_verification = driver_document_verification.objects.filter(request_token=token)
            is_ver_serilizer = DriverDocumentVerificationSerializer(is_verification, many=True)

            data_list = []
            for i in is_ver_serilizer.data:
                data_list.append(i['is_vehicle_front'])
                data_list.append(i['is_vehicle_back'])
                data_list.append(i['is_vehicle_left'])
                data_list.append(i['is_vehicle_right'])
                data_list.append(i['is_vehicle_rc'])
                data_list.append(i['is_vehicle_insurance'])
                data_list.append(i['is_vehicle_permit'])

                
            unique_data = (numpy.unique(data_list))
            
            if '2' in unique_data:print("Two is present bhai")
            else:update_verification_state = driver_verification.objects.filter(request_token=token).update(is_vehicle_document_verified=1)

            check_v_state = driver_verification.objects.filter(request_token=token)
            check_serilizer = DriverVerificationSerializer(check_v_state, many=True)

            n_data_list = []
            for i in check_serilizer.data:
                n_data_list.append(i["is_basic_verified"])
                n_data_list.append(i["is_address_verified"])
                n_data_list.append(i["is_kyc_verified"])
                n_data_list.append(i["is_vehicle_info_verified"])
                n_data_list.append(i["is_vehicle_document_verified"])

            
            if 2 in n_data_list:print(n_data_list)
            else:driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=1)
            

            if up_verify_state:
                messages.success(request,"Vehicle Permit Verification Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to verify this document")
                return redirect('handlereq', driverid)
        else:
            return JsonResponse("This is not vehicle front", safe=False)            
    else:
        return JsonResponse("Need to create user", safe=False)    


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

# ---- reject vehicle documents ---
def RejectVehicleDocuments(request, doc_name, driverid):
    req_data = driver_registartion_request.objects.filter(id=driverid)
    serilizer = DriverRegistrationRequestSerializer(req_data, many=True)
    
    token = serilizer.data[0]["request_token"]

    if driver_document_verification.objects.filter(request_token=token).exists():
        if doc_name == "vehicle_front":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_front=2)
            up_doc_state = driver_verification.objects.filter(request_token=token).update(is_vehicle_document_verified=2)
            if up_verify_state and up_doc_state:
                driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   vehicle_front_photo=None, status=4)
                messages.success(request,"Document Rejected Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to Reject this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_back":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_back=2)
            up_doc_state = driver_verification.objects.filter(request_token=token).update(is_vehicle_document_verified=2)
            if up_verify_state and up_doc_state:
                driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   vehicle_back_photo=None, status=4)
                messages.success(request,"Document Rejected Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to Reject this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_left":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_left=2)
            up_doc_state = driver_verification.objects.filter(request_token=token).update(is_vehicle_document_verified=2)
            if up_verify_state and up_doc_state:
                driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   vehicle_left_photo=None, status=4)
                messages.success(request,"Document Rejected Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to Reject this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_right":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_right=2)
            up_doc_state = driver_verification.objects.filter(request_token=token).update(is_vehicle_document_verified=2)
            if up_verify_state and up_doc_state:
                driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   vehicle_right_photo=None, status=4)
                messages.success(request,"Document Rejected Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to Reject this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_rc":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_rc=2)
            up_doc_state = driver_verification.objects.filter(request_token=token).update(is_vehicle_document_verified=2)
            if up_verify_state and up_doc_state:
                driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   vehicle_rc=None, status=4)
                messages.success(request,"Document Rejected Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to Reject this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_insurance":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_insurance=2)
            up_doc_state = driver_verification.objects.filter(request_token=token).update(is_vehicle_document_verified=2)
            if up_verify_state and up_doc_state:
                driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   vehicle_insurance=None, status=4)
                messages.success(request,"Document Rejected Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to Reject this document")
                return redirect('handlereq', driverid)
        elif doc_name == "vehicle_permit":
            up_verify_state = driver_document_verification.objects.filter(request_token=token).update(is_vehicle_permit=2)
            up_doc_state = driver_verification.objects.filter(request_token=token).update(is_vehicle_document_verified=2)
            if up_verify_state and up_doc_state:
                driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=3,
                                                                                   vehicle_permit=None, status=4)
                messages.success(request,"Document Rejected Successfully...")
                return redirect('handlereq', driverid)
            else:
                messages.error(request, "Failed to Reject this document")
                return redirect('handlereq', driverid)
        else:
            messages.error(request, "Failed to reject this document, please try again ...")
            return redirect('handlereq', driverid)
    else:
        messages.error(request, "Failed to reject this document, please try again ...")
        return redirect('handlereq', driverid)

# ----- reject basic info ---
def RejectBasicInfo(request, driverid):
    req_data = driver_registartion_request.objects.filter(id=driverid)
    serilizer = DriverRegistrationRequestSerializer(req_data, many=True)

    token = serilizer.data[0]["request_token"]

    if driver_verification.objects.filter(request_token=token).exists():
        up_verify_state = driver_verification.objects.filter(request_token=token).update(is_basic_verified=2)
        # remove old basic info
        rm_old_info = driver_registartion_request.objects.filter(request_token=token).update(full_name=None,email=None,
                                                                                             contact_number=None,date_of_birth=None, 
                                                                                             status=1, account_verification_status=3)

        if up_verify_state and rm_old_info:
            messages.success(request, "Document Successfully Rejected")
            return redirect('handlereq', driverid)
        else:
            messages.error(request, "Failed to reject the docment please try again..")
            return redirect('handlereq', driverid)    
    else:
        result = driver_verification.objects.create(request_token=token, is_basic_verified=2)
        rm_old_info = driver_registartion_request.objects.filter(request_token=token).update(full_name=None,email=None,
                                                                                             contact_number=None,date_of_birth=None, 
                                                                                             status=1, account_verification_status=3)
        if result:
            messages.success(request, "Document Successfully Rejected")
            return redirect('handlereq', driverid)    
        else:
            messages.error(request, "Failed to reject the docment please try again..")
            return redirect('handlereq', driverid)

# ---- reject address info ----
def RejectAddressInfo(request, driverid):
    req_data = driver_registartion_request.objects.filter(id=driverid)
    req_serilizer = DriverRegistrationRequestSerializer(req_data, many=True)

    token = req_serilizer.data[0]["request_token"]

    up_verify_state = driver_verification.objects.filter(request_token=token).update(is_address_verified=2)

    # remove all address info
    rm_add_info = driver_registartion_request.objects.filter(request_token=token).update(house_number=None, building_name=None,
                                                                                         street_name=None, landmark=None,
                                                                                         state=None, district=None, pin_code=None,
                                                                                         status=2, account_verification_status=3
                                                                                         )

    if up_verify_state and rm_add_info:
        messages.success(request,"Address Information Rejected Successfully..")
        return redirect('handlereq', driverid)
    else:
        messages.error(request, "Failed To Reject Address Information..")
        return redirect('handlereq', driverid)    

# ---- reject vehicle info ---
def RejectVehicleInfo(request, driverid):
    req_data = driver_registartion_request.objects.filter(id=driverid)
    req_serilizer = DriverRegistrationRequestSerializer(req_data, many=True)

    token = req_serilizer.data[0]["request_token"]

    up_verify_state = driver_verification.objects.filter(request_token=token).update(is_vehicle_info_verified=2)

    rm_vehicle_info = driver_registartion_request.objects.filter(request_token=token).update(vehicle_RTO_registration_number=None, vehicle_rc_number=None,
                                                                                     vehicle_colour=None, vehicle_make_year=None,
                                                                                     vehicle_type=None, status=4,
                                                                                     account_verification_status=3)
    if up_verify_state and rm_vehicle_info:
        messages.success(request, "Vehicle Information Rejected Successfully..")
        return redirect('handlereq', driverid)
    else:
        messages.error(request, "Failed to Reject the Vehicle Information,Please try again..")
        return redirect('handlereq', driverid)    

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
                                                                                   aadhaar_back_photo=None, status=3)
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
                                                                                   aadhaar_back_photo=None, status=3)
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
            # check document is not empty
            if bool(rej_serializer.data[0]["aadhaar_front_photo"]):
                # to get new uploaded document
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
                return render(request, 'ReviewRejectedDocs.html', {'token': token})

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
                return render(request, 'ReviewRejectedDocs.html', {'token': token})

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
                return render(request, 'ReviewRejectedDocs.html', {'token': token})

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
                return render(request, 'ReviewRejectedDocs.html', {'token': token})

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
                return render(request, 'ReviewRejectedDocs.html', {'token': token})
        else:
            return ReviewVehicleDocument(request, token, driverid)

    else:
        return JsonResponse("Not found ....... ")

def ReviewVehicleDocument(request, token, driverid):
    rej_docs = driver_document_verification.objects.filter(request_token=token)
    serilizer = DriverDocumentVerificationSerializer(rej_docs, many=True)

    request_docs = driver_registartion_request.objects.filter(request_token=token)
    req_serilizer = DriverRegistrationRequestSerializer(request_docs, many=True)
   
    if serilizer.data[0]["is_vehicle_front"] == "2":
        if bool(req_serilizer.data[0]["vehicle_front_photo"]):
            dataa = getAllKYCDocByAPI(token)
            context = {
                    'finaldata': dataa[0]['vehicle_front_photo'],
                    'token': token,
                    'tag': "New upload document : Vehicle Front Photo"
                }
            return render(request, 'ReviewRejectedDocs.html', context)
        else:
            messages.error(request,"Vehicle Front photo is rejected in last verification. New Document not upload by user to verify insted of rejected")
            return render(request, 'ReviewRejectedDocs.html', {'token': token})
    elif serilizer.data[0]["is_vehicle_back"] == "2":
        if bool(req_serilizer[0]["vehicle_back_photo"]):
            dataa = getAllKYCDocByAPI(token)
            context = {
                    'finaldata': dataa[0]['vehicle_back_photo'],
                    'token': token,
                    'tag': "New upload document : Vehicle Back Photo"
                }
            return render(request, 'ReviewRejectedDocs.html', context)
        else:
            messages.error(request,"Vehicle Back photo is rejected in last verification. New Document not upload by user to verify insted of rejected")
            return render(request, 'ReviewRejectedDocs.html', {'token': token})
    elif serilizer.data[0]["is_vehicle_left"]:
        if bool(req_serilizer.data[0]["vehicle_left_photo"]):
            dataa = getAllKYCDocByAPI(token)
            context = {
                    'finaldata': dataa[0]['vehicle_left_photo'],
                    'token': token,
                    'tag': "New upload document : Vehicle Left Photo"
                }
            return render(request, 'ReviewRejectedDocs.html', context)
        else:
            messages.error(request,"Vehicle Left photo is rejected in last verification. New Document not upload by user to verify insted of rejected")
            return render(request, 'ReviewRejectedDocs.html', {'token': token})
    elif serilizer.data[0]["is_vehicle_right"] == "2":
        if bool(req_serilizer.data[0]["vehicle_right_photo"]):
            dataa = getAllKYCDocByAPI(token)
            context = {
                    'finaldata': dataa[0]['vehicle_right_photo'],
                    'token': token,
                    'tag': "New upload document : Vehicle Right Photo"
                }
            return render(request, 'ReviewRejectedDocs.html', context)
        else:
            messages.error(request,"Vehicle Right photo is rejected in last verification. New Document not upload by user to verify insted of rejected")
            return render(request, 'ReviewRejectedDocs.html', {'token': token})
    elif serilizer.data[0]["is_vehicle_rc"]:
        if bool(req_serilizer.data[0]["vehicle_rc"]):
            dataa = getAllKYCDocByAPI(token)
            context = {
                    'finaldata': dataa[0]['vehicle_rc'],
                    'token': token,
                    'tag': "New upload document : Vehicle RC "
                }
            return render(request, 'ReviewRejectedDocs.html', context)
        else:
            messages.error(request,"Vehicle RC  is rejected in last verification. New Document not upload by user to verify insted of rejected")
            return render(request, 'ReviewRejectedDocs.html', {'token': token})
    elif serilizer.data[0]["is_vehicle_insurance"] == "2":
        if bool(req_serilizer.data[0]["vehicle_insurance"]):
            dataa = getAllKYCDocByAPI(token)
            context = {
                    'finaldata': dataa[0]['vehicle_insurance'],
                    'token': token,
                    'tag': "New upload document : Vehicle Insurance "
                }
            return render(request, 'ReviewRejectedDocs.html', context)
        else:
            messages.error(request,"Vehicle Insurance  is rejected in last verification. New Document not upload by user to verify insted of rejected")
            return render(request, 'ReviewRejectedDocs.html', {'token': token})
    elif serilizer.data[0]["is_vehicle_permit"] == "2":
        if bool(req_serilizer.data[0]["vehicle_permit"]):
            dataa = getAllKYCDocByAPI(token)
            context = {
                    'finaldata': dataa[0]['vehicle_permit'],
                    'token': token,
                    'tag': "New upload document : Vehicle Permit "
                }
            return render(request, 'ReviewRejectedDocs.html', context)
        else:
            messages.error(request,"Vehicle Permit  is rejected in last verification. New Document not upload by user to verify insted of rejected")
            return render(request, 'ReviewRejectedDocs.html', {'token': token})
    else:
        return ReviewAddressDocument(request, token, driverid)
        messages.error(request, "Invalid Document found Please try again...")
        return render(request, 'ReviewRejectedDocs.html', {'token': token})

# review address information
def ReviewAddressDocument(request, token, driverid):
    if driver_verification.objects.filter(request_token=token).exists():
        
        doc_state = driver_verification.objects.filter(request_token=token)
        doc_serilizer = DriverVerificationSerializer(doc_state, many=True)
        
        if doc_serilizer.data[0]["is_address_verified"] == 2:
            
            # get all address information if verification is rejected
            new_req_info = driver_registartion_request.objects.filter(request_token=token)
            new_req_serilizer = DriverRegistrationRequestSerializer(new_req_info, many=True)

            if bool(new_req_serilizer.data[0]["house_number"]):
                context={'address_data':new_req_serilizer.data,'token':token}
                return render(request, 'ReviewRejectedDocs.html', context)
            else:
                return ReviewBasicInfo(request, token, driverid)     
        else:
            return ReviewBasicInfo(request, token, driverid)   
    else:
        return ReviewBasicInfo(request, token, driverid)     

# ---- review Basic Information ---
def ReviewBasicInfo(request, token, driverid):
    if driver_verification.objects.filter(request_token=token).exists():
       
        doc_state = driver_verification.objects.filter(request_token=token)
        doc_serilizer = DriverVerificationSerializer(doc_state, many=True)

        if doc_serilizer.data[0]["is_basic_verified"] == 2:
            new_req_info = driver_registartion_request.objects.filter(request_token=token)
            new_req_serilizer = DriverRegistrationRequestSerializer(new_req_info, many=True)

            if bool(new_req_serilizer.data[0]["full_name"]):
                context={'basic_data':new_req_serilizer.data,'token':token}
                return render(request, 'ReviewRejectedDocs.html', context)
            else:
                return ReviewVehicleInfo(request, token, driverid)
        else:
            return ReviewVehicleInfo(request, token, driverid)       
    else:
        return ReviewVehicleInfo(request, token, driverid)

# review vehicle document
def ReviewVehicleInfo(request, token, driverid):
    if driver_verification.objects.filter(request_token=token).exists():
        doc_state = driver_verification.objects.filter(request_token=token)
        doc_serilizer = DriverVerificationSerializer(doc_state, many=True)

        if doc_serilizer.data[0]["is_vehicle_info_verified"] == 2:
            new_req_info = driver_registartion_request.objects.filter(request_token=token)
            new_req_serilizer = DriverRegistrationRequestSerializer(new_req_info, many=True)

            if bool(new_req_serilizer.data[0]["vehicle_RTO_registration_number"]):
                context={'vehicle_info_data':new_req_serilizer.data,'token':token}
                return render(request, 'ReviewRejectedDocs.html', context)
            else:
                messages.error(request,"Invalid Request please check the documents..")
            return render(request, 'ReviewRejectedDocs.html', {'token': token})    
        else:
            messages.error(request,"Invalid Request please check the documents..")
            return render(request, 'ReviewRejectedDocs.html', {'token': token})   
    else:
        messages.error(request,"Invalid Request please check the documents..")
        return render(request, 'ReviewRejectedDocs.html', {'token': token})      

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
        driver_registartion_request.objects.filter(request_token=token).update(account_verification_status=2)
        return redirect('driverReq')
