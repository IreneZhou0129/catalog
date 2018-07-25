# -*- coding: utf-8 -*-
from flask import url_for, request, redirect
from flask import session as login_session
from functools import wraps


def login_status_verification(func):
    ''' decorator manager wrapper for login status '''

    @wraps(func)
    def inner_wrapper(*args, **kwargs):
        if 'username' in login_session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('showLogin', next=request.url))

    return inner_wrapper


def not_authorized_alert():
    function = ""
    function += "<script>"
    function += "function myFunction() {"
    function += "alert('You are not authorized!')}</script>"
    function += "<body onload='myFunction()'>"
    return function
