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
from django.urls import path
from testapp.views import voilaopen, remove, newtry, driverReq, testfunc, VerifyBasicInfo, VerifyAddressInfo, \
    VerifyKYCDocument, VerifyVehicleInfo, VerifyVehicleDocument, RejectKYCDocument, ReviewDriverDocument
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('voilaopen', voilaopen, name='index'),
                  path('remove', remove, name='remove'),
                  path('newtry', newtry, name="newtry"),

                  # to show driver request
                  path('driverReq', driverReq, name='driverReq'),

                  path('testfunc/<driverid>/', testfunc, name='handlereq'),

                  # verify the basic info
                  path('VerifyBasicInfo/<str:token>/<int:driverid>/', VerifyBasicInfo, name="verifyBasicInfo"),

                  # verify the address information
                  path('VerifyAddressInfo/<str:token>/<int:driverid>/', VerifyAddressInfo, name="verifyAddressInfo"),

                  # verify the kyc information
                  path('VerifyKYCDocument', VerifyKYCDocument, name="verifyKYCDocument"),

                  # verify the vehicle  information
                  path('VerifyVehicleInfo', VerifyVehicleInfo, name="verifyVehicleInfo"),

                  # verify the vehicle  information
                  path('VerifyVehicleDocument', VerifyVehicleDocument, name="verifyVehicleDocument"),

                  # reject the driver kyc document
                  path('RejectKYCDocument/<str:doc_name>/<int:driverid>/', RejectKYCDocument, name="rejectKYCDocument"),

                #   review the driver rejected document
                path('ReviewDriverDocument/<str:token>/<int:driverid>/', ReviewDriverDocument, name='reviewDriverDocument')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
