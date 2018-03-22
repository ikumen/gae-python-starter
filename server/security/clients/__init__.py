import glob
import importlib
import inspect
import logging
import os

from ..core import OAuth2Client, OAuthClientException


__all__ = ['OAuthClientFactory']


class OAuthClientFactory(object):
    K_CLIENTS = 'CLIENTS'

    def __init__(self):
        self.clients = {}
        self.config = {}

    def init_config(self, config):
        """Initialize factory with client modules.

        @param config OAuth settings
        """
        # TODO: reloadable???
        self.config.update(config)

        # OAuth config are stored in YAML with uppercase provider ids (flask 
        # config only takes upper case configs), but we'll normalize the client
        # id values to lower case so it's consistent throughout codebase
        if self.K_CLIENTS in config:
            client_configs = {}
            for pid in config[self.K_CLIENTS]:
                client_configs[pid.lower()] = config[self.K_CLIENTS][pid]
            self.config[self.K_CLIENTS] = client_configs

        # TODO: encapsulate
        # Search the security.clients folder for client implementations, load them
        # up and get the implementing OAuthClient classes for our factory.
        module_names = glob.glob('{}/{}'.format(os.path.dirname(__file__),'*_client.py'))
        for n in module_names:
            module = importlib.import_module('.{}'.format(os.path.basename(n)[:-3]), __name__)
            for name, obj in inspect.getmembers(module):
                # OAuthClient subclasses have following name pattern *OAuthClient, let's
                # store all the names in lower case to make it consistent throughout
                pid = name[:-11].lower()
                # Make sure we have a subclass of OAuthClient
                if pid in self.config[self.K_CLIENTS] \
                  and inspect.isclass(obj) \
                  and issubclass(obj, OAuth2Client) \
                  and obj is not OAuth2Client:
                    # Save reference of id with implementing class
                    self._register_client_class(pid, obj)


    def _register_client_class(self, provider_id, client_class):
        """Registers the OAuthClient class for the given provider

        @param provider_id OAuth provider id (e.g. google)
        @param client_class OAuthClient implementation class
        """
        if provider_id in self.clients:
            logging.warn('Provider "%s" already registered!', provider_id)
        else:
            logging.debug('Registering: %s', provider_id)
            self.clients[provider_id] = client_class

    def _get_client_class(self, provider_id):
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
        if provider_id not in self.config[self.K_CLIENTS]:
            raise OAuthClientException('Provider {} config not found!'.format(provider_id))
        return self.config[self.K_CLIENTS][provider_id]

    def create_client(self, provider_id, token=None, state=None):
        """Create an instance of OAuthClient for given provider.
        
        @param provider_id provider id (e.g. google)
        """
        cls = self._get_client_class(provider_id)
        return cls(provider_id, self._get_client_config(provider_id),token=token, state=state)

        

