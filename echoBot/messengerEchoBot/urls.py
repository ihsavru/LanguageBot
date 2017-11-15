from django.conf.urls import include, url
from .views import EchoBotView
urlpatterns =[
                url(r'^d0d96e34ed367ec57d8e33a9f6646dcbcb6118d4db32ce82fc/?$', EchoBotView.as_view())
]