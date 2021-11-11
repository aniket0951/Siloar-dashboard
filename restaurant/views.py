from django.shortcuts import render
from restaurant.models import restaurant_registration_request
from restaurant.Serilizer import RestaurantRegistrationRequestSerializer
from django.http import JsonResponse

# Create your views here.
def ShowRestaurantReq(request):
    data = restaurant_registration_request.objects.all()
    serializer = RestaurantRegistrationRequestSerializer(data, many=True)
    return JsonResponse(serializer.data, safe=False)
    return render(request, 'restaurant_req.html')