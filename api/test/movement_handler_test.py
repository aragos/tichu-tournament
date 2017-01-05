import json
import unittest
import webtest
import os

from api.src import main
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from sets import Set


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


  def testGetMovement_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}a/movement/1".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)


  def testGetMovement_bad_pair(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}/movement/0".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/movement/30".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 404)


  def testGetMovement_owner(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}/movement/1".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual([], response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(6, len(response_dict['movement']))


  def testGetMovement_right_header(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}/pairids/2".format(id))
    opaque_id = json.loads(response.body)['pair_id']
    self.logoutUser()
    
    hand_headers = {'X-tichu-pair-code' : str(opaque_id)}
    response = self.testapp.get("/api/tournaments/{}/movement/2".format(id),
                                headers=hand_headers)
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual([{"email": "My email", "name": "My name"}],
                     response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(6, len(response_dict['movement']))

  def testGetMovement_scores(self):
    self.loginUser()
    id = self.AddBasicTournament()
    # Team 2 is E team 1 is N. Playing hands 13-14 in Round 1.
    params = {'calls': {}, 'ns_score': 20, 'ew_score': 80}
    response = self.testapp.put_json("/api/tournaments/{}/hands/13/1/2".format(id),
                                     params)
    params = {'calls': {}, 'ns_score': 10, 'ew_score': 90}
    response = self.testapp.put_json("/api/tournaments/{}/hands/14/1/2".format(id),
                                     params)
    # Team 2 is N team 7 is E. Playing hand 22 in Round 2.
    params = {'calls': {}, 'ns_score': 100, 'ew_score': 0}
    response = self.testapp.put_json("/api/tournaments/{}/hands/22/2/7".format(id),
                                     params)
    # Team 4 is N team 7 is E. Playing hand 13 in Round 1.
    params = {'calls': {}, 'ns_score': 125, 'ew_score': -25}
    response = self.testapp.put_json("/api/tournaments/{}/hands/13/4/7".format(id),
                                     params)
    
    # Team 5's hand. Add it and then delete it.
    params = {'calls': {}, 'ns_score': 125, 'ew_score': -25}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/5/6".format(id),
                                     params)
    self.testapp.delete("/api/tournaments/{}/hands/1/5/6".format(id))
    
    # Another tournament with same basic parameters. Team two has one different
    # score.
    id2 = self.AddBasicTournament()
    # Team 2 is E team 1 is N. Playing hands 13-15 in Round 1.
    params = {'calls': {'south' : "T"}, 'ns_score': 120, 'ew_score': 80}
    response = self.testapp.put_json("/api/tournaments/{}/hands/13/1/2".format(id2),
                                     params)
    
    response = self.testapp.get("/api/tournaments/{}/pairids/1".format(id))
    opaque_id_team1_tourney1 = json.loads(response.body)['pair_id']
    response = self.testapp.get("/api/tournaments/{}/pairids/2".format(id))
    opaque_id_team2_tourney1 = json.loads(response.body)['pair_id']
    response = self.testapp.get("/api/tournaments/{}/pairids/4".format(id))
    opaque_id_team4_tourney1 = json.loads(response.body)['pair_id']
    response = self.testapp.get("/api/tournaments/{}/pairids/5".format(id))
    opaque_id_team5_tourney1 = json.loads(response.body)['pair_id']
    response = self.testapp.get("/api/tournaments/{}/pairids/6".format(id))
    opaque_id_team6_tourney1 = json.loads(response.body)['pair_id']
    response = self.testapp.get("/api/tournaments/{}/pairids/7".format(id))
    opaque_id_team7_tourney1 = json.loads(response.body)['pair_id']
    response = self.testapp.get("/api/tournaments/{}/pairids/1".format(id2))
    opaque_id_team1_tourney2 = json.loads(response.body)['pair_id']
    response = self.testapp.get("/api/tournaments/{}/pairids/2".format(id2))
    opaque_id_team2_tourney2 = json.loads(response.body)['pair_id']
    
    ##### Output Testing #####
    self.logoutUser()
    # Team 1
    response = self.testapp.get(
        "/api/tournaments/{}/movement/1".format(id),
        headers={'X-tichu-pair-code' : str(opaque_id_team1_tourney1)})
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual([], response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(6, len(response_dict['movement']))
    expected_hands = [
        {"hand_no" : 13, "score"  : { "ns_score" : 20, "calls" : {}, "ew_score" : 80 }},
        {"hand_no" : 14, "score"  : { "ns_score" : 10, "calls" : {}, "ew_score" : 90 }}, 
        {"hand_no" : 15}]
    self.assertHandEquals(response_dict['movement'], 1, expected_hands,
                          "Round 1, Tourney 1, Hands 13-15, Team 1 vs 2")
    self.assertScoresNotPresent(response_dict['movement'],
                                Set([2, 3, 4, 5, 6, 7]), "Team 1")
    
    # Team 2
    response = self.testapp.get(
        "/api/tournaments/{}/movement/2".format(id),
        headers={'X-tichu-pair-code' : str(opaque_id_team2_tourney1)})
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual([{"email": "My email", "name": "My name"}],
                     response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(6, len(response_dict['movement']))
    expected_hands = [
        {"hand_no" : 13, "score"  : { "calls" : {}, "ns_score" : 20, "ew_score" : 80 }},
        {"hand_no" : 14}, {"hand_no" : 15}]
    self.assertHandEquals(response_dict['movement'], 1, expected_hands,
                          "Round 1, Tourney 1, Hands 13-15, Team 2 vs 1")
    expected_hands = [
        {"hand_no" : 22, "score"  : { "calls" : {}, "ns_score" : 100, "ew_score" : 0 }},
        {"hand_no" : 23}, {"hand_no" : 24}]
    self.assertHandEquals(response_dict['movement'], 2, expected_hands,
                          "Round 1, Tourney 1, Hands 22-24, Team 2 vs 7")
    self.assertScoresNotPresent(response_dict['movement'],
                                Set([3, 4, 5, 6, 7]), "Team 2")
    
    # Team 4                            
    response = self.testapp.get(
        "/api/tournaments/{}/movement/4".format(id),
        headers={'X-tichu-pair-code' : str(opaque_id_team4_tourney1)})
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual([], response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(7, len(response_dict['movement']))
    expected_hands = [
        {"hand_no" : 13, "score"  : { "calls" : {}, "ns_score" : 125, "ew_score" : -25 }},
        {"hand_no" : 14}, {"hand_no" : 15}]
    self.assertHandEquals(response_dict['movement'], 1, expected_hands,
                          "Round 1, Tourney 1, Hands 13-15, Team 4 vs 7")
    self.assertScoresNotPresent(response_dict['movement'],
                                Set([3, 4, 5, 6, 7]), "Team 4")
    
    # Team 5                        
    response = self.testapp.get(
        "/api/tournaments/{}/movement/5".format(id),
        headers={'X-tichu-pair-code' : str(opaque_id_team5_tourney1)})
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual([], response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(6, len(response_dict['movement']))
    self.assertScoresNotPresent(response_dict['movement'],
                                Set([1, 2, 3, 4, 5, 6, 7]), "Team 5")
                                

    # Team 7
    response = self.testapp.get(
        "/api/tournaments/{}/movement/7".format(id),
        headers={'X-tichu-pair-code' : str(opaque_id_team7_tourney1)})
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual([], response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(6, len(response_dict['movement']))
    expected_hands = [
        {"hand_no" : 13, "score"  : { "calls" : {}, "ns_score" : 125, "ew_score" : -25 }},
        {"hand_no" : 14}, {"hand_no" : 15}]
    self.assertHandEquals(response_dict['movement'], 1, expected_hands,
                          "Round 1, Tourney 1, Hand 13, Team 7 vs 4")
    expected_hands = [
        {"hand_no" : 22, "score"  : { "calls" : {}, "ns_score" : 100, "ew_score" : 0 }},
        {"hand_no" : 23}, {"hand_no" : 24}]
    self.assertHandEquals(response_dict['movement'], 2, expected_hands,
                          "Round 2 Tourney 1, Hands 22-24, Team 7 vs 2")
    self.assertScoresNotPresent(response_dict['movement'],
                                Set([3, 4, 5, 6, 7]), "Team 7")

    # Team 1 Tourney 2                        
    response = self.testapp.get(
        "/api/tournaments/{}/movement/1".format(id2),
        headers={'X-tichu-pair-code' : str(opaque_id_team1_tourney2)})
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual([], response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(6, len(response_dict['movement']))
    expected_hands = [
        {"hand_no" : 13, "score"  : {"calls" : {'south' : "T"}, "ns_score" : 120, "ew_score" : 80 }},
        {"hand_no" : 14}, {"hand_no" : 15}]
    self.assertHandEquals(response_dict['movement'], 1, expected_hands,
                          "Round 1, Tourney 2, Hand 13, Team 1 vs 2")
    self.assertScoresNotPresent(response_dict['movement'],
                                Set([2, 3, 4, 5, 6, 7]), "Team 1 Tourney 2")
                                
                                
    # Team 2 Tourney 2                        
    response = self.testapp.get(
        "/api/tournaments/{}/movement/2".format(id2),
        headers={'X-tichu-pair-code' : str(opaque_id_team2_tourney2)})
    self.assertEqual(response.status_int, 200)
    response_dict = json.loads(response.body)
    self.assertEqual([{"email": "My email", "name": "My name"}],
                     response_dict['players'])
    self.assertEqual('name', response_dict['name'])
    self.assertEqual(6, len(response_dict['movement']))
    expected_hands = [
        {"hand_no" : 13, "score"  : {"calls" : {'south' : "T"}, "ns_score" : 120, "ew_score" : 80 }},
        {"hand_no" : 14}, {"hand_no" : 15}]
    self.assertHandEquals(response_dict['movement'], 1, expected_hands,
                          "Round 1, Tourney 2, Hand 13, Team 2 vs 1")
    self.assertScoresNotPresent(response_dict['movement'],
                                Set([2, 3, 4, 5, 6, 7]), "Team 2 Tourney 2")

  def assertScoresNotPresent(self, movement, rounds, handmsg=None):
    for hand in movement:
      if hand['round'] in rounds:
        self.assertIsNone(hand.get('score'), 
                          msg="{}: Round {} hand contains an unexpected " + 
                              "score {}".format(handmsg, hand['round'],
                                                hand.get('score')))
    

  def assertHandEquals(self, movement, round, expected_hands, handmsg=None):
    for r in movement:
      if r['round'] != round:
        continue
      hands = r['hands']
      for i in range(3):
        #if not expected_hands[i]:
        #  self.assertiIsNone(hands[i], msg="Expected no score" )
        self.assertEqual(3, len(hands),
                         msg="{}: wrong number of hands. Hands are {}.".format(
                             handmsg, hands))
        self.assertEqual(
             expected_hands[i]['hand_no'], hands[i]['hand_no'],
             msg="{}: hand numbers do not match up. Expected {}, was {}".format(
                 handmsg, expected_hands[i]['hand_no'], hands[i]['hand_no']))
        expected_score = expected_hands[i].get('score')
        if expected_score:
          actual_score = hands[i]['score']
          self.assertEqual(expected_score['calls'], actual_score['calls'],
              msg="{}: Hand {} calls do not match up. Expected {}, was {}".format(
                  handmsg, i, expected_score['calls'], actual_score['calls']))
          self.assertEqual(expected_score['ns_score'], actual_score['ns_score'],
              msg="{}: Hand {} ns_score do not match up. Expected {}, was {}".format(
                  handmsg, i, expected_score['ns_score'], actual_score['ns_score']))
          self.assertEqual(expected_score['ew_score'], actual_score['ew_score'],
              msg="{}: Hand {} calls do not match up. Expected {}, was {}".format(
                  handmsg, i, expected_score['ew_score'], actual_score['ew_score']))
        else: 
          self.assertIsNone(actual_score.get('score'),
                            msg="{}: Did not expect any scores. Got {}.".format(
                                handmsg, actual_score.get('score')))
      return
    self.assertTrue(False,
                    msg="{}: round {} not present in movement".format(handmsg, round))

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
    params = {'name': 'name', 'no_pairs': 10, 'no_boards': 24,
              'players': [{'pair_no': 2, 'name': "My name", 'email': "My email"},
                          {'pair_no': 8}]}
    response = self.testapp.post_json("/api/tournaments", params)
    self.assertNotEqual(response.body, '')
    response_dict = json.loads(response.body)
    id = response_dict['id']
    self.assertIsNotNone(id)
    return id
    
