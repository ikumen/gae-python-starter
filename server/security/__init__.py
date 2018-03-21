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

oauth_factory = OAuthClientFactory()


def __handle_unauthorized():
    """Force signout, then respond according to acceptable mimetypes.
    """
    session.clear()
    # http://flask.pocoo.org/snippets/45
    target = request.accept_mimetypes.best_match([
        constants.MIME_TYPE_APPLICATION_JSON, 
        constants.MIME_TYPE_TEXT_HTML])
    if target == constants.MIME_TYPE_APPLICATION_JSON and \
            request.accept_mimetypes[target] > request.accept_mimetypes[constants.MIME_TYPE_TEXT_HTML]:
        response = jsonify({'message': 'Unauthorized'})
        response.status_code = 401
        return response
    else:
        return redirect('/signin')


def start_oauth_signin(fn):
    """Decorates given function as a start of OAuth signin sequence.
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        session.clear()
        oauth_client = oauth_factory.create_client(kwargs['provider_id'])
        authorization_url, state = oauth_client.authorize()
        if oauth_client.version() == '1.0':
            session[constants.TOKEN_SESSION_KEY] = state
        elif oauth_client.version() == '2.0':
            session[constants.STATE_SESSION_KEY] = state
        else:
            raise RuntimeError('Only OAuth version 1.0 and 2.0 are currently supported!')    
        logging.info('before start_oauth_signin wrapped fn:')
        fn(*args, **kwargs)
        logging.info('after start_oauth_signin wrapped fn:')
        return redirect(authorization_url)
    return decorator


def end_oauth_signin(fn):
    """Decorates given function as end of OAuth signin sequence.
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        oauth_client = oauth_factory.create_client(kwargs['provider_id'],
            token=session.get(constants.TOKEN_SESSION_KEY),
            state=session.get(constants.STATE_SESSION_KEY))
        try:
            email, token = oauth_client.fetch_parse_token(oauth_resp=request.url)
            print(email)
            print(token)
        except(UnauthorizedException) as e:
            print(e)
        fn(*args, **kwargs)
        return redirect(oauth_factory.config['POST_SIGNIN_URL'])
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


__all__ = ['oauth_factory', 'UnauthorizedException', 'start_oauth_signin', 'end_oauth_signin']
