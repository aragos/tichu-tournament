import json
import unittest
import webtest
import os

from google.appengine.ext import ndb
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

  def testGetTournament_not_logged_in(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    response = self.testapp.get("/api/tournaments/{}".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 401)

  def testGetTournament_not_owner(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.loginUser('user2@example.com', '234')
    response = self.testapp.get("/api/tournaments/{}".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 403)

  def testGetTournament_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}a".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testGetTournament(self):
    self.loginUser()
    id1 = self.AddBasicTournament()
    params = {'name': 'name2', 'no_pairs': 9, 'no_boards': 27, 
              'players' : [{ "pair_no": 1, "name": "my name" }]}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id2 = response_dict['id']

    response = self.testapp.get("/api/tournaments/{}".format(id1))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(8, response_dict['no_pairs'])
    self.assertEqual(24, response_dict['no_boards'])
    self.assertEqual(2, len(response_dict['players']))

    response = self.testapp.get("/api/tournaments/{}".format(id2))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual('name2', response_dict['name'])
    self.assertEqual(9, response_dict['no_pairs'])
    self.assertEqual(27, response_dict['no_boards'])
    self.assertEqual(1, response_dict['players'][0]["pair_no"])
    self.assertEqual("my name", response_dict['players'][0]["name"])

  def testPutTournament_not_logged_in(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    params = {'name': 'Name', 'no_pairs': 8, 'no_boards': 24}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 401)
  
  def testPutTournament_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'name': 'name', 'no_pairs': 8, 'no_boards': 24}
    response = self.testapp.put_json("/api/tournaments/{}a".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testPutTournament_not_owner(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.loginUser('user2@example.com', id='234')
    params = {'name': 'name', 'no_pairs': 8, 'no_boards': 24}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 403)
    
  def testPutTournament_empty_name(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'name': '', 'no_pairs': 8, 'no_boards': 24}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testPutTournament_bad_num_pairs(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'name': 'name1', 'no_pairs': '8a', 'no_boards': 24}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testPutTournament_bad_num_boards(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'name': 'name1', 'no_pairs': 8, 'no_boards': '24b'}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testPutTournament_invalid_num_boards(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'name': 'name1', 'no_pairs': 8, 'no_boards': '-1'}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': 'name1', 'no_pairs': 8}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testPutTournament_invalid_num_pairs(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'name': 'name1', 'no_pairs': -1, 'no_boards': '24'}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': 'name1', 'no_pairs': 1, 'no_boards': '24'}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': 'name1', 'no_boards': 24}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testPutTournament_existing_hands(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'ns_score': 75,
              'ew_score': 25}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params)
    self.assertEqual(response.status_int, 204)
    params = {'name': 'name2', 'no_pairs': 9, 'no_boards': 27, 
              'players' : [{ "pair_no": 1, "name": "other name" }]}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    
  def testPutTournament_bad_config(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'name': 'name2', 'no_pairs': 9, 'no_boards': 26, 
              'players' : [{ "pair_no": 1, "name": "other name" }]}
    response = self.testapp.put_json("/api/tournaments/{}".format(id), params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testPutTournament(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'name': 'name2', 'no_pairs': 9, 'no_boards': 27, 
              'players' : [{ "pair_no": 1, "name": "other name" }]}
    self.testapp.put_json("/api/tournaments/{}".format(id), params)
    response = self.testapp.get("/api/tournaments/{}".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual('name2', response_dict['name'])
    self.assertEqual(9, response_dict['no_pairs'])
    self.assertEqual(27, response_dict['no_boards'])
    self.assertEqual(1, len(response_dict['players']))
    self.assertEqual(1, response_dict['players'][0]["pair_no"])
    self.assertEqual("other name", response_dict['players'][0]["name"])
    self.assertEqual(9, len(json.loads(self.testapp.get(
        "/api/tournaments/{}/pairids".format(id)).body)["pair_ids"]))
    
  def testPutTournament_override_num_pairs_fewer(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'name': 'name2', 'no_pairs': 7, 'no_boards': 21, 
              'players' : [{ "pair_no": 2, "name": "other name" }]}
    self.testapp.put_json("/api/tournaments/{}".format(id), params)
    response = self.testapp.get("/api/tournaments/{}".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual('name2', response_dict['name'])
    self.assertEqual(7, response_dict['no_pairs'])
    self.assertEqual(21, response_dict['no_boards'])
    self.assertEqual(1, len(response_dict['players']))
    self.assertEqual(2, response_dict['players'][0]["pair_no"])
    self.assertEqual("other name", response_dict['players'][0]["name"])
    self.assertEqual(7, len(json.loads(self.testapp.get(
        "/api/tournaments/{}/pairids".format(id)).body)["pair_ids"]))
   
    
  def testPutTournament_override_just_names(self):
    self.loginUser()
    id = self.AddBasicTournament()
    original_ids = json.loads(self.testapp.get(
        "/api/tournaments/{}/pairids".format(id)).body)["pair_ids"]
    params = {'name': 'name2', 'no_pairs': 8, 'no_boards': 24, 
              'players' : [{ "pair_no": 2, "name": "other name" }]}
    self.testapp.put_json("/api/tournaments/{}".format(id), params)
    response = self.testapp.get("/api/tournaments/{}".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual('name2', response_dict['name'])
    self.assertEqual(8, response_dict['no_pairs'])
    self.assertEqual(24, response_dict['no_boards'])
    self.assertEqual(1, len(response_dict['players']))
    self.assertEqual(2, response_dict['players'][0]["pair_no"])
    self.assertEqual("other name", response_dict['players'][0]["name"])
    new_ids = json.loads(self.testapp.get(
        "/api/tournaments/{}/pairids".format(id)).body)["pair_ids"]
    self.assertEqual(original_ids, new_ids)

  def testDeleteTournament_not_logged_in(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    response = self.testapp.delete("/api/tournaments/{}".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 401)
  
  def testDeleteTournament_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.delete("/api/tournaments/{}a".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testDeleteTournament_not_owner(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.loginUser('user2@example.com', id='234')
    response = self.testapp.delete("/api/tournaments/{}".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 403)
    
  def testDeleteTournament(self):
    self.loginUser()
    id = self.AddBasicTournament()
    id2 = self.AddBasicTournament()
    self.assertEqual(16, len(ndb.Query(kind = "PlayerPair").fetch()))
    response = self.testapp.delete("/api/tournaments/{}".format(id))
    self.assertEqual(response.status_int, 204)
    response = self.testapp.get("/api/tournaments/{}".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)
    self.assertEqual(8, len(ndb.Query(kind = "PlayerPair").fetch()))
    response = self.testapp.get("/api/tournaments")
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(1, len(tourneys["tournaments"]))
    self.assertEqual(id2, tourneys["tournaments"][0]["id"])
    response = self.testapp.get("/api/tournaments/{}".format(id2),
                                expect_errors=True)
    self.CheckBasicTournamentMetadataUnchanged(json.loads(response.body))
    
  def testDeleteTournament_hands_removed(self):
    self.loginUser()
    id = self.AddBasicTournament()
    id2 = self.AddBasicTournament()
    params = {'calls': {}, 'ns_score': 25, 'ew_score': 75}
    self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id), params)
    params = {'calls': {"south" : "T"}, 'ns_score': 225, 'ew_score': -25}
    self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id2), params)
    
    
    self.assertEqual(2, len(ndb.Query(kind = "HandScore").fetch()))
    response = self.testapp.delete("/api/tournaments/{}".format(id))
    self.assertEqual(response.status_int, 204)
    response = self.testapp.get("/api/tournaments/{}".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)
    self.assertEqual(1, len(ndb.Query(kind = "HandScore").fetch()))
    response = self.testapp.get("/api/tournaments")
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(1, len(tourneys["tournaments"]))
    self.assertEqual(id2, tourneys["tournaments"][0]["id"])
    response = self.testapp.get("/api/tournaments/{}".format(id2),
                                expect_errors=True)
    response_dict = json.loads(response.body)
    self.CheckBasicTournamentMetadataUnchanged(response_dict)
    self.assertEqual({"south" : "T"}, response_dict["hands"][0]['calls'])
    self.assertEqual(225, response_dict["hands"][0]['ns_score'])
    self.assertEqual(-25, response_dict["hands"][0]['ew_score'])
    self.assertEqual(1, response_dict["hands"][0]['board_no'])
    self.assertEqual(2, response_dict["hands"][0]['ns_pair'])
    self.assertEqual(3, response_dict["hands"][0]['ew_pair'])

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
                          {'pair_no': 8}]}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']
    self.assertIsNotNone(id)
    return id
    
  def CheckBasicTournamentMetadataUnchanged(self, response_dict):
    self.assertEqual([{'pair_no': 2, 'name': "My name", 'email': "My email"},
                          {'pair_no': 8}],
                     response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(8, response_dict['no_pairs'])
    self.assertEqual(24, response_dict['no_boards'])

