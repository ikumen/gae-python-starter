import logging

from collections import namedtuple
from google.appengine.ext import ndb


class AbstractModel(object):
   @classmethod
   def to_key(urlsafe_key):
      """
      Helper for converting urlsafe key to model key.
      https://cloud.google.com/appengine/docs/standard/python/ndb/creating-entity-keys

      :param urlsafe_key: urlsafe key string to convert to a key
      """
      return ndb.Key(urlsafe=urlsafe_key)

   @classmethod
   def _isinstance(cls, model, raise_error=True):
      """
      Check if given model is of same type as implementing class.

      :param model: the model instance to check
      :param raise_error: indicate if we should raise an error on type mismatch
      :returns True if model is instance of given class
      """
      result = isinstance(model, cls)
      if not result and raise_error:
         raise ValueError('%s is not of type %s' % (model, cls))
      return result

   @classmethod
   def _preprocess_new_params(cls, **kwargs):
      """
      Preprocess params used to create a new instance implementing model.
      The default implementation converts string-based datetime values to
      actual datetime.datetime value.

      :param kwargs: dictionary of params for creating a new model
      :returns **kwargs for downstream processing
      """
      return kwargs

   @classmethod
   def new(cls, **kwargs):
      """
      Creates a new instance of implementing class but does not actually persists.

      :param kwargs: dictionary of params for creating new instance
      :returns newly created instance
      """
      return cls(**cls._preprocess_new_params(**kwargs))

   @classmethod
   def create(cls, **kwargs):
      """
      Creates a new instance of implementing class and saves it.

      :param kwargs: dictionary of params for creating new instance
      :returns saved instance
      """
      instance = cls.new(**kwargs)
      instance.save()
      return instance

   @classmethod
   def list(cls, parent_key=None, limit=50):
      """
      Returns all instances of implementing class.

      :param parent_key: optional ancestor key to filter by
      :param limit: optional fetch limit, defaults to 50
      """
      query = cls.query() if parent_key is None else cls.query(ancestor=ndb.Key(urlsafe=parent_key))
      return query.fetch(limit)

   @classmethod
   def get(cls, key):
      """
      Returns instance of implementing class identified by given key.
      Key should be in urlsafe format, see:
      https://cloud.google.com/appengine/docs/python/ndb/creating-entities#Python_retrieving_entities

      :param key: identifying key
      """
      try:
         return ndb.Key(urlsafe=key).get()
      except ProtocolBufferDecodeError:
         return None


   def get_key(self):
      """
      Returns the key for this instance.
      https://cloud.google.com/appengine/docs/standard/python/ndb/creating-entity-keys
      """
      return self.key.urlsafe()

   def get_parent_key(self):
      """
      Returns this instance's parent key.
      """
      return self.key.parent().urlsafe()

   def save(self):
      """
      Save this instance to datastore.
      """
      self.put()

   def delete(self):
      """
      Delete this instance from datastore.
      """
      self.key.delete()

   def as_dict(self, include=all, exclude=None):
      """
      Returns a dictionary representation for an instance of the implementing class.
      https://cloud.google.com/appengine/docs/standard/python/ndb/modelclass#Model_to_dict
      """
      result = super(AbstractModel, self).to_dict(include, exclude)
      result['key'] = self.key.urlsafe()
      return result


class User(AbstractModel, ndb.Model):
   name = ndb.StringProperty()
   email = ndb.StringProperty()
   created_at = ndb.DateTimeProperty(auto_now_add=True)


