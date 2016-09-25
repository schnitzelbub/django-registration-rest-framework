from django.conf.urls import url
from registration_api.views import register

urlpatterns = [
    url(r'^$',
        register,
        name='registration_api_register'),
]
