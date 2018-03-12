import os
import pytest
import json

import sys
sys.path.insert(1, '/Volumes/Data/Projects/gcloud/google-cloud-sdk/platform/google_appengine')
sys.path.insert(1, '/Volumes/Data/Projects/gcloud/google-cloud-sdk/platform/google_appengine/lib/yaml/lib')

if 'google' in sys.modules:
   del sys.modules['google']


from flask import current_app
from starter_app import factory
from starter_app import models
from . import settings
from google.appengine.ext import testbed
from google.appengine.ext import ndb

@pytest.fixture
def app():
   """
   Fixture that makes app available for each test.
   """
   _testbed = testbed.Testbed()
   _testbed.activate()
   _testbed.init_datastore_v3_stub()
   _testbed.init_memcache_stub()
   ndb.get_context().clear_cache()

   app = factory.create_app(opt_settings=settings)
   with app.app_context():
      yield app


@pytest.fixture
def client(app):
   """
   Fixture that makes the Flask test client available.
   """
   return app.test_client()


def make_headers(headers={}):
   """
   Utility for creating headers. By default assumes request is
   of application/json.
   """
   _headers = {'Content-Type': 'application/json'}
   _headers.update(headers)
   return _headers


def assert_valid_response(resp, status_code=200, content_type='application/json'):
   """
   Make sure we have an expected response.
   """
   assert resp.status_code == status_code
   assert resp.content_type == content_type
