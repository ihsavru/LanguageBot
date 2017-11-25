from django.conf.urls import include, url
from .views import messengerBotView

urlpatterns = [
    url(r'^21975e0a3c7ab17aa37124158bbda569af363d15eacb576e06/?$', messengerBotView.as_view()),
]