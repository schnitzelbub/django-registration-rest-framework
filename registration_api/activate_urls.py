from django.conf.urls import url
from registration_api.views import activate

urlpatterns = [
    url(r'^(?P<activation_key>\w+)/$',
        activate,
        name='registration_activate'),
]
