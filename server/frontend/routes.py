import os

from flask import Blueprint, render_template, current_app, redirect, session, request
from .. import security

bp = Blueprint('home', __name__)


@bp.route('/signout')
def signout():
    """Invalidate user session, and redirect them to homepage."""
    session.clear()
    return redirect('/')

@bp.route('/signin/<provider_id>')
@security.start_oauth_signin
def signin(provider_id):
    pass

@bp.route('/signin/<provider_id>/complete')
@security.end_oauth_signin
def signin_complete(provider_id, oauth_result=None):
    pass
