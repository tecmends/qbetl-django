from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.authtoken.admin import Token
from qbconnect.models import UserConnection
from quickbooks import Oauth2SessionManager
from django.conf import settings

# Create your views here.

def get_user_for_token(key):
    user = Token.objects.get(key=key).user
    return user


def connect_with_qb(request):
    origin = request.META['HTTP_HOST']
    scheme = request.META['wsgi.url_scheme']
    print(origin)
    key = request.GET.get("token")
    user = get_user_for_token(key)
    connection = UserConnection.objects.get(user=user)
    client_id = connection.consumer_key
    client_secret = connection.consumer_secret

    session_manager = Oauth2SessionManager(
        client_id=client_id,
        client_secret=client_secret,
        base_url=origin,
    )

    #callback_url = "https://qbetldev.tecnicslabs.com/qbetl/connectsuccess/"  # Quickbooks will send the response to this url
    #callback_url = "http://localhost:8000/qbetl/connectsuccess/".format(scheme, origin)  # Quickbooks will send the response to this url
    callback_url = settings.QB_CALL_BACK_URL
    authorize_url = session_manager.get_authorize_url(callback_url, state=key)
    print(authorize_url)
    return redirect(authorize_url)


def connect_with_qb_success_handler(request):
    origin = request.META['HTTP_HOST']
    scheme = request.META['wsgi.url_scheme']
    key = request.GET['state']
    user = get_user_for_token(key)
    connection = UserConnection.objects.get(user=user)
    client_id = connection.consumer_key
    client_secret = connection.consumer_secret

    #callback_url = "https://qbetldev.tecnicslabs.com/qbetl/connectsuccess/"
    #callback_url = "http://localhost:8000/qbetl/connectsuccess/".format(scheme,
    # Quickbooks will send the response to this url
    callback_url = settings.QB_CALL_BACK_URL
    session_manager = Oauth2SessionManager(
        client_id=client_id,
        client_secret=client_secret,
        base_url=callback_url,
    )
    realm_id = request.GET['realmId']
    session_manager.get_access_tokens(request.GET['code'])

    access_token = session_manager.access_token
    refresh_token = session_manager.refresh_token
    print("access_token:{}".format(access_token))
    print("refresh_token:{}".format(refresh_token))
    connection.company_id = realm_id
    connection.access_token = access_token
    connection.refresh_token = refresh_token
    connection.save()

    return HttpResponse("QB Connected success")
