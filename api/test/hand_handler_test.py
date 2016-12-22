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

  def testHead_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.AddBasicHand(id)
    self.logoutUser()
    response = self.testapp.head("/api/tournaments/{}a/hands/1/2/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testHead_bad_parameters(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.AddBasicHand(id)
    self.logoutUser()
    response = self.testapp.head("/api/tournaments/{}/hands/1a/2/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.head("/api/tournaments/{}/hands/0/2/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.head("/api/tournaments/{}/hands/25/2/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.head("/api/tournaments/{}/hands/1/2a/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.head("/api/tournaments/{}/hands/1/0/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.head("/api/tournaments/{}/hands/1/9/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.head("/api/tournaments/{}/hands/1/2/3a".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.head("/api/tournaments/{}/hands/1/2/0".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.head("/api/tournaments/{}/hands/1/2/9".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testHead_not_present(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.AddBasicHand(id)
    self.logoutUser()
    response = self.testapp.head("/api/tournaments/{}/hands/1/2/3".format(id))
    self.assertEqual(response.status_int, 200)

  def testHead_present(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.AddBasicHand(id)
    self.logoutUser()
    response = self.testapp.head("/api/tournaments/{}/hands/2/2/3".format(id))
    self.assertEqual(response.status_int, 204)

  def testPut_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    params = {'calls': {}, 'ns_score': 75, 'ew_score': 25}
    response = self.testapp.put_json("/api/tournaments/{}a/hands/1/2/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testPut_bad_parameters(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    params = {'calls': {}, 'ns_score': 75, 'ew_score': 25}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1a/2/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.put_json("/api/tournaments/{}/hands/0/2/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.put_json("/api/tournaments/{}/hands/25/2/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2a/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/0/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/25/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3a".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/0".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/35".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    
  def testPut_invalid_scoring(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    params = {'calls': {}, 'ns_score': 75, 'ew_score': 20}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'calls': {'north': 'G' }, 'ns_score': 75, 'ew_score': 25}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'calls': {'north': "T" }, 'ns_score': 60, 'ew_score': 40}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
    params = {'calls': {'north': "T" }, 'ns_score': -30, 'ew_score': 130}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testPut_score_exists_not_logged_in(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    params = {'calls': {}, 'ns_score': 75, 'ew_score': 25}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params)
    params = {'calls': {}, 'ns_score': 25, 'ew_score': 75}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 403)
    
  def testPut_score_exists_does_not_own(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.loginUser('user2@example.com', '234')
    params = {'calls': {}, 'ns_score': 75, 'ew_score': 25}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params)
    params = {'calls': {}, 'ns_score': 25, 'ew_score': 75}
    hand_headers = {'X-tichu-pair-code' : 'AAAA'}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params, headers=hand_headers,
                                     expect_errors=True)
    self.assertEqual(response.status_int, 403)

  def testPut(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    params = {'calls': { 'north': "T" }, 
              'ns_score': 75,
              'ew_score': 25,
              'notes': 'I am a note'}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params)
    self.assertEqual(response.status_int, 204)
    self.loginUser()
    
    # Test the hand is there
    response = self.testapp.get("/api/tournaments/{}".format(id))
    hand_list = json.loads(response.body)['hands']
    self.assertEqual(1, len(hand_list))
    self.assertEqual( { 'north': "T" }, hand_list[0]['calls'])
    self.assertEqual(75, hand_list[0]['ns_score'])
    self.assertEqual(25, hand_list[0]['ew_score'])
    self.assertEqual('I am a note', hand_list[0]['notes'])
    self.assertEqual(1, hand_list[0]['board_no'])
    self.assertEqual(2, hand_list[0]['ns_pair']) 
    self.assertEqual(3, hand_list[0]['ew_pair']) 

    # Override the hand.
    params = {'calls': {}, 'ns_score': 20, 'ew_score': 80}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params)
    self.assertEqual(response.status_int, 204)
    response = self.testapp.get("/api/tournaments/{}".format(id))
    self.CheckBasicTournamentMetadataUnchanged(json.loads(response.body))
    hand_list = json.loads(response.body)['hands']
    self.assertEqual(1, len(hand_list))
    self.assertEqual({}, hand_list[0]['calls'])
    self.assertEqual(20, hand_list[0]['ns_score'])
    self.assertEqual(80, hand_list[0]['ew_score'])
    self.assertIsNone(hand_list[0].get('notes'))
    self.assertEqual(1, hand_list[0]['board_no'])
    self.assertEqual(2, hand_list[0]['ns_pair']) 
    self.assertEqual(3, hand_list[0]['ew_pair']) 
    
    # Override the hand again but now as a logged out user with the right
    # credentials.
    response = self.testapp.get("/api/tournaments/{}/pairid/2".format(id))
    opaque_id = json.loads(response.body)['pair_id']
    self.logoutUser()
    params = {'calls': {}, 'ns_score': 25, 'ew_score': 75}
    hand_headers = {'X-tichu-pair-code' : str(opaque_id)}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params, headers=hand_headers)
    self.loginUser()
    self.assertEqual(response.status_int, 204)
    response = self.testapp.get("/api/tournaments/{}".format(id))
    self.CheckBasicTournamentMetadataUnchanged(json.loads(response.body))
    hand_list = json.loads(response.body)['hands']
    self.assertEqual(1, len(hand_list))
    self.assertEqual({}, hand_list[0]['calls'])
    self.assertEqual(25, hand_list[0]['ns_score'])
    self.assertEqual(75, hand_list[0]['ew_score'])
    self.assertIsNone(hand_list[0].get('notes'))
    self.assertEqual(1, hand_list[0]['board_no'])
    self.assertEqual(2, hand_list[0]['ns_pair']) 
    self.assertEqual(3, hand_list[0]['ew_pair']) 

    # Add a second hand, check that both hands are set correctly.
    params = {'calls': {'south': "T", 'east': "", 'west': "GT", 'north': ""},
              'ns_score': -75,
              'ew_score': 275}
    response = self.testapp.put_json("/api/tournaments/{}/hands/4/5/6".format(id),
                                     params)
    self.assertEqual(response.status_int, 204)
    response = self.testapp.get("/api/tournaments/{}".format(id))
    self.CheckBasicTournamentMetadataUnchanged(json.loads(response.body))
    hand_list = json.loads(response.body)['hands']
    self.assertEqual(2, len(hand_list))
    first_hand = self.GetHandFromList(hand_list, 1)
    self.assertEqual({}, first_hand['calls'])
    self.assertEqual(25, first_hand['ns_score'])
    self.assertEqual(75, first_hand['ew_score'])
    self.assertIsNone(first_hand.get('notes'))
    self.assertEqual(1, first_hand['board_no'])
    self.assertEqual(2, first_hand['ns_pair']) 
    self.assertEqual(3, first_hand['ew_pair']) 

    second_hand = self.GetHandFromList(hand_list, 4)
    self.assertEqual({'south': "T", 'east': "", 'west': "GT", 'north': ""},
                     second_hand['calls'])
    self.assertEqual(-75, second_hand['ns_score'])
    self.assertEqual(275, second_hand['ew_score'])
    self.assertIsNone(second_hand.get('notes'))
    self.assertEqual(4, second_hand['board_no'])
    self.assertEqual(5, second_hand['ns_pair']) 
    self.assertEqual(6, second_hand['ew_pair']) 


  def testDelete_not_logged_in(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    self.AddBasicHand(id)
    response = self.testapp.delete("/api/tournaments/{}/hands/1/2/3".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 401)


  def testDelete_not_owner(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.AddBasicHand(id)
    self.loginUser('user2@example.com', id='234')
    response = self.testapp.delete("/api/tournaments/{}/hands/1/2/3".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 403)


  def testDelete_bad_parameters(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.AddBasicHand(id)
    response = self.testapp.delete("/api/tournaments/{}a/hands/1a/2/3".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.delete("/api/tournaments/{}/hands/1a/2/3".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.delete("/api/tournaments/{}/hands/0/2/3".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.delete("/api/tournaments/{}/hands/25/2/3".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.delete("/api/tournaments/{}/hands/1/2a/3".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.delete("/api/tournaments/{}/hands/1/0/3".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.delete("/api/tournaments/{}/hands/1/9/3".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.delete("/api/tournaments/{}/hands/1/2/3a".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.delete("/api/tournaments/{}/hands/1/2/0".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.delete("/api/tournaments/{}/hands/1/2/9".format(id),
                                   expect_errors=True)
    self.assertEqual(response.status_int, 404)


  def testDelete(self):
    self.loginUser()
    id = self.AddBasicTournament()
    # Add simple hand.
    self.AddBasicHand(id)
    # Add a second hand to make sure only the first one is deleted.
    params = {'calls': {}, 'ns_score': 25, 'ew_score': 75}
    response = self.testapp.put_json("/api/tournaments/{}/hands/2/2/3".format(id),
                                     params)

    response = self.testapp.delete("/api/tournaments/{}/hands/1/2/3".format(id))
    self.assertEqual(response.status_int, 204)
    response = self.testapp.get("/api/tournaments/{}".format(id))
    hand_list = json.loads(response.body)['hands']
    self.assertEqual(1, len(hand_list))
    self.assertEqual({}, hand_list[0]['calls'])
    self.assertEqual(25, hand_list[0]['ns_score'])
    self.assertEqual(75, hand_list[0]['ew_score'])
    self.assertIsNone(hand_list[0].get('notes'))
    self.assertEqual(2, hand_list[0]['board_no'])
    self.assertEqual(2, hand_list[0]['ns_pair']) 
    self.assertEqual(3, hand_list[0]['ew_pair']) 


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
                          {'pair_no': 7}]}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']
    self.assertIsNotNone(id)
    return id

  def CheckBasicTournamentMetadataUnchanged(self, response_dict):
    self.assertEqual([{'pair_no': 2, 'name': "My name", 'email': "My email"},
                          {'pair_no': 7}],
                     response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(8, response_dict['no_pairs'])
    self.assertEqual(24, response_dict['no_boards'])

  def AddBasicHand(self, id):
    params = {'calls': {}, 'ns_score': 75, 'ew_score': 25}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params)
    self.assertEqual(response.status_int, 204)
    
  def GetHandFromList(self, hand_list, board_no):
    for hand in hand_list:
      if hand.get('board_no') == board_no:
        return hand
    return None
