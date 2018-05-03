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

  def testGet_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.AddBasicHand(id)
    response = self.testapp.get("/api/tournaments/{}a/handresults/1".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testGet_bad_parameters(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.AddBasicHand(id)
    response = self.testapp.get("/api/tournaments/{}/handresults/1a".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testGet_director_empty(self):
    self.loginUser();
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}/handresults/1".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual({"results": []}, response_dict)

  def testGet_director_not_empty(self):
    self.loginUser();
    id = self.AddBasicTournament()
    self.AddBasicHand(id);
    params = {'calls': {"west": "T"}, 'ns_score': 50, 'ew_score': -50}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/7/5".format(id),
                                     params)
    self.assertEqual(response.status_int, 204)
    response = self.testapp.get("/api/tournaments/{}/handresults/1".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual({"results": [{'calls': {"west": "T"},
                                   'ew_pair': 5,
                                   'ew_score': -50,
                                   'ns_pair': 7,
                                   'ns_score': 50},
                                  {'calls': {},
                                   'ew_pair': 3,
                                   'ew_score': 25,
                                   'ns_pair': 2,
                                   'ns_score': 75}]}, response_dict)

  def testGet_not_director_unlocked(self):
    self.loginUser();
    id = self.AddBasicTournament()
    self.AddBasicHand(id);
    response = self.testapp.get("/api/tournaments/{}/pairids/2".format(id))
    opaque_id = json.loads(response.body)['pair_id']
    self.logoutUser()
    hand_headers = {'X-tichu-pair-code' : str(opaque_id)}
    response = self.testapp.get("/api/tournaments/{}/handresults/1".format(id),
                                headers=hand_headers, expect_errors=True)
    self.assertEqual(response.status_int, 403)

  def testGet_not_director_locked_not_played(self):
    self.loginUser();
    id = self.AddLockableTournament()
    self.AddBasicHand(id);
    response = self.testapp.get("/api/tournaments/{}/pairids/5".format(id))
    opaque_id = json.loads(response.body)['pair_id']
    self.logoutUser()
    hand_headers = {'X-tichu-pair-code' : str(opaque_id)}
    response = self.testapp.get("/api/tournaments/{}/handresults/1".format(id),
                                headers=hand_headers, expect_errors=True)
    self.assertEqual(response.status_int, 403)

  def testGet_not_director_played_deleted_played(self):
    self.loginUser();
    id = self.AddLockableTournament()
    self.AddBasicHand(id);
    response = self.testapp.get("/api/tournaments/{}/pairids/2".format(id))
    opaque_id = json.loads(response.body)['pair_id']
    response = self.testapp.delete("/api/tournaments/{}/hands/1/2/3".format(id))
    self.assertEqual(response.status_int, 204)
    self.logoutUser()
    hand_headers = {'X-tichu-pair-code' : str(opaque_id)}
    response = self.testapp.get("/api/tournaments/{}/handresults/1".format(id),
                                headers=hand_headers, expect_errors=True)
    self.assertEqual(response.status_int, 403)
    params = {'calls': {}, 'ns_score': 25, 'ew_score': 75}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params, headers=hand_headers)
    self.assertEqual(response.status_int, 204)
    response = self.testapp.get("/api/tournaments/{}/handresults/1".format(id),
                                headers=hand_headers, expect_errors=True)
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual({"results": [{'calls': {},
                                   'ew_pair': 3,
                                   'ew_score': 75,
                                   'ns_pair': 2,
                                   'ns_score': 25}]}, response_dict)

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
    params = {'name': 'name', 'no_pairs': 8, 'no_boards': 24,
              'players': [{'pair_no': 2, 'name': "My name", 'email': "My email"},
                          {'pair_no': 7}],
              'allow_score_overwrites': True}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']
    self.assertIsNotNone(id)
    return id

  def AddLockableTournament(self):
    params = {'name': 'name', 'no_pairs': 8, 'no_boards': 24,
              'players': [{'pair_no': 2, 'name': "My name", 'email': "My email"},
                          {'pair_no': 7}],
              'allow_score_overwrites': False}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']
    self.assertIsNotNone(id)
    return id

  def AddBasicHand(self, id):
    self.loginUser()
    params = {'calls': {}, 'ns_score': 75, 'ew_score': 25}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params)
    self.assertEqual(response.status_int, 204)
