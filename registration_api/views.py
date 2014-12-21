from django.conf import settings
from django.http import HttpResponseRedirect


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

import utils
from serializers import UserSerializer


VALID_USER_FIELDS = utils.get_valid_user_fields()


@api_view(['POST'])
@permission_classes((AllowAny, ))
def register(request):
    serialized = {}
    user_data = {}
    if request.META['CONTENT_TYPE'].startswith('application/json'):
        serialized = UserSerializer(data=request.DATA)
        if serialized.is_valid():
            user_data = request.DATA
    elif request.META['CONTENT_TYPE'].startswith('application/x-www-form-urlencoded'):
        serialized = UserSerializer(data=request.POST)
        if serialized.is_valid():
            user_data = utils.get_user_data(request.POST)

    print user_data
    if user_data:
        create_user_data = {}
        for mapping in settings.REGISTRATION_API_USER_DATA_MAPPING:
             create_user_data[mapping] = user_data.get(mapping, '')
        utils.create_inactive_user(**create_user_data)
        return Response(utils.USER_CREATED_RESPONSE_DATA,
                        status=status.HTTP_201_CREATED)
    else:
        error = ''
        if isinstance(serialized, UserSerializer):
            error = serialized._errors
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


def activate(request, activation_key=None):
    """
    Given an an activation key, look up and activate the user
    account corresponding to that key (if possible).

    """
    utils.activate_user(activation_key)
    # if not activated
    success_url = utils.get_settings('REGISTRATION_API_ACTIVATION_SUCCESS_URL')
    if success_url is not None:
        return HttpResponseRedirect(success_url)
