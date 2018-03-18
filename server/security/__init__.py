"""
    server.security
"""
import glob
import inspect
import sys
import importlib

from clients import OAuthClientFactory

__all__ = ['oauth_factory']

oauth_factory = OAuthClientFactory()
