import logging
import os
import yaml

from abc import ABCMeta, abstractmethod

class Configuration(object):
    def __init__(self,
            default_settings='default.yaml',
            override_settings=None,
            secret_settings=None,
            ignore_errors=True):
        """Construct this Configuration with given settings. Each of the settings
        params should be: 1) string path to a YAML file or 2) list of string paths
        to YAML files containing the settings. See class description for details on
        loading process and order.

        @param default_settings string or list of string paths to settings file(s) 
                                that will provide default settings.
        @param override_settings string or list of string paths to settings file(s) 
                                that will override default settings. This is a good 
                                place to put environment specific settings.
        @param secret_settings string or list of string paths to settings file(s) 
                                that will override all override and default settings. 
                                This is a good place to put secret settings (make sure 
                                to keep out of source control).
        @param ignore_errors errors should be ignore if True
        """
        self.ignore_errors = ignore_errors
        self.settings = {}

        # Normalize paths, order is important here as later settings 
        # will override earlier settings.
        paths = self._normalize_paths(
            default_settings,
            override_settings,
            secret_settings)

        # load the settings, then resolve any missing settings
        self.settings = self.resolve_settings(self._load_all_settings(paths, {}))

    @abstractmethod
    def resolve_settings(self, settings):
        """Resolve any missing settings.
        
        @param settings dictionary of settings
        """
        pass

    def _load_all_settings(self, paths, settings={}):
        """Load settings for each of the paths given, merging each set of 
        settings with previously loaded. Again later settings will override 
        settings loaded earlier.

        @param paths list of paths to load settings from
        @param settings dictionary to store the settings
        """
        if not isinstance(settings, dict):
            raise TypeError('settings must be a dictionary!')
        for p in paths:
            self._merge_settings(settings, self._load_settings(p))
        return settings


    def _merge_settings(self, to_settings, from_settings):
        """Merges two given settings (dictionaries) recursively. This is a very
        naive implementation that expects the two dictionaries to be fairly similar
        in structure.
        """
        if from_settings is not None:
            for k, v in from_settings.items():
                # if key/value in from exists in to, try to merge or replace
                if k in to_settings and isinstance(to_settings[k], dict):
                    self._merge_settings(to_settings[k], v) # merge
                else:
                    to_settings[k] = v # replace
        return to_settings


    def _load_settings(self, path):
        """Loads and returns YAML settings from file at given path.
        
        @param path where to find YAML settings file.
        """
        try:
            with open(path) as f:
                settings = yaml.safe_load(f)
                if isinstance(settings, dict):
                    return settings
                else:
                    raise yaml.YAMLError('Unable to parse/load {}'.format(path))
        except(IOError, yaml.YAMLError) as e:
            if self.ignore_errors:
                logging.info(e)
                return None
            else:
                raise e

    def _normalize_paths(self, *args):
        """Returns a list of all the settings paths, normalized and validated."""
        paths = []
        for s in args:
            if s is None:
                continue
            elif self._is_valid_path(s):
                paths.append(s)
            elif isinstance(s, list) and all(self._is_valid_path(_) for _ in s):
                paths = paths + s
            elif not self.ignore_errors:
                raise TypeError('Only string or list of string paths are supported!')
        return paths

    def _is_valid_path(self, s):
        """Helper for validating path is actual file"""
        return isinstance(s, basestring) and os.path.isfile(s)

    def get(self):
        """Return our simple Settings object containing our loaded and 
        resolved settings, in a form that Flask can consume.
        """
        return self.Settings(**self.settings)

    class Settings(object):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


    