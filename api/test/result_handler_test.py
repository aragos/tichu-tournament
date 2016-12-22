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

  def buildFullTournament(self):
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

