"""testproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from restaurant.views import ShowRestaurantReq, HandleRestaurantReq, VerifyOwnerDetails, VerifyRestaurantDetails, \
                             VerifyRestaurantDocuments, RejectOwnerDetails, ReviewOwnerDetails 
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path('admin/', admin.site.urls),

                  # -- to show restaurant request -
                  path('ShowRestaurantReq', ShowRestaurantReq, name="showRestaurantReq"),

                  # -- handle restaurant request -- 
                  path('HandleRestaurantReq/<int:res_id>/', HandleRestaurantReq, name="handleRestaurantReq"),

                  # --- verify owner details ---
                  path('VerifyOwnerDetails/<int:res_id>/', VerifyOwnerDetails, name='verifyOwnerDetails'),

                  # --- verify restaurant details ---
                  path('VerifyRestaurantDetails/<int:res_id>/', VerifyRestaurantDetails, name='verifyRestaurantDetails'),

                  # --- verify restaurant document details ---
                  path('VerifyRestaurantDocuments/<str:doc_name>/<int:res_id>/', VerifyRestaurantDocuments, name='verifyRestaurantDocuments'),

                  # --- reject owner details ---
                  path('RejectOwnerDetails/<int:res_id>/', RejectOwnerDetails, name="rejectOwnerDetails"),

                  # --- review owner details ---
                  path('ReviewOwnerDetails/<str:token>/', ReviewOwnerDetails, name='reviewOwnerDetails')

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
