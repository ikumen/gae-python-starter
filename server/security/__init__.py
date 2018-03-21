"""
    server.security
"""
import glob
import logging

from functools import wraps
from flask import request, jsonify, redirect, session
from clients import OAuthClientFactory
from core import UnauthorizedException
from .. import constants
from .. import helpers


oauth_factory = OAuthClientFactory()

class Constants(object):
    OAUTH1_VERSION_TAG = '1.0'
    OAUTH2_VERSION_TAG = '2.0'

    K_OAUTH_CLIENT_ID = 'CLIENT_ID'
    K_OAUTH_CLIENT_SECRET = 'CLIENT_SECRET'
    K_OAUTH_CALLBACK_URL = 'CALLBACK_URL'
    K_OAUTH_TOKEN_URL = 'TOKEN_URL'
    K_OAUTH_AUTH_URL = 'AUTHORIZATION_URL'
    K_POST_SIGN_URL = 'POST_SIGNIN_URL'

    K_OAUTH_PROVIDER_ID = 'provider_id'
    K_OAUTH_TOKEN_SESSION = 'token_session_key'
    K_STATE_SESSION = 'state_session_key'
    K_OAUTH_RESULT = 'oauth_result'


def __handle_unauthorized():
    """Force signout, then respond according to acceptable mimetypes.
    """
    session.clear()
    if helpers.use_json_mimetype():
        # TODO: parameterize
        resp = jsonify({'message': 'Unauthorized'})
        resp.status_code = 401
        return resp
    else:
        # TODO: parameterize 
        return redirect('/signin')


def start_oauth_signin(fn):
    """Includes decorated function in OAuth signin flow, specifically
    the decorated function will be called before the flow starts.

    The decorated function is expected to have the following attributes:
     - the session is guaranteed to be clear before function starts
     - function should take a 'provider_id' that references a registered
       OAuth clients
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        session.clear()

        logging.debug('Before `start_oauth_signin` wrapped fn:')
        fn(*args, **kwargs)

        logging.debug('Before start_oauth_signin signin sequence:')
        provider_id = kwargs[Constants.K_OAUTH_PROVIDER_ID]

        oauth_client = oauth_factory.create_client(provider_id)
        authorization_url, state = oauth_client.authorize()
        if oauth_client.version() == Constants.OAUTH1_VERSION_TAG:
            session[Constants.K_OAUTH_TOKEN_SESSION] = state
        elif oauth_client.version() == Constants.OAUTH2_VERSION_TAG:
            session[Constants.K_STATE_SESSION] = state
        else:
            raise RuntimeError('Only OAuth version 1.0 and 2.0 are currently supported!')    

        logging.debug('Sending user to OAuth provider %s for authentication', provider_id)
        return redirect(authorization_url)
    return decorator


def end_oauth_signin(fn):
    """Includes decorated function in OAuth signin flow, specifically
    the decorated function will be called after signin flow completes.

    The decorated function is expected to have the following attributes:
     - function should take a 'provider_id' that references a registered
       OAuth client
     - results of the OAuth signin flow (e.g. access token, user info) 
       will be available to decorated function as a keyword argument
       'oauth_result'
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        oauth_client = oauth_factory.create_client(kwargs[Constants.K_OAUTH_PROVIDER_ID],
            token=session.get(Constants.K_OAUTH_TOKEN_SESSION),
            state=session.get(Constants.K_STATE_SESSION))
        try:
            # Parse out user info from OAuth provider response
            oauth_result = oauth_client.fetch_parse_token(oauth_resp=request.url)
            # Send back parse oauth results to caller
            kwargs[Constants.K_OAUTH_RESULT] = oauth_result
            fn(*args, **kwargs)
        except(UnauthorizedException) as e:
            logging.warn(e)
            return __handle_unauthorized()
        return redirect(oauth_factory.config[Constants.K_POST_SIGN_URL])
    return decorator


def auth_required(fn):
    """Decoreates given function with simple security check before allowing
    it to continue.

    @param fn function to decorate
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        # TODO: Very simple check, additional validation needed?
        if 'user' in session:
            return fn(*args, **kwargs)
        else:
            return __handle_unauthorized()
    return decorator

