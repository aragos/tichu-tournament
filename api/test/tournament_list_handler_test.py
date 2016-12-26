import json
import unittest
import webtest
import os

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

  def testCreateTournament_unauthorized(self):
    params = {'name': 'name1', 'no_pairs': 8, 'no_boards': 24}
    response = self.testapp.post_json("/api/tournaments", params, expect_errors=True)
    self.assertEqual(response.status_int, 401)

  def testCreateTournament_empty_name(self):
    self.loginUser()
    params = {'name': '', 'no_pairs': 8, 'no_boards': 24}
    response = self.testapp.post_json("/api/tournaments", params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testCreateTournament_bad_num_pairs(self):
    self.loginUser()
    params = {'name': 'name1', 'no_pairs': '8a', 'no_boards': 24}
    response = self.testapp.post_json("/api/tournaments", params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testCreateTournament_bad_num_boards(self):
    self.loginUser()
    params = {'name': 'name1', 'no_pairs': 8, 'no_boards': '24b'}
    response = self.testapp.post_json("/api/tournaments", params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testCreateTournament_invalid_num_boards(self):
    self.loginUser()
    params = {'name': 'name1', 'no_pairs': 8, 'no_boards': '-1'}
    response = self.testapp.post_json("/api/tournaments", params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': 'name1', 'no_pairs': 8}
    response = self.testapp.post_json("/api/tournaments", params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testCreateTournament_invalid_num_pairs(self):
    self.loginUser()
    params = {'name': 'name1', 'no_pairs': -1, 'no_boards': '24'}
    response = self.testapp.post_json("/api/tournaments", params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': 'name1', 'no_pairs': 1, 'no_boards': '24'}
    response = self.testapp.post_json("/api/tournaments", params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': 'name1', 'no_boards': 24}
    response = self.testapp.post_json("/api/tournaments", params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testCreateTournament_invalid_movement_config(self):
    self.loginUser()
    params = {'name': 'name1', 'no_pairs': 8, 'no_boards': 21}
    response = self.testapp.post_json("/api/tournaments", params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    

  def testListTournaments_unauthorized(self):
    response = self.testapp.get("/api/tournaments", expect_errors=True)
    self.assertEqual(response.status_int, 401)

  def testSimpleListTournaments(self):
    self.loginUser()

    params = {'name': 'name1', 'no_pairs': 8, 'no_boards': 24}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']
    self.assertIsNotNone(id)
    response = self.testapp.get("/api/tournaments")
    self.assertEqual(response.status_int, 200)
    tourneys = json.loads(response.body)
    tourneys_list = tourneys["tournaments"]
    self.assertIsNotNone(tourneys_list)
    self.assertEqual(1, len(tourneys_list))
    self.assertEqual('name1', tourneys_list[0]['name'])
    self.assertEqual(int(id), tourneys_list[0]['id'])

  def testListTournaments(self):
    self.loginUser()

    # First fetch an empty list.
    response = self.testapp.get("/api/tournaments")
    self.assertEqual(response.status_int, 200)
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(0, len(tourneys["tournaments"]))
    
    # Now let's add a tournament.
    params = {'name': 'name1', 'no_pairs': 8, 'no_boards': 24}
    self.testapp.post_json("/api/tournaments", params)
    response = self.testapp.get("/api/tournaments")
    self.assertEqual(response.status_int, 200)
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(1, len(tourneys["tournaments"]))

    # And another.
    params = {'name': 'name2', 'no_pairs': 9, 'no_boards': 27}
    self.testapp.post_json("/api/tournaments", params)
    response = self.testapp.get("/api/tournaments")
    self.assertEqual(response.status_int, 200)
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(2, len(tourneys["tournaments"]))

    # Different user should not see any tournaments.
    self.loginUser(email='user2@example.com', id = '444')
    response = self.testapp.get("/api/tournaments")
    self.assertEqual(response.status_int, 200)
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(0, len(tourneys["tournaments"]))

    self.testapp.post_json("/api/tournaments", params)
    response = self.testapp.get("/api/tournaments")
    self.assertEqual(response.status_int, 200)
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(1, len(tourneys["tournaments"]))

    # Back to original user.
    self.loginUser()
    response = self.testapp.get("/api/tournaments")
    self.assertEqual(response.status_int, 200)
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(2, len(tourneys["tournaments"]))

  def loginUser(self, email='user@example.com', id='123', is_admin=False):
    self.testbed.setup_env(
      user_email=email,
      user_id=id,
      user_is_admin='1' if is_admin else '0',
      overwrite=True)

