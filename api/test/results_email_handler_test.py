import json
import unittest
import webtest
import os
import sys
import test_utils

from google.appengine.api import mail
from google.appengine.ext import testbed
from test_base import AppTestBase
from api.src import main

class AppTest(AppTestBase):
  def setUp(self):
    os.environ['AUTH_DOMAIN'] = 'testbed'

    self.testbed = testbed.Testbed()
    self.testbed.activate()

    self.testbed.init_mail_stub()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    self.testapp = webtest.TestApp(main.app)

  def tearDown(self):
    self.testbed.deactivate()
    
  def testSendResults_not_logged_in(self):
    self.loginUser()
    id = self.buildFullTournament()
    self.logoutUser()
    params = {'emails': ["email1@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}/resultsemail".format(id),
                                 params, expect_errors=True)
    self.assertEqual(response.status_int, 401)

  def testSendResults_does_not_own(self):
    self.loginUser()
    id = self.buildFullTournament()
    self.loginUser(email='user2@example.com', id='234')
    params = {'emails': ["email1@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}/resultsemail".format(id),
                                 params, expect_errors=True)
    self.assertEqual(response.status_int, 403)
    
  def testSendResults_bad_id(self):
    self.loginUser()
    id = self.buildFullTournament()
    params = {'emails': ["email1@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}a/resultsemail".format(id),
                                 params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    
  def testSendResults_no_emails(self):
    self.loginUser()
    id = self.buildFullTournament()
    params = {'emails': []}
    response = self.testapp.post_json("/api/tournaments/{}/resultsemail".format(id),
                                 params, expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testSendResults_not_complete(self):
    self.loginUser()
    id = self.buildFullTournament()
    response = self.testapp.delete("/api/tournaments/{}/hands/1/1/7".format(id))
    self.assertEqual(response.status_int, 204)
    params = {'emails': ["email1@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}/resultsemail".format(id),
                                 params, expect_errors=True)
    messages = self.mail_stub.get_sent_messages()
    self.assertEqual(len(messages), 0)

  def testSendResults_email_not_in_tournament(self):
    self.loginUser(email="director@example.com")
    id = self.buildFullTournament()
    params = {'emails': ["unknownemail@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}/resultsemail".format(id),
                                 params)
    self.assertEqual(response.status_int, 201)
    messages = self.mail_stub.get_sent_messages()
    self.assertEqual(len(messages), 1)
    self.assertEqual(messages[0].to, "director@example.com")
    self.assertEqual(messages[0].reply_to, "director@example.com")
    email_text = str(messages[0].body)
    assert "Awesome Tournament Director" in email_text 
    assert "1. Team 3 (2 Awesome Players)" in email_text
    assert "2. Team 2 (Name3 and Name4)" in email_text
    assert "3. Team 6 (Name5 and an Awesome Partner)" in email_text

  def testSendResults_email_not_in_tournament_director_is_player(self):
    self.loginUser(email="email1@something.com")
    id = self.buildFullTournament()
    params = {'emails': ["unknownemail@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}/resultsemail".format(id),
                                 params)
    self.assertEqual(response.status_int, 201)
    messages = self.mail_stub.get_sent_messages()
    self.assertEqual(len(messages), 0)
    
  def testSendResults_director_is_player(self):
    self.loginUser(email="email1@something.com")
    id = self.buildFullTournament()
    params = {'emails': ["email1@something.com", "email2@something.com", 
                         "email3@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}/resultsemail".format(id),
                                 params)
    self.assertEqual(response.status_int, 201)
    messages = sorted(self.mail_stub.get_sent_messages(), key=lambda x: x.to)
    self.assertEqual(len(messages), 3)
    email_text = str(messages[0].body)
    self.assertEqual(messages[0].to, "email1@something.com")
    self.assertEqual(messages[0].reply_to, "email1@something.com")
    assert "Awesome Tournament Director" not in email_text 
    assert "Hi there Name1" in email_text 
    assert "1. Team 3 (2 Awesome Players)" in email_text
    assert "2. Team 2 (Name3 and Name4)" in email_text
    assert "3. Team 6 (Name5 and an Awesome Partner)" in email_text
    email_text = str(messages[1].body)
    self.assertEqual(messages[1].to, "email2@something.com")
    self.assertEqual(messages[1].reply_to, "email1@something.com")
    assert "Awesome Tournament Director" not in email_text 
    assert "Hi there Name2" in email_text 
    assert "1. Team 3 (2 Awesome Players)" in email_text
    assert "2. Team 2 (Name3 and Name4)" in email_text
    assert "3. Team 6 (Name5 and an Awesome Partner)" in email_text
    email_text = str(messages[2].body)
    self.assertEqual(messages[2].to, "email3@something.com")
    self.assertEqual(messages[2].reply_to, "email1@something.com")
    assert "Awesome Tournament Director" not in email_text 
    assert "Hi there Name3" in email_text 
    assert "1. Team 3 (2 Awesome Players)" in email_text
    assert "2. Team 2 (Name3 and Name4)" in email_text
    assert "3. Team 6 (Name5 and an Awesome Partner)" in email_text

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
      params = {'name' : 'Test Tournament', 'no_pairs': 7, 'no_boards': 21,
                'players': [{'pair_no': 1, 'name': "Name1", 'email': "email1@something.com"},
                            {'pair_no': 1, 'name': "Name2", 'email': "email2@something.com"},
                            {'pair_no': 2, 'name': "Name3", 'email': "email3@something.com"},
                            {'pair_no': 2, 'name': "Name4"},
                            {'pair_no': 6, 'name': "Name5", 'email': "email5@something.com"},
                            {'pair_no': 3}]}
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
