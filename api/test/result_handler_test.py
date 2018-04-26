import json
import unittest
import webtest
import os
import sys
import test_utils

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

  def testScoreTournament_not_logged_in(self):
    self.loginUser()
    id = self.buildFullTournament()
    self.logoutUser()
    response = self.testapp.get("/api/tournaments/{}/results".format(id), expect_errors=True)
    self.assertEqual(response.status_int, 401)

  def testScoreTournament_does_not_own(self):
    self.loginUser()
    id = self.buildFullTournament()
    self.loginUser(email='user2@example.com', id='234')
    response = self.testapp.get("/api/tournaments/{}/results".format(id), expect_errors=True)
    self.assertEqual(response.status_int, 403)
    
  def testScoreTournament_bad_id(self):
    self.loginUser()
    id = self.buildFullTournament()
    response = self.testapp.get("/api/tournaments/{}a/results".format(id), expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testScoreTournament(self):
    self.loginUser()
    id = self.buildFullTournament()
    response = self.testapp.get("/api/tournaments/{}/results".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    expected_dict = json.loads(open(os.path.join(os.getcwd(), 
                              'api/test/example_tournament_results.txt')).read())
    self.assertEqual(expected_dict, response_dict)

  def testScoreTournament_legacy(self):
    self.loginUser()
    id = self.buildFullTournament(True)
    response = self.testapp.get("/api/tournaments/{}/results".format(id))
    self.assertEqual(response.status_int, 200)

  def testCheckCompleteScoring_not_logged_in(self):
    self.loginUser()
    id = self.buildFullTournament()
    self.logoutUser()
    response = self.testapp.get(
        "/api/tournaments/{}/handStatus".format(id),
        expect_errors=True)
    self.assertEqual(response.status_int, 401)

  def testCheckCompleteScoring_does_not_own(self):
    self.loginUser()
    id = self.buildFullTournament()
    self.loginUser(email='user2@example.com', id='234')
    response = self.testapp.get(
        "/api/tournaments/{}/handStatus".format(id),
        expect_errors=True)
    self.assertEqual(response.status_int, 403)
    
  def testCheckCompleteScoring_bad_id(self):
    self.loginUser()
    id = self.buildFullTournament()
    response = self.testapp.get(
        "/api/tournaments/{}a/handStatus".format(id),
        expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testCheckCompleteTournament_all_scored(self):
    self.loginUser()
    id = self.buildFullTournament()
    response = self.testapp.get(
        "/api/tournaments/{}/handStatus".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    for round in response_dict['rounds']:
      self.assertEqual([], round['unscored_hands'])

  def testCheckCompleteTournament_none_scored(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get(
        "/api/tournaments/{}/handStatus".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    num_hands = sum([len(x['unscored_hands']) for x in response_dict['rounds']])
    self.assertEqual(72, num_hands)

  def testCheckCompleteTournament_some_scored(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'ns_score': 75,
              'ew_score': 25}
    response = self.testapp.put_json(
        "/api/tournaments/{}/hands/7/2/7".format(id), params)
    response = self.testapp.get(
        "/api/tournaments/{}/handStatus".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    num_unscored = sum([len(x['unscored_hands']) for x in response_dict['rounds']])
    num_scored = sum([len(x['scored_hands']) for x in response_dict['rounds']])
    expected_scored = [{"hand": 7, "ns_pair": 2,
                        "ew_pair" : 7, "table" : 2,
                        "ns_names": ["My name", None],
                        "ew_names": [None, None]}]
    self.assertEqual(71, num_unscored)
    self.assertEqual(1, num_scored)
    self.assertEqual(expected_scored, response_dict['rounds'][0]['scored_hands'])

  def AddBasicTournament(self):
    params = {'name': 'name', 'no_pairs': 8, 'no_boards': 24,
              'players': [{'pair_no': 2, 'name': "My name", 
                           'email': "My email"}, {'pair_no': 7}]}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']
    self.assertIsNotNone(id)
    return id

  def buildFullTournament(self, legacy=False):
    if legacy:
      params = {'name' : 'Test Tournament', 'no_pairs': 7, 'no_boards': 14}
      response = self.testapp.post_json("/api/tournaments", params)
      response_dict = json.loads(response.body)
      id = response_dict['id']
      test_utils.setLegacyId(id, 1)
      json_data=open(os.path.join(os.getcwd(), 
                     'api/test/example_tournament_legacy.txt')).read();
    else:
      params = {'name' : 'Test Tournament', 'no_pairs': 7, 'no_boards': 21}
      response = self.testapp.post_json("/api/tournaments", params)
      response_dict = json.loads(response.body)
      id = response_dict['id']
      json_data=open(os.path.join(os.getcwd(), 
                     'api/test/example_tournament.txt')).read();
    tourney_dict = json.loads(json_data)
    for hand in tourney_dict['hands']:
      params = {'calls' : hand['calls'],
                'ns_score' : hand['ns_score'],
                'ew_score' : hand['ew_score']}
      if hand.get('notes'):
        params['notes'] = hand.get('notes')
      response = self.testapp.put_json("/api/tournaments/{}/hands/{}/{}/{}".format(
                                           id, int(hand['board_no']), int(hand['ns_pair']),
                                           int(hand['ew_pair'])),
                                       params)
    return id

  def logoutUser(self):
    self.testbed.setup_env(
      user_email='',
      user_id='',
      user_is_admin='',
      overwrite=True)
 
  def loginUser(self, email='user@example.com', id='123', is_admin=False):
    self.testbed.setup_env(
      user_email=email,
      user_id=id,
      user_is_admin='1' if is_admin else '0',
      overwrite=True)
