import json
import pytest

from google.appengine.ext import testbed
from tests import BaseTestCase
from server import api, models

class TestApiRoutes(BaseTestCase):
    def create_app(self):
        return api.create_app()
    
    @pytest.fixture
    def with_users(self, app):
        """Tests with this fixture will have the following users injected into
        the test context.
        """
        with app.app_context():
            models.User.create(name='foo', email='foo@acme.org')
            models.User.create(name='bar', email='bar@acme.org')

    def test_api_should_return_list_of_users(self, app, client, with_users):
        """Test should return list of users.
        """
        print('=============')
        resp = client.get('/api/users', headers=self.make_headers())

        # make sure we have expected response
        self.assert_valid_response(resp)

        # parse the return data and assert correctness
        users = json.loads(resp.get_data(as_text=True))
        assert any(u['name'] == 'foo' and u['email'] == 'foo@acme.org' for u in users)
        assert any(u['name'] == 'bar' and u['email'] == 'bar@acme.org' for u in users)


    def test_api_should_create_user(self, app, client, with_users):
        """Test should create a user and add to datastore.
        """
        # we start with only 2 users
        assert models.User.query().count() == 2

        # when
        resp = client.post('/api/users', 
            headers=self.make_headers(),
            data=json.dumps(dict(name='neo', email='neo@acme.org')))

        # make sure we have expected response
        self.assert_valid_response(resp)

        created_user = json.loads(resp.get_data(as_text=True))
        assert created_user['name'] == 'neo' and created_user['email'] == 'neo@acme.org'
        assert models.User.query().count() == 3