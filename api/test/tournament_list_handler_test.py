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
    response = self.testapp.post_json("/api/tournaments", params,
                                      expect_errors=True)
    self.assertEqual(response.status_int, 401)

  def testCreateTournament_empty_name(self):
    self.loginUser()
    params = {'name': '', 'no_pairs': 8, 'no_boards': 24}
    response = self.testapp.post_json("/api/tournaments", params,
                                      expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testCreateTournament_bad_num_pairs(self):
    self.loginUser()
    params = {'name': 'name1', 'no_pairs': '8a', 'no_boards': 24}
    response = self.testapp.post_json("/api/tournaments", params,
                                      expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testCreateTournament_bad_num_boards(self):
    self.loginUser()
    params = {'name': 'name1', 'no_pairs': 8, 'no_boards': '24b'}
    response = self.testapp.post_json("/api/tournaments", params,
                                      expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testCreateTournament_invalid_num_boards(self):
    self.loginUser()
    params = {'name': 'name1', 'no_pairs': 8, 'no_boards': '-1'}
    response = self.testapp.post_json("/api/tournaments", params,
                                      expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': 'name1', 'no_pairs': 8}
    response = self.testapp.post_json("/api/tournaments", params,
                                      expect_errors=True)
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

  def testCreateTournament_lock_state_lockable(self):
    self.loginUser()
    params = {'name': 'name', 'no_pairs': 8, 'no_boards': 24, 
              'allow_score_overwrites': True}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']

  def testCreateTournament_lock_state_unlocked(self):
    self.loginUser()
    params = {'name': 'name', 'no_pairs': 8, 'no_boards': 24, 
              'allow_score_overwrites': False}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']

  def testPutTournament_unauthorized(self):
    params = {'name': 'name', 
              'no_pairs': 8,
              'no_boards': 24, 
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 401)

  def testPutTournament_empty_name(self):
    self.loginUser()
    params = {'name': "", 
              'no_pairs': 8,
              'no_boards': 24, 
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testPutTournament_bad_num_pairs(self):
    self.loginUser()
    params = {'name': "Name", 
              'no_pairs': '8a',
              'no_boards': 24, 
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testPutTournament_bad_num_boards(self):
    self.loginUser()
    params = {'name': "Name", 
              'no_pairs': 8,
              'no_boards': '24a', 
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testPutTournament_invalid_num_boards(self):
    self.loginUser()
    params = {'name': "Name", 
              'no_pairs': 8,
              'no_boards': -1, 
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': "Name", 
              'no_pairs': 8,
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': "Name", 
              'no_pairs': 8,
              'no_boards': '-1', 
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testPutTournament_invalid_num_pairs(self):
    self.loginUser()
    params = {'name': "Name", 
              'no_pairs': -1,
              'no_boards': 24, 
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': "Name", 
              'no_boards': 24,
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'name': "Name", 
              'no_boards': 24,
              'no_pairs': '-1', 
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testPutTournament_invalid_config(self):
    self.loginUser()
    params = {'name': "Name", 
              'no_pairs': 8,
              'no_boards': 21, 
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testPutTournamnet_invalid_scoring(self):
    self.loginUser()
    hand = {"board_no": 1,
            "ns_pair": 2,
            "ew_pair": 3,
            "calls": {
              "north": "T",
              "east": "GT",
              "west": "",
              "south": ""},
            "ns_score": 20,
            "ew_score": 75,
            "notes": "hahahahahaha what a fool"}
    params = {'name': "Name", 
              'no_pairs': 8,
              'no_boards': 24, 
              'allow_score_overwrites': True,
              'hands': [hand]}
    response = self.testapp.put_json("/api/tournaments",
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params["hands"][0]["ew_score"] = 80
    params["hands"][0]["calls"]["north"] = "G"
    response = self.testapp.put_json("/api/tournaments",
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testPutTournament_null_calls(self):
    self.loginUser()
    hand = {"board_no": 1,
            "ns_pair": 2,
            "ew_pair": 3,
            "ns_score": 25,
            "ew_score": 75,
            "notes": "hahahahahaha what a fool"}
    params = {'name': "Name", 
              'no_pairs': 8,
              'no_boards': 24, 
              'allow_score_overwrites': True,
              'hands': [hand]}
    response = self.testapp.put_json("/api/tournaments", params)
    self.assertEqual(response.status_int, 201)

  def testPutTournament_no_hands(self):
    self.loginUser()
    params = {'name': "Name", 
              'no_pairs': 8,
              'no_boards': 24, 
              'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params)
    self.assertEqual(response.status_int, 201)

  def testPutTournament_avg_calls(self):
    self.loginUser()
    hand = {"board_no": 1,
            "ns_pair": 2,
            "ew_pair": 3,
            "ns_score": "Avg+",
            "ew_score": "aVg",
            'calls': { 'north': "T" },
            "notes": "hahahahahaha what a fool"}
    params = {'name': "Name", 
              'no_pairs': 8,
              'no_boards': 24, 
              'allow_score_overwrites': True,
              'hands': [hand]}
    response = self.testapp.put_json("/api/tournaments/",
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params["hands"][0]["calls"]["north"] = ""
    response = self.testapp.put_json("/api/tournaments", params)
    self.assertEqual(response.status_int, 201)

  def testPutTournament_simple(self):
    self.loginUser()
    params = {'name': 'name', 
              'no_pairs': 8,
              'no_boards': 24, 
              'players': [{
                'pair_no': 1,
                'name': "Michael the Magnificent",
               }],
              "pair_ids": ["ABCD", "DEFG", "HIJK"],
              'hands': [{
                'board_no': 1,
                'ns_pair': 2,
                'ew_pair': 3,
                'calls': {
                  'north': "T",
                  'east': "GT",
                  'west': "",
                  'south': ""
                },
                'ns_score': 150,
                'ew_score': -150,
                'notes': "hahahahahaha what a fool"
              }],
            'allow_score_overwrites': True}
    response = self.testapp.put_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    self.assertEqual(response.status_int, 201)
    id = response_dict['id']
    response = self.testapp.get("/api/tournaments/{}".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    params['pair_ids'] = None
    response_dict['pair_ids'] = None
    self.assertEqual(response_dict, params)

  def testPutTournament_full(self):
    self.loginUser()
    params = json.loads(open(os.path.join(os.getcwd(), 
                        'api/test/example_tournament.txt')).read())
    params["allow_score_overwrites"] = False
    response = self.testapp.put_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    self.assertEqual(response.status_int, 201)
    id = response_dict['id']
    response = self.testapp.get("/api/tournaments/{}".format(id))
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    params['pair_ids'] = None
    response_dict['pair_ids'] = None
    self.assertEqual(len(response_dict['hands']), len(params['hands']))
    self.assertEqual(response_dict['no_boards'], 21)
    self.assertEqual(response_dict['no_pairs'], 7)
    self.assertEqual(response_dict['name'], 'Tournament Name')

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
    self.assertEqual(id, tourneys_list[0]['id'])

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

