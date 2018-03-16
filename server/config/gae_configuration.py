import logging

from core import Configuration
from ..models import Setting

class GAEDataStoreConfiguration(Configuration):
    def __init__(self, **kwargs):
        self.place_holder = '__REPLACE_ME__'
        super(GAEDataStoreConfiguration, self).__init__(**kwargs)

    def resolve_settings(self, settings):
        unresolved = []
        self._resolve([], settings, unresolved)
        if len(unresolved) > 0:
            msg = 'Unresolved settings: {}'.format(unresolved)
            warning_msg = '''
            \n***************************************************************************
            \n{}
            \n***************************************************************************
            '''.format(msg)
            logging.warn(warning_msg)
            if not self.ignore_errors:
                raise LookupError(msg)
        return settings


    def _resolve(self, path, settings, unresolved):
        if isinstance(settings, dict):
            for k,v in settings.items():
                if not k.isupper():
                    continue
                path.append(''.join(['_', k]))
                if v is None:
                    id = (''.join(path))[1:]
                    value = self._get_setting_from_datastore(id)
                    settings[k] = value
                    if value is None:
                        unresolved.append(id)
                elif hasattr(v, '__iter__'):
                    self._resolve(path, v, unresolved)
                path.pop()
        elif isinstance(settings, list):
            for _ in settings:
                self._resolve(path, _, unresolved)

    def _get_setting_from_datastore(self, id):
        """Return setting from datastore with given id/key. If the setting
        is missing, put a place holder in it's place.
        """
        setting = Setting.get_by_id(id)
        if setting is None:
            setting = Setting.create(id=id, value=self.place_holder)
        
        if setting.value == self.place_holder:
            # Returning setting with placeholder is useless, return None
            # instead so caller can act on it.
            return None 
        else:    
            return setting.value
