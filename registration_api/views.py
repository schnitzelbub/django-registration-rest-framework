from django.conf import settings
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import utils
from .serializers import UserSerializer

VALID_USER_FIELDS = utils.get_valid_user_fields()


@api_view(['POST'])
@permission_classes((AllowAny,))
def register(request):
    serialized = {}
    user_data = {}

    if hasattr(settings, 'REGISTRATION_API_USER_SERIALIZER'):
        serializer = utils.get_serializer(settings.REGISTRATION_API_USER_SERIALIZER)
    else:
        serializer = UserSerializer

    if 'CONTENT_TYPE' not in request.META or \
            ('CONTENT_TYPE' in request.META and request.META['CONTENT_TYPE'].startswith('application/json')):
        serialized = UserSerializer(data=request.data)
        if serialized.is_valid():
            user_data = request.data
    elif 'CONTENT_TYPE' in request.META and \
            request.META['CONTENT_TYPE'].startswith('application/x-www-form-urlencoded'):
        serialized = UserSerializer(data=request.POST)  # TODO change to data?
        if serialized.is_valid():
            user_data = utils.get_user_data(request.POST)

    if user_data:
        create_user_data = {}
        for mapping in settings.REGISTRATION_API_USER_DATA_MAPPING:
            create_user_data[mapping] = user_data.get(mapping, '')
        try:
            utils.create_inactive_user(**create_user_data)
        except IntegrityError:
            return Response({'error': 'user failed to create'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(utils.USER_CREATED_RESPONSE_DATA,
                            status=status.HTTP_201_CREATED)
    else:
        error = ''
        if isinstance(serialized, serializer):
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
