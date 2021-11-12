from django.shortcuts import render, redirect
from restaurant.models import restaurant_registration_request, restaurant_document_verification, restaurant_verification
from restaurant.Serilizer import RestaurantRegistrationRequestSerializer,RestaurantVerificationSerilizer,RestaurantDocumentVerificationSerilizer
from django.http import JsonResponse
import requests
import json
from django.contrib import messages
import numpy


# Create your views here.
def ShowRestaurantReq(request):

    # new requestes
    data = restaurant_registration_request.objects.filter(status=3, account_verification_status=0)
    serilizer = RestaurantRegistrationRequestSerializer(data, many=True)

    # in-progress requests
    in_pro_req = restaurant_registration_request.objects.filter(account_verification_status=2)
    in_pro_serilizer = RestaurantRegistrationRequestSerializer(in_pro_req, many=True)

    # verified requests
    verified_req = restaurant_registration_request.objects.filter(account_verification_status=1)
    verified_serilizer = RestaurantRegistrationRequestSerializer(verified_req, many=True)

    # rejected requests
    reject_req = restaurant_registration_request.objects.filter(account_verification_status=3)
    reject_serilizer = RestaurantRegistrationRequestSerializer(reject_req, many=True)

    context={'new_req':serilizer.data, 'in_progress_req':in_pro_serilizer.data,
             'verified_req':verified_serilizer.data, 'reject_req':reject_serilizer.data}

    return render(request, 'restaurant_req.html', context)


# -- handle restaurant req --
def HandleRestaurantReq(request, res_id):

    handlereq = restaurant_registration_request.objects.filter(id=res_id)
    handlereq_serilizer = RestaurantRegistrationRequestSerializer(handlereq,many=True)

    token = handlereq_serilizer.data[0]["request_token"]
    
    url = f"http://3.7.18.55/api/getRestaurantProfilePic?request_token={token}"

    r = requests.get(url)
    result = json.loads(r.text)

    verify_data = restaurant_verification.objects.filter(request_token=token)
    verify_serializer = RestaurantVerificationSerilizer(verify_data, many=True)

    doc_verify_data = restaurant_document_verification.objects.filter(request_token=token)
    doc_verify_serilizer = RestaurantDocumentVerificationSerilizer(doc_verify_data, many=True)
    

    for i in result:
        finaldata = i

    context = {'handle_req_data':handlereq_serilizer.data, 'restuarnt_doc':finaldata,
               'info_verify_data':verify_serializer.data, 'doc_verify_data':doc_verify_serilizer.data,
               'res_id':res_id}
    return render(request, 'handleres_req.html', context) 

# --- verify owner details ---
def VerifyOwnerDetails(request, res_id):
    req_data = restaurant_registration_request.objects.filter(id=res_id)
    req_serilizer = RestaurantRegistrationRequestSerializer(req_data, many=True)

    token = req_serilizer.data[0]["request_token"]

    if restaurant_verification.objects.filter(request_token=token).exists():
        up_verify_state = restaurant_verification.objects.filter(request_token=token).update(is_owner_verified=1)
        update_req_state = restaurant_registration_request.objects.filter(request_token=token).update(account_verification_status=2)

        if up_verify_state and update_req_state:
            messages.success(request, "Owner Details Verification Successfully...")
            return redirect('handleRestaurantReq', res_id)
        else:
            messages.error(request, "Failed To Verify The Owner Details, Please try again..")
            return redirect('handleRestaurantReq', res_id)      

    else:
        add_new_verify = restaurant_verification.objects.create(request_token=token, is_owner_verified=1)

        updata_req_state = restaurant_registration_request.objects.filter(request_token=token).update(account_verification_status=2)

        if add_new_verify and updata_req_state:
            messages.success(request, "Owner Details Verification Successfully...")
            return redirect('handleRestaurantReq', res_id)
        else:
            messages.error(request, "Failed To Verify The Owner Details, Please try again..")
            return redirect('handleRestaurantReq', res_id)       
    

# --- verify restaurant details ---
def VerifyRestaurantDetails(request, res_id):
    req_data = restaurant_registration_request.objects.filter(id=res_id)
    req_serilizer = RestaurantRegistrationRequestSerializer(req_data, many=True)

    token = req_serilizer.data[0]["request_token"]

    if restaurant_verification.objects.filter(request_token=token).exists():
        up_verify_state = restaurant_verification.objects.filter(request_token=token).update(is_restaurant_details_verified=1)

        if up_verify_state:
            messages.success(request, "Restaurant Details Verification Successfully...")
            return redirect('handleRestaurantReq', res_id)
        else:
            messages.error(request, "Failed To Verify The Restaurant Details, Please try again..")
            return redirect('handleRestaurantReq', res_id) 
    else:
        messages.error(request, "Owner Details Not Verifyed. Please Verify Owner Details")
        return redirect('handleRestaurantReq', res_id)    

# --- verify restaurant documents ---
def VerifyRestaurantDocuments(request, doc_name, res_id):
    req_data = restaurant_registration_request.objects.filter(id=res_id)
    req_serilizer = RestaurantRegistrationRequestSerializer(req_data, many=True)

    token = req_serilizer.data[0]["request_token"]

    if restaurant_verification.objects.filter(request_token=token).exists():
        
        if restaurant_document_verification.objects.filter(request_token=token).exists():
            return UpdateResDocState(request, doc_name, token, res_id) 
        else:
            return CreateResDocState(request, doc_name, token, res_id)
    else:
        messages.error(request, "Owner Details Not Verifyed. Please Verify Owner Details")
        return redirect('handleRestaurantReq', res_id)    
     
# -- create restaurant document verification state --
def CreateResDocState(request, doc_name, token, res_id):

    if doc_name == "restaurant_indoor_photo":
        add_new_verify = restaurant_document_verification.objects.create(request_token=token, is_restaurant_indoor=1)
        if add_new_verify:
            return SendSuccessMessage(request, "Restaurant Indoor Image", res_id)
        else:
            return SendErrorMessage(request,res_id)
    elif doc_name == "restaurant_outdoor_photo":
        add_new_verify = restaurant_document_verification.objects.create(request_token=token, is_restaurant_outdoor=1)
        if add_new_verify:
            return SendSuccessMessage(request, "Restaurant Outdoor Image", res_id)
        else:
            return SendErrorMessage(request,res_id)
    elif doc_name == "restaurant_licence_photo":
        add_new_verify = restaurant_document_verification.objects.create(request_token=token, is_restaurant_liecence=1)
        if add_new_verify:
            return SendSuccessMessage(request, "Restaurant Liecence Image", res_id)
        else:
            return SendErrorMessage(request,res_id)
    else:
        messages.error(request, "Invalid Document Found Please Try Again..")
        return redirect('handleRestaurantReq', res_id)

# --- update restaurant document verification state --
def UpdateResDocState(request, doc_name, token, res_id):
    if doc_name == "restaurant_indoor_photo":
        add_new_verify = restaurant_document_verification.objects.filter(request_token=token).update(is_restaurant_indoor=1)
        if add_new_verify:
            return SendSuccessMessage(request, "Restaurant Indoor Image", res_id)
        else:
            return SendErrorMessage(request,res_id)
    elif doc_name == "restaurant_outdoor_photo":
        add_new_verify = restaurant_document_verification.objects.filter(request_token=token).update(is_restaurant_outdoor=1)
        if add_new_verify:
            return SendSuccessMessage(request, "Restaurant Outdoor Image", res_id)
        else:
            return SendErrorMessage(request,res_id)
    elif doc_name == "restaurant_licence_photo":
        add_new_verify = restaurant_document_verification.objects.filter(request_token=token).update(is_restaurant_liecence=1)
        
        old_doc_state = restaurant_document_verification.objects.filter(request_token=token)
        old_doc_serilizer = RestaurantDocumentVerificationSerilizer(old_doc_state, many=True)

        data_list = []
        for i in old_doc_serilizer.data:
            data_list.append(i["is_restaurant_indoor"])
            data_list.append(i["is_restaurant_outdoor"])
            data_list.append(i["is_restaurant_liecence"])

        unique_data = (numpy.unique(data_list))

        if '2' in unique_data:print("Two is present")
        else: restaurant_verification.objects.filter(request_token=token).update(is_restaurant_document_verified=1)

        verify_state = restaurant_verification.objects.filter(request_token=token)
        verify_serializer = RestaurantVerificationSerilizer(verify_state, many=True)

        new_data_list = []
        for i in verify_serializer.data:
            new_data_list.append(i["is_owner_verified"])
            new_data_list.append(i["is_restaurant_details_verified"])
            new_data_list.append(i["is_restaurant_document_verified"])

        new_unique_data = numpy.unique(new_data_list)

        if '2' in new_data_list:print("Verifivation Pending..")
        else: restaurant_registration_request.objects.filter(request_token=token).update(account_verification_status=1)


        if add_new_verify:
            return SendSuccessMessage(request, "Restaurant Liecence Image", res_id)
        else:
            return SendErrorMessage(request,res_id)
    else:
        messages.error(request, "Invalid Document Found Please Try Again..")
        return redirect('handleRestaurantReq', res_id)

# --- reject owner details ---
def RejectOwnerDetails(request, res_id):
    req_data = restaurant_registration_request.objects.filter(id=res_id)
    req_serilizer = RestaurantRegistrationRequestSerializer(req_data, many=True)

    token = req_serilizer.data[0]["request_token"]

    if restaurant_verification.objects.filter(request_token=token).exists():
        result = restaurant_verification.objects.filter(request_token=token).update(is_owner_verified=2)

        rm_req_data = restaurant_registration_request.objects.filter(request_token=token).update(owner_name=None, owner_contact_no=None,
                                                                                                 owner_email=None, owner_current_address=None,
                                                                                                 owner_permanent_address=None, status=1, 
                                                                                                 account_verification_status=3)
        if result and rm_req_data:
            return DocumentRejSuccess(request, res_id, "Owner Details Rejected Successfully")
        else:
            return DocumentRejError(request, res_id, "Failed To Reject Owner Details, Please Try Again..") 
    
    else:

        result = restaurant_verification.objects.create(request_token=token, is_owner_verified=2)

        rm_req_data = restaurant_registration_request.objects.filter(request_token=token).update(owner_name=None, owner_contact_no=None,
                                                                                                 owner_email=None, owner_current_address=None,
                                                                                                 owner_permanent_address=None, status=1, 
                                                                                                 account_verification_status=3)
        if result and rm_req_data:
            return DocumentRejSuccess(request, res_id, "Owner Details Rejected Successfully")
        else:
            return DocumentRejError(request, res_id, "Failed To Reject Owner Details, Please Try Again..")                                                                                            

# -- review rejected document ---
def ReviewOwnerDetails(request, token):
    if restaurant_verification.objects.filter(request_token=token, is_owner_verified=2).exists():
        owner_details = restaurant_registration_request.objects.filter(request_token=token)
        serilizer = RestaurantRegistrationRequestSerializer(owner_details,many=True)

        if bool(serilizer.data[0]["owner_name"]):
            context={'owner_details':serilizer.data}
            return render(request, 'review_res_req.html',context)
        else:
            return ReviewRestaurantDetails(request, token)
    else:
        return ReviewRestaurantDetails(request, token)    

# --- review restaurant details --
def ReviewRestaurantDetails(request, token):
    if restaurant_verification.objects(request_token=token, is_restaurant_details_verified=2).exists():
        messages.error(request, "New Document Not Uploaded By User. Please Check Again...")
        return render(request, 'review_res_req.html')  
    else:
        messages.error(request, "New Document Not Uploaded By User. Please Check Again...")
        return render(request, 'review_res_req.html')     


# --- return a message with validations ---
def SendSuccessMessage(request, doc_name, res_id):
    messages.success(request, f"{doc_name} Verification Successfully..")
    return redirect('handleRestaurantReq', res_id)

# --- return a error message with validations ---
def SendErrorMessage(request, res_id):
    messages.error(request, "Failed To Verify The Document..")
    return redirect('handleRestaurantReq', res_id)    

# ---- return a document rejection success message --
def DocumentRejSuccess(request, res_id, msg):
    messages.success(request, msg)
    return redirect('handleRestaurantReq', res_id)

# --- return a document rejection failed message ---
def DocumentRejError(request, res_id, msg):
    messages.error(request, msg)
    return redirect('handleRestaurantReq', res_id)        