import json
import unittest
import webtest
import os

from google.appengine.ext import testbed


from api.src import main


class PairIdHandlerTest(unittest.TestCase):
  def setUp(self):
    os.environ['AUTH_DOMAIN'] = 'testbed'

    self.testbed = testbed.Testbed()
    self.testbed.activate()

    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

    self.testapp = webtest.TestApp(main.app)

  def tearDown(self):
    self.testbed.deactivate()

  def testGetPairId_not_logged_in(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(id, 1),
                                expect_errors=True)
    self.assertEqual(response.status_int, 401)
    
  def testGetPairId_not_owner(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.loginUser('user2@example.com', '234')
    response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(id, 1),
                                expect_errors=True)
    self.assertEqual(response.status_int, 403)

  def testGetPairId_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}a/pairids/{}".format(id, 1),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)
    
  def testGetPairId_bad_pair_no(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}a/pairids/{}a".format(id, 1),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(id, 11),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(id, 0),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testGetPairId(self):
    self.loginUser()
    id = self.AddBasicTournament()
    seen_ids = set()
    for i in range(10):
      response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(
          id, i + 1))
      self.assertEqual(response.status_int, 200)
      pair_id = json.loads(response.body)['pair_id']
      self.assertEqual(4, len(pair_id), 
                       msg="Pair {} has invalid pair id".format(i + 1))
      self.assertTrue(pair_id.isalpha(), 
                      msg="Pair {} has invalid pair id".format(i + 1))
      seen_ids.add(pair_id)
    self.assertEqual(10, len(seen_ids), msg="Duplicated IDS for same tournament")


  def testGetPairIds_not_logged_in(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    response = self.testapp.get("/api/tournaments/{}/pairids".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 401)
    
  def testGetPairIds_not_owner(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.loginUser('user2@example.com', '234')
    response = self.testapp.get("/api/tournaments/{}/pairids/".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 403)

  def testGetPairIds_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}a/pairids/".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testGetPairIds(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}/pairids/".format(id))
    self.assertEqual(response.status_int, 200)
    id_list = json.loads(response.body)['pair_ids']
    seen_ids = set(id_list)
    self.assertEqual(10, len(seen_ids))
    for i in range(10):
      response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(
          id, i + 1))
      self.assertEqual(response.status_int, 200)
      pair_id = json.loads(response.body)['pair_id']
      self.assertEqual(4, len(id_list[i]),
                       msg="Pair {} has invalid pair id".format(i + 1))
      self.assertTrue(id_list[i].isalpha(),
                      msg="Pair {} has invalid pair id".format(i + 1))
      self.assertEqual(pair_id, id_list[i], 
                       msg="Pair {} has two different ids in the list get " + 
                           "format and single id get.".format(i+1))
    
    
  def testGetTourneyInfo_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/pairno/{}".format(id, "CBDG"),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)
    
  def testGetTourneyInfo(self):
    self.loginUser()
    id = str(self.AddBasicTournament())
    response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(id, 5))
    tourney1_pair5_id = json.loads(response.body)["pair_id"]
    response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(id, 8))
    tourney1_pair8_id = json.loads(response.body)["pair_id"]
    id2 = str(self.AddBasicTournament())
    response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(id2, 5))
    tourney2_pair5_id = json.loads(response.body)["pair_id"]
    self.logoutUser()
    response = self.testapp.get("/api/tournaments/pairno/{}".format(tourney1_pair5_id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual(1, len(response_dict["tournament_infos"]))
    self.assertEqual(5, response_dict["tournament_infos"][0]["pair_no"])
    self.assertEqual(id, response_dict["tournament_infos"][0]["tournament_id"])
    
    response = self.testapp.get("/api/tournaments/pairno/{}".format(tourney1_pair8_id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual(1, len(response_dict["tournament_infos"]))
    self.assertEqual(8, response_dict["tournament_infos"][0]["pair_no"])
    self.assertEqual(id, response_dict["tournament_infos"][0]["tournament_id"])
    
    response = self.testapp.get("/api/tournaments/pairno/{}".format(tourney2_pair5_id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual(1, len(response_dict["tournament_infos"]))
    self.assertEqual(5, response_dict["tournament_infos"][0]["pair_no"])
    self.assertEqual(id2, response_dict["tournament_infos"][0]["tournament_id"])

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

  def AddBasicTournament(self):
    params = {'name': 'name', 'no_pairs': 10, 'no_boards': 24,
              'players': [{'pair_no': 2, 'name': "My name", 'email': "My email"},
                          {'pair_no': 8}]}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']
    self.assertIsNotNone(id)
    return id
    
