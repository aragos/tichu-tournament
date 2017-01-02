import json
import os
import unittest
import webtest

from google.appengine.ext import testbed

from api.src import main


class AppTest(unittest.TestCase):
  def setUp(self):
    os.environ['AUTH_DOMAIN'] = 'testbed'

    self.testbed = testbed.Testbed()
    self.testbed.activate()

    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

    self.testapp = webtest.TestApp(main.app)

  def tearDown(self):
    self.testbed.deactivate()

  def testAuth_logged_in(self):
    self.loginUser()
    response = self.testapp.get("/api/checkAuth")
    self.assertEqual(json.loads(response.body)['user'], 'user@example.com')

  def testAuth_not_logged_in(self):
    response = self.testapp.get("/api/checkAuth", expect_errors=True)
    self.assertEqual(response.status_int, 401)

  def loginUser(self, email='user@example.com', id='123', is_admin=False):
    self.testbed.setup_env(
      user_email=email,
      user_id=id,
      user_is_admin='1' if is_admin else '0',
      overwrite=True)
