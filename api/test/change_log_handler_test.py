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

  def testGetChangeLogs_bad_id(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.AddBasicHand(id)
    response = self.testapp.get("/api/tournaments/{}a/hands/changelog/1/2/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)

  def testGetChangeLogs_bad_parameters(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.AddBasicHand(id)
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/1a/2/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/0/2/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/25/2/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/1/2a/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/1/0/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/1/9/3".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/1/2/3a".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/1/2/0".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/1/2/9".format(id),
                                 expect_errors=True)
    self.assertEqual(response.status_int, 404)


  def testGetChangeLogs_not_logged_in(self):
    self.loginUser()
    id = self.AddBasicTournament()
    self.logoutUser()
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/1/2/3".format(id),
                                expect_errors=True)
    self.assertEqual(response.status_int, 401)
    
  def testGetChangeLogs_does_not_own(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}/pairids/2".format(id))
    # Even correct headers should not reveal changelogs to nondirectors.
    opaque_id = json.loads(response.body)['pair_id']
    hand_headers = {'X-tichu-pair-code' : str(opaque_id)}
    self.loginUser('user2@example.com', '234')
    params = {'calls': {}, 'ns_score': 25, 'ew_score': 75}
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/1/2/3".format(id),
                                headers=hand_headers, 
                                expect_errors=True)
    self.assertEqual(response.status_int, 403)

  def testGetChangeLogs_invalid_config(self):
    self.loginUser()
    id = self.AddBasicTournament()
    params = {'calls': { 'north': "T" }, 
              'ns_score': 75,
              'ew_score': 25,
              'notes': 'I am a note'}
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/4/2/3".format(id),
                                     params, expect_errors=True)
    self.assertEqual(response.status_int, 400)
                                    


  def testGetChangeLogs(self):
    self.loginUser()
    id = self.AddBasicTournament()
    response = self.testapp.get("/api/tournaments/{}/pairids/2".format(id))
    pair_2_id = json.loads(response.body)['pair_id']
    response = self.testapp.get("/api/tournaments/{}/pairids/3".format(id))
    pair_3_id = json.loads(response.body)['pair_id']
    
    # First hand put in by the director
    params = {'calls': { 'north': "T" }, 
              'ns_score': 75,
              'ew_score': 25,
              'notes': 'I am a note'}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params)
    self.assertEqual(response.status_int, 204)
    
    # Then changed by Pair 2
    self.logoutUser()
    hand_headers = {'X-tichu-pair-code' : str(pair_2_id)}
    params = {'calls': { 'south': "T" }, 
              'ns_score': 85,
              'ew_score': 115,
              'notes': 'I am another note'}
    self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                          headers=hand_headers, params=params)
    
    # Then deleted by the director
    self.loginUser()
    self.testapp.delete("/api/tournaments/{}/hands/1/2/3".format(id))
    
    # Then readded by Pair 3
    self.logoutUser()
    hand_headers = {'X-tichu-pair-code' : str(pair_3_id)}
    params = {'ns_score': 80,
              'ew_score': 20,
              'notes': 'I am a third note'}
    self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                          headers=hand_headers, params=params)
    
    
    # Test the changelog
    self.loginUser()
    response = self.testapp.get("/api/tournaments/{}/hands/changelog/1/2/3".format(id))
    change_list = json.loads(response.body)['changes']
    self.assertEqual(4, len(change_list), msg=change_list)
    
    first_change_log = change_list[3]
    first_score_change = first_change_log['change']
    self.assertEqual( { 'north': "T" }, first_score_change['calls'])
    self.assertEqual(75, first_score_change['ns_score'])
    self.assertEqual(25,first_score_change['ew_score'])
    self.assertEqual('I am a note', first_score_change['notes'])
    self.assertEqual(0, first_change_log['changed_by'])
    
    second_change_log = change_list[2]
    second_score_change = second_change_log['change']
    self.assertEqual( { 'south': "T" }, second_score_change['calls'])
    self.assertEqual(85, second_score_change['ns_score'])
    self.assertEqual(115,second_score_change['ew_score'])
    self.assertEqual('I am another note', second_score_change['notes'])
    self.assertEqual(2, second_change_log['changed_by'])
    
    third_change_log = change_list[1]
    third_score_change = third_change_log['change']
    self.assertIsNone(third_score_change.get('calls'))
    self.assertIsNone(third_score_change.get('ns_score'))
    self.assertIsNone(third_score_change.get('ew_score'))
    self.assertIsNone(third_score_change.get('notes'))
    self.assertEqual(0, third_change_log['changed_by'])
    
    fourth_change_log = change_list[0]
    fourth_score_change = fourth_change_log['change']
    self.assertEqual( { }, fourth_score_change['calls'])
    self.assertEqual(80, fourth_score_change['ns_score'])
    self.assertEqual(20,fourth_score_change['ew_score'])
    self.assertEqual('I am a third note', fourth_score_change['notes'])
    self.assertEqual(3, fourth_change_log['changed_by'])
    
    


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
    self.loginUser()
    params = {'calls': {}, 'ns_score': 75, 'ew_score': 25}
    response = self.testapp.put_json("/api/tournaments/{}/hands/1/2/3".format(id),
                                     params)
    self.assertEqual(response.status_int, 204)
    
  def GetHandFromList(self, hand_list, board_no):
    for hand in hand_list:
      if hand.get('board_no') == board_no:
        return hand
    return None
