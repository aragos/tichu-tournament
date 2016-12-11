import json
import unittest
import webtest
import os

from google.appengine.api import memcache
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

  def testListTournaments_unauthorized(self):
    response = self.testapp.get("/api/tournaments", expect_errors= True)
    self.assertEqual(response.status_int, 401)

  def testListTournaments(self):
    self.loginUser()

    # First fetch an empty list.
    response = self.testapp.get("/api/tournaments")
    self.assertEqual(response.status_int, 200)
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(0, len(tourneys["tournaments"]))
    
    #Now let's add a list.
    params = {'name': 'name', 'no_pairs': 8, 'no_boards': 24}
    self.testapp.post("/api/tournaments", params)
    response = self.testapp.get("/api/tournaments")
    self.assertEqual(response.status_int, 200)
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(1, len(tourneys["tournaments"]))

  def loginUser(self, email='user@example.com', id='123', is_admin=False):
    self.testbed.setup_env(
      user_email=email,
      user_id=id,
      user_is_admin='1' if is_admin else '0',
      overwrite=True)

