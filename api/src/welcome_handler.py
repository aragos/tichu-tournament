import webapp2
import json

from generic_handler import GenericHandler
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import SetErrorStatus
from models import Tournament
from models import PlayerPair

class WelcomeHandler(GenericHandler):
  ''' Handles reuqests to /api/tournament/:id/welcome. Responsible for emailing
      players with their player codes.
  '''

  @ndb.toplevel
  def post(self, id):
    ''' Sends an email for all email addresses in the request.
    Checks that emails belong to players in the tournament and sends the email
    only to valid addresses.

    Args: 
      id: tournament ID to look up. Tournament must already have been
          created.
    '''
    user = users.get_current_user()
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return
    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response, user,
                                                       tourney):
      return

    request_dict = self._ParseRequestAndMaybeSetStatus()
    if not request_dict:
      return
    self._SendEmails(request_dict, user, tourney)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(201)

  def _SendEmails(self, request_dict, user, tourney):
    '''Sends a welcome email for all email addresses in the request_dict.

    Args: 
      request_dict: Parsed JSON dict.
      user: The ndb.User owning this tournament.
      tourney: The tournament model object. 
    ''' 
    player_pairs = PlayerPair._query(ancestor=tourney.key).fetch()
    requested_emails = request_dict["emails"]
    for player_pair in player_pairs:
      for player in player_pair.player_list():
        if player.get("email") not in requested_emails:
          continue
        player_name = player.get("name")
        player_greeting = "Dear {},".format(player_name) if player_name else "Greetings!"
        email_text = """{} 
\nWelcome to Tichu tournament \"{}\". Your pair's ID is {}.
You can use it to view and enter your results on
http://tichu-tournament.appspot.com. 
\nGood Luck!
\nYour friendly neighborhood tournament director""".format(
                player_greeting, tourney.name, player_pair.id)
        mail.send_mail(
            sender=user.email(),
            to=player["email"],
            subject="Your Tichu Tournament Pair Code",
            body=email_text,
            reply_to=user.email())


  def _ParseRequestAndMaybeSetStatus(self): 
    ''' Parses the client request for email sents an error status if the
        request is unreadable or the email list is empty. 

    Returns: dict corresponding to the parsed request.s
    ''' 
    try:
      request_dict = json.loads(self.request.body)
    except ValueError:
      SetErrorStatus(self.response, 500, "Invalid Input",
                     "Unable to parse request body as JSON object")
      return None
    request_dict["emails"] = [e for e in request_dict["emails"] if e and e != ""]
    if len(request_dict["emails"]) == 0:
      SetErrorStatus(self.response, 400, "Invalid Input",
                     "No emails specified.")
      return None
    return request_dict