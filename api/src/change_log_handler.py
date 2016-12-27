import webapp2
import json

from google.appengine.api import users
from handler_utils import CheckUserLoggedInAndMaybeReturnStatus
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import CheckValidHandParametersMaybeSetStatus
from handler_utils import CheckValidMatchupForMovementAndMaybeSetStatus
from handler_utils import CheckValidMovementConfigAndMaybeSetStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from models import ChangeLog
from models import HandScore

class ChangeLogHandler(webapp2.RequestHandler):
  ''' Handles requests to /api/tournament/:id/hands/changelog/:hand_no/:ns_pair/:ew_pair.
      Returnes the complete change log for a hand for users with access.
  '''

  def get(self, id, board_no, ns_pair, ew_pair):
    ''' Returns the complete change log for a hand to tournament owners.
    ''' 
    user = users.get_current_user()
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return

    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return
    
    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
                                                       user.user_id(),
                                                       tourney, id):
      return
    
    if not CheckValidHandParametersMaybeSetStatus(self.response, tourney,
        board_no, ns_pair, ew_pair):
      return

    movements = CheckValidMovementConfigAndMaybeSetStatus(
        self.response, tourney.no_pairs, tourney.no_boards)
    if not CheckValidMatchupForMovementAndMaybeSetStatus(
        self.response, movements, int(board_no), int(ns_pair), int(ew_pair)):
     return

    change_logs = ChangeLog._query(
        ancestor=HandScore.CreateKey(tourney, board_no, ns_pair, ew_pair)).order(
            -ChangeLog.key).fetch()

    change_dict = { 'changes' : [] }
    for cl in change_logs:
      change_dict['changes'].append(cl.to_dict())

    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(json.dumps(change_dict, indent=2))
