import glob
import importlib
import inspect
import logging
import os

from ..core import OAuth2Client, OAuthClientException


__all__ = ['OAuthClientFactory']


class OAuthClientFactory(object):
    def __init__(self):
        self.clients = {}
        self.config = {}

    def init_config(self, config):
        """Initialize factory with client modules.

        @param config OAuth settings
        """
        self.config.update(config)

        module_names = glob.glob('{}/{}'.format(os.path.dirname(__file__),'*_client.py'))
        for n in module_names:
            module = importlib.import_module('.{}'.format(os.path.basename(n)[:-3]), __name__)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, OAuth2Client) and obj is not OAuth2Client:
                    self._register_client(name[:-6].lower(), obj)

    def _register_client(self, provider_id, client_class):
        """Registers the OAuthClient class for the given provider

        @param provider_id OAuth provider id (e.g. google)
        @param client_class OAuthClient implementation class
        """
        if provider_id in self.clients:
            logging.warn('Provider "%s" already registered!', provider_id)
        else:
            logging.debug('Registering: %s', provider_id)
            self.clients[provider_id] = client_class

    def _get_client(self, provider_id):
        """Returns the OAuthClient with given provider id.
        
        @param provider_id OAuth provider id (e.g. google)
        """
        if provider_id not in self.clients:
            raise OAuthClientException('Provider %s not found!', provider_id)
        return self.clients[provider_id]

    def _get_client_config(self, provider_id):
        """Returns the OAuth configuration for given provider.
        
        @param provider_id OAuth provider if (e.g. google)
        """
        if provider_id not in self.config:
            raise OAuthClientException('Provider %s config not found!', provider_id)
        return self.config[provider_id]

    def create_client(self, provider_id, token=None, state=None):
        """Create an instance of OAuthClient for given provider.
        
        @param provider_id provider id (e.g. google)
        """
        return self._get_client(provider_id)(
            self._get_client_config(provider_id),
            token=token,
            state=state)

        

