from gae_configuration import GAEDataStoreConfiguration

__all__ = ['load_settings', 'GAEDataStoreConfiguration']

def load_settings(app, configuration, **kwargs):    
    """Loads the configuration settings for the given Flask application (app).

    @param default_settings string or list of string path(s) to an YAML settings
    @param override_settings sr
    """
    options = dict(
        default_settings='server/config/default.yaml', 
        override_settings=None, 
        secret_settings=None,
        ignore_errors=True)
    options.update(kwargs)
    app.config.from_object(configuration(**options).get())
