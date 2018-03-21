import logging
import os

from abc import ABCMeta, abstractmethod
from functools import wraps
from flask import Flask, session, jsonify
from requests_oauthlib import OAuth2Session
from . import constants


class UnauthorizedException(Exception):
    """Thrown when there's an unauthorized access attempt.
    """
    pass

class OAuthClientException(Exception):
    """Generic OAuthClient related exception.
    """
    pass

class OAuthClient(object):
    """Base OAuth client class that handles interactions with an OAuth provider.
    Under the hood the class delegates the actual OAuth details to one of the
    OAuthSession classes.
    """
    __metaclass__ = ABCMeta

    def __init__(self, config, **kwargs):
        self.config = config
        self.token = kwargs.get('token')
        self.post_construct(**kwargs)

    @abstractmethod
    def post_construct(self, **kwargs):
        """Handle any post construct configurations."""
        pass

    @abstractmethod
    def authorize(self):
        """Starts the OAuth dance."""
        pass
    
    @abstractmethod
    def fetch_token(self, **kwargs):
        """Fetch token from provider."""
        pass

    @abstractmethod
    def parse_token_response(self, oauth_resp):
        """Parses the token response from provider."""
        pass

    @abstractmethod
    def post_parse_token_response(self, oauth_resp):
        """Called user has been authenticated and token from OAuth provider
        has been parsed.
        """
        pass

    def fetch_parse_token(self, **kwargs):
        """Performs the fetch and parse sequence, delegating
        each step to client implementations.
        """
        oauth_resp = self.fetch_token(**kwargs)
        return self.parse_token_response(oauth_resp)

    def version(self):
        """Returns the OAuth version."""
        return self.config.get('VERSION')


class OAuth2Client(OAuthClient):
    """OAuth2 specific client that handles interactions with an OAuth provider.
    Actual work is done by OAuth2Session.
    """

    def __init__(self, config, state=None, token=None, **kwargs):
        super(OAuth2Client, self).__init__(config, state=state, token=token)
        self.session = OAuth2Session(
                config.get(constants.K_OAUTH_CLIENT_ID),
                scope=config.get('SCOPE'),
                state=state,
                token=token,
                redirect_uri=config.get(constants.K_OAUTH_CALLBACK_URL), 
                **kwargs)

    def authorize(self, **kwargs):
        """Starts an OAuth2 specific authorization dance.
        """
        return self.session.authorization_url(
            self.config.get(constants.K_OAUTH_AUTH_URL),
            access_type=self.config.get('ACCESS_TYPE', None),
            approval_prompt='force',
            include_granted_scopes='true')

    def fetch_token(self, oauth_resp):
        """Fetch the OAuth tokens from configured provider.
        """
        return self.session.fetch_token(
            self.config.get(constants.K_OAUTH_TOKEN_URL),
            client_secret=self.config.get(constants.K_OAUTH_CLIENT_SECRET),
            authorization_response=oauth_resp)

    def post_construct(self, **kwargs):
        pass