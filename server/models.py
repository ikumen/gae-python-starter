import logging

from collections import namedtuple
from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from .helpers import JSONSerializable


class AbstractModel(JSONSerializable, ndb.Model):
    @classmethod
    def to_key(urlsafe_key):
        """Helper for converting urlsafe key to model key.
        https://cloud.google.com/appengine/docs/standard/python/ndb/creating-entity-keys

        @param urlsafe_key urlsafe key string to convert to a key
        """
        return ndb.Key(urlsafe=urlsafe_key)

    @classmethod
    def _isinstance(cls, model, raise_error=True):
        """Check if given model is of same type as implementing class.

        @param model the model instance to check
        @param raise_error indicate if we should raise an error on type mismatch
        @returns True if model is instance of given class
        """
        result = isinstance(model, cls)
        if not result and raise_error:
            raise ValueError('%s is not of type %s' % (model, cls))
        return result

    @classmethod
    def _preprocess_new_params(cls, **kwargs):
        """Preprocess params used to create a new instance implementing model.
        The default implementation converts string-based datetime values to
        actual datetime.datetime value.

        @param kwargs dictionary of params for creating a new model
        @returns **kwargs for downstream processing
        """
        return kwargs

    @classmethod
    def new(cls, **kwargs):
        """Creates a new instance of implementing class but does not actually persists.

        @param kwargs dictionary of params for creating new instance
        @returns newly created instance
        """
        return cls(**cls._preprocess_new_params(**kwargs))

    @classmethod
    def create(cls, **kwargs):
        """Creates a new instance of implementing class and saves it.

        @param kwargs dictionary of params for creating new instance
        @returns saved instance
        """
        instance = cls.new(**kwargs)
        instance.save()
        return instance

    @classmethod
    def list(cls, parent_key=None, limit=50):
        """Returns all instances of implementing class.

        @param parent_key optional ancestor key to filter by
        @param limit optional fetch limit, defaults to 50
        """
        query = cls.query() if parent_key is None else cls.query(ancestor=ndb.Key(urlsafe=parent_key))
        return query.fetch(limit)

    @classmethod
    def count(cls, parent_key=None):
        """Returns a count of all instances for implementing class.

        @param parent_key optional ancestor key to filter by
        """
        return cls.query().count() if parent_key is None else cls.query(ancestor=ndb.Key(urlsafe=parent_key))

    @classmethod
    def get_by_key(cls, key):
        """Returns instance of implementing class identified by given urlsafe key.
        Key should be in urlsafe format, see:
        https://cloud.google.com/appengine/docs/python/ndb/creating-entities#Python_retrieving_entities

        @param key identifying key
        """
        try:
            return ndb.Key(urlsafe=key).get()
        except ProtocolBufferDecodeError:
            return None

    @classmethod
    def get_by_id(cls, id):
        """Returns instance of implementing class identified by given id.
        
        @param id identifier
        """
        try:
            return ndb.Key(cls, id).get()
        except ProtocolBufferDecodeError:
            return None

    def get_key(self):
        """Returns the key for this instance.
        https://cloud.google.com/appengine/docs/standard/python/ndb/creating-entity-keys
        """
        return self.key.urlsafe()

    def get_parent_key(self):
        """Returns this instance's parent key.
        """
        return self.key.parent().urlsafe()

    def save(self):
        """Save this instance to datastore.
        """
        self.put()
        return self

    def delete(self):
        """Delete this instance from datastore.
        """
        self.key.delete()

    def to_json(self):
        rv = self.to_dict()
        rv['key'] = self.key.urlsafe()
        return rv


class Setting(AbstractModel):
    value = ndb.StringProperty()

class OAuth(AbstractModel):
    """Class representing OAuth token, and User group (e.g. parent=User)
    """
    # Unique identifier from OAuth provider
    identity = ndb.StringProperty(indexed=True, required=True)
    # Identity of OAuth provider (e.g. google)
    provider_id = ndb.StringProperty(indexed=True, required=True)
    # Dict of token type, refresh token, and access token
    token = ndb.JsonProperty()
    created_at = ndb.DateTimeProperty()

    def update_token(self, token):
        self.token = token
        self.save()

    @classmethod
    def find_by_identity(cls, identity, provider_id):
        """Find an instance of OAuth with given identity and provider.

        @param identity identifier unique to given provider
        @param provider_id id of OAuth provider
        """
        return cls.query(cls.identity == identity, cls.provider_id == provider_id).get()
        
    @classmethod
    def _preprocess_new_params(cls, **kwargs):
        """Make sure all OAuth instances are ancestors of User (ie, children).
        """
        if 'parent' not in kwargs:
            raise ValueError('OAuth requires a parent (eg, belongs to a User)')
        return super(OAuth, cls)._preprocess_new_params(**kwargs)


class User(AbstractModel):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_or_create_by_oauth_info(cls, oauth_info):
        oauth = OAuth.find_by_identity(oauth_info['identity'], oauth_info['provider_id'])
        if oauth is None:
            return ndb.transaction(lambda: cls._create_user_with_oauth(oauth_info))
        else:
            ndb.transaction(oauth.update_token(oauth_info['token']))
            return oauth.key.parent().get()

    @classmethod   
    def _create_user_with_oauth(cls, oauth_info):
        oauth = OAuth.create(parent=cls.create().key, **oauth_info)
        return oauth.key.parent().get()

 

