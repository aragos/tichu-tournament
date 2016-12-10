import webapp2
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from handler_utils import CheckUserLoggedInAndMaybeReturnStatus
from handler_utils import is_int
from handler_utils import SetErrorStatus
from handler_utils import UserNotLoggedInStatus
from models import Tournament


class TourneyListHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return

    # TODO: Implement paging if ever needed.
    tourneys = Tournament._query(ndb.GenericProperty('owner_id') == 
        user.user_id()).fetch(100)
    tourney_list =  [{"id": t.key.id(), "name": json.loads(t.metadata)["name"]} 
                     for t in tourneys]
    self.response.set_status(200)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({"tournaments": tourney_list}, indent=2))


  def post(self):
    user = users.get_current_user()
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return

    if not self._CheckValidReuestInfoAndMaybeSetStatus():
      return

    name = self.request.get("name")
    no_pairs = int(self.request.get('no_pairs', default_value=0))
    no_boards = int(self.request.get('no_boards', default_value=0))
    if not self._CheckValidTournamentInfoAndMaybeSetStatus(name, no_pairs,
                                                           no_boards):
      return

    metadata_dict = {"name": name, "no_pairs": no_pairs,
                     "no_boards": no_boards}

    tourney = Tournament(owner_id=user.user_id(),
                         metadata=json.dumps(metadata_dict))
    tourney.put()
    self.response.set_status(201)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({"id": tourney.key.id()}))


  def _CheckValidReuestInfoAndMaybeSetStatus(self):
    ''' Checks if the number of boards and number of pairs are valid numbers.
        If not sets the response with the appropriate status and error message.
    '''
    if not is_int(self.request.get('no_pairs')):
      SetErrorStatus(self.response, 400, "Invalid input",
                     "no_pairs must be an integer")
      return False
    elif not is_int(self.request.get('no_boards')):
      SetErrorStatus(self.response, 400, "Invalid input",
                     "no_boards must be an integer")
      return False
    return True


  def _CheckValidTournamentInfoAndMaybeSetStatus(self, name, no_pairs,
                                                 no_boards):
    ''' Checks if the input is valid and sane. 
        If not sets the response with the appropriate status and error message.
        Assumes no_pairs and no_boards are integers.
    '''
    error_message = {"error": "Invalid input"}
    # TODO: Should enforce uniqueness of names?
    if name == "":
      SetErrorStatus(self.response, 400, "Invalid input",
                     "Tournament name must be nonempty")
      return False
    elif no_pairs < 2:
      SetErrorStatus(self.response, 400, "Invalid input",
                     "Number of pairs must be > 1, was {}".format(no_pairs))
      return False
    elif no_boards < 1:
      SetErrorStatus(self.response, 400, "Invalid input",
                     "Number of boards must be > 0, was {}".format(no_boards))
      return False
    return True
