from flask import redirect, url_for
from . import auth

@auth.route('/login')
def login():
    # Redirect to the external login page
    return redirect('https://external-login-url.com')
