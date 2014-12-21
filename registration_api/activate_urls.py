from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^(?P<activation_key>\w+)/$',
        'registration_api.views.activate',
        name='registration_activate'),
)
