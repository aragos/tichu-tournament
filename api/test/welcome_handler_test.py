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
    
  def testSendWelcome_not_logged_in(self):
    self.loginUser()
    id = self.buildNewTournament()
    self.logoutUser()
    params = {'emails': ["email1@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}/welcomeemail".format(id),
                                 params, expect_errors=True)
    self.assertEqual(response.status_int, 401)

  def testSendWelcome_does_not_own(self):
    self.loginUser()
    id = self.buildNewTournament()
    self.loginUser(email='user2@example.com', id='234')
    params = {'emails': ["email1@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}/welcomeemail".format(id),
                                 params, expect_errors=True)
    self.assertEqual(response.status_int, 403)
    
  def testSendWelcome_bad_id(self):
    self.loginUser()
    id = self.buildNewTournament()
    params = {'emails': ["email1@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}a/welcomeemail".format(id),
                                 params, expect_errors=True)
    self.assertEqual(response.status_int, 404)
    
  def testSendWelcome_no_emails(self):
    self.loginUser()
    id = self.buildNewTournament()
    params = {'emails': []}
    response = self.testapp.post_json("/api/tournaments/{}/welcomeemail".format(id),
                                 params, expect_errors=True)
    self.assertEqual(response.status_int, 400)

  def testSendWelcome_email_not_in_tournament(self):
    self.loginUser()
    id = self.buildNewTournament()
    params = {'emails': ["unknownemail@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}/welcomeemail".format(id),
                                      params)
    self.assertEqual(response.status_int, 201)
    messages = self.mail_stub.get_sent_messages()
    self.assertEqual(len(messages), 0)

  def testSendWelcome(self):
    self.loginUser()
    id = self.buildNewTournament()
    params = {'emails': ["email1@something.com", "email2@something.com", 
                         "email3@something.com"]}
    response = self.testapp.post_json("/api/tournaments/{}/welcomeemail".format(id),
                                 params)
    self.assertEqual(response.status_int, 201)
    messages = sorted(self.mail_stub.get_sent_messages(), key=lambda x: x.to)
    self.assertEqual(len(messages), 3)
    email_text = str(messages[0].body)
    self.assertEqual(messages[0].to, "email1@something.com")
    self.assertEqual(messages[0].reply_to, "user@example.com")
    assert "Dear Name1" in email_text 
    response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(
          id, 1))
    self.assertEqual(response.status_int, 200)
    pair_id = json.loads(response.body)['pair_id'] 
    assert pair_id in email_text
    assert "https://tichu-tournament.appspot.com/home/{}".format(pair_id) in email_text
    email_text = str(messages[1].body)
    self.assertEqual(messages[1].to, "email2@something.com")
    self.assertEqual(messages[1].reply_to, "user@example.com")
    assert "Dear Name2" in email_text 
    assert pair_id in email_text
    assert "https://tichu-tournament.appspot.com/home/{}".format(pair_id) in email_text
    email_text = str(messages[2].body)
    self.assertEqual(messages[2].to, "email3@something.com")
    self.assertEqual(messages[2].reply_to, "user@example.com")
    assert "Dear Name3" in email_text 
    response = self.testapp.get("/api/tournaments/{}/pairids/{}".format(
          id, 2))
    self.assertEqual(response.status_int, 200)
    pair_id = json.loads(response.body)['pair_id'] 
    assert "https://tichu-tournament.appspot.com/home/{}".format(pair_id) in email_text
    assert pair_id in email_text


  def buildNewTournament(self, legacy=False):
    params = {'name' : 'Test Tournament', 'no_pairs': 7, 'no_boards': 21,
              'players': [{'pair_no': 1, 'name': "Name1", 'email': "email1@something.com"},
                          {'pair_no': 1, 'name': "Name2", 'email': "email2@something.com"},
                          {'pair_no': 2, 'name': "Name3", 'email': "email3@something.com"},
                          {'pair_no': 2, 'name': "Name4"},
                          {'pair_no': 6, 'name': "Name5", 'email': "email5@something.com"},
                          {'pair_no': 3}]}
    response = self.testapp.post_json("/api/tournaments", params)
    response_dict = json.loads(response.body)
    return response_dict['id']
