import os
import pytest
import json


from google.appengine.ext import testbed
from google.appengine.ext import ndb
from flask import current_app
from server import create_app, models, settings


class BaseTestCase(object):
    def create_app(self):
        pass

    @pytest.fixture
    def app(self):
        """Fixture that makes app available for each test.
        """
        # Setup stubs for GAE datastore and memcache
        # See https://cloud.google.com/appengine/docs/standard/python/tools/localunittesting
        _testbed = testbed.Testbed()
        _testbed.activate()
        _testbed.init_datastore_v3_stub()
        _testbed.init_memcache_stub()
        ndb.get_context().clear_cache()

        app = self.create_app()
        with app.app_context():
            yield app


    @pytest.fixture
    def client(self, app):
        """Fixture that makes the Flask test client available.
        """
        return app.test_client()


    def make_headers(self, headers={}):
        """Utility for creating headers. By default assumes request is
        of application/json.
        """
        _headers = {'Content-Type': 'application/json'}
        _headers.update(headers)
        return _headers


    def assert_valid_response(self, resp, status_code=200, content_type='application/json'):
        """Utility to validate an expected response.
        """
        assert resp.status_code == status_code
        assert resp.content_type == content_type
