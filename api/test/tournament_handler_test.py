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
    self.assertFalse('players' in response_dict)

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

  def testPutTournament(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'name': 'name2', 'no_pairs': 9, 'no_boards': 27, 
              'players' : [{ "pair_no": 1, "name": "my name" }]}
    self.testapp.put_json("/api/tournaments/{}".format(id), params, 
                          expect_errors=True)
    response = self.testapp.get("/api/tournaments/{}".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual('name2', response_dict['name'])
    self.assertEqual(9, response_dict['no_pairs'])
    self.assertEqual(27, response_dict['no_boards'])
    self.assertEqual(1, response_dict['players'][0]["pair_no"])
    self.assertEqual("my name", response_dict['players'][0]["name"])

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
    response = self.testapp.delete("/api/tournaments/{}".format(id))
    self.assertEqual(response.status_int, 204)
    response = self.testapp.get("/api/tournaments/{}".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments")
    tourneys = json.loads(response.body)
    self.assertIsNotNone(tourneys["tournaments"])
    self.assertEqual(0, len(tourneys["tournaments"]))

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
    params = {'name': 'name', 'no_pairs': 8, 'no_boards': 24}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']
    self.assertIsNotNone(id)
    return id

