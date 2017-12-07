# Copyright (c) Microsoft. All rights reserved. Licensed under the MIT license. See LICENSE.txt in the project root for license information.
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from outlook.authhelper import get_signin_url, get_token_from_code, get_access_token
from outlook.outlookservice import get_me, get_my_messages, get_my_events, get_my_contacts
import time


# Create your views here.

def home(request):
    redirect_uri = request.build_absolute_uri(reverse('outlook:gettoken'))
    sign_in_url = get_signin_url(redirect_uri)
    context = {'signin_url': sign_in_url}
    return render(request, 'outlook/home.html', context)


def gettoken(request):
    auth_code = request.GET['code']
    redirect_uri = request.build_absolute_uri(reverse('outlook:gettoken'))
    token = get_token_from_code(auth_code, redirect_uri)
    access_token = token['access_token']
    user = get_me(access_token)
    refresh_token = token['refresh_token']
    expires_in = token['expires_in']

    # expires_in is in seconds
    # Get current timestamp (seconds since Unix Epoch) and
    # add expires_in to get expiration time
    # Subtract 5 minutes to allow for clock differences
    expiration = int(time.time()) + expires_in - 300

    # Save the token in the session
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token
    request.session['token_expires'] = expiration
    request.session['user_email'] = user['mail']

    return HttpResponseRedirect(reverse('outlook:mail'))


def mail(request):
    access_token = get_access_token(request, request.build_absolute_uri(reverse('outlook:gettoken')))
    user_email = request.session['user_email']
    # If there is no token in the session, redirect to home
    if not access_token:
        return HttpResponseRedirect(reverse('outlook:home'))
    else:
        messages = get_my_messages(access_token, user_email)
        context = {'messages': messages['value']}
        return render(request, 'outlook/mail.html', context)


def events(request):
    access_token = get_access_token(request, request.build_absolute_uri(reverse('outlook:gettoken')))
    user_email = request.session['user_email']
    # If there is no token in the session, redirect to home
    if not access_token:
        return HttpResponseRedirect(reverse('outlook:home'))
    else:
        events = get_my_events(access_token, user_email)
        context = {'events': events['value']}
        return render(request, 'outlook/events.html', context)


def contacts(request):
    access_token = get_access_token(request, request.build_absolute_uri(reverse('outlook:gettoken')))
    user_email = request.session['user_email']
    # If there is no token in the session, redirect to home
    if not access_token:
        return HttpResponseRedirect(reverse('outlook:home'))
    else:
        contacts = get_my_contacts(access_token, user_email)
        context = {'contacts': contacts['value']}
        return render(request, 'outlook/contacts.html', context)