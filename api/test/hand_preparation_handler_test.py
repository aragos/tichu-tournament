import json
import unittest
import webtest
import os
import time

from google.appengine.ext import testbed

from api.src import main
from api.src import movements

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

  def testGetHandPrep_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}a/handprep".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testGetHandPrep_not_logged_in(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    response = self.testapp.get("/api/tournaments/{}/handprep".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 401)
    
  def testGetHandPrep_does_not_own(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.loginUser('user2@example.com', '345')
    response = self.testapp.get("/api/tournaments/{}/handprep".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 403)                                    

  def testGetHandPrep(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = json.loads(
        self.testapp.get("/api/tournaments/{}/handprep".format(id)).body)
    movement = movements.Movement(7, 2, 7)
    for i in range(1, 8):
      self.assertEqual(movement.GetUnplayedHands(i),
                       response["unplayed_hands"][i - 1]["hands"])
      self.assertEqual(i, response["unplayed_hands"][i - 1]["pair_no"])

  def loginUser(self, email='user@example.com', id='123', is_admin=False):
    self.testbed.setup_env(
      user_email=email,
      user_id=id,
      user_is_admin='1' if is_admin else '0',
      overwrite=True)

  def logoutUser(self):
    self.testbed.setup_env(
      user_email='',
      user_id='',
      user_is_admin='',
      overwrite=True)
      
  def AddBasicTournament(self):
    params = {'name': 'name', 'no_pairs': 7, 'no_boards': 14,
              'players': [{'pair_no': 2, 'name': "My name", 'email': "My email"},
                          {'pair_no': 7}]}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']
    self.assertIsNotNone(id)
    return id
