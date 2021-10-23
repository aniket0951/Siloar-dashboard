from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from testapp.sailor_modules.DriverRegistrationRequestModel import driver_registartion_request, \
    restaurant_registration_request
from testapp.serilizers.sailor_serlizers import DriverRegistrationRequestSerializer, \
    RestaurantRegistrationRequestSerializer
from django.contrib import messages


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
    new_request = driver_registartion_request.objects.all()
    serializers = DriverRegistrationRequestSerializer(new_request, many=True)
    countRe = driver_registartion_request.objects.all().count()
    # return render(request, 'DriverReq.html', {'data': serializers.data})

    p = Paginator(serializers.data, 5)                
    page_num = request.GET.get('page')

    try:
        page_obj = p.get_page(page_num)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    context = {'serializers.data': page_obj, 'data':serializers.data}




    return render(request,'DriverReq.html', context)
   