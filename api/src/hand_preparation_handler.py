import webapp2
import json

from generic_handler import GenericHandler
from google.appengine.api import users
from handler_utils import BuildMovementAndMaybeSetStatus
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from models import Tournament

class HandPreparationHandler(GenericHandler):
  ''' Handles requests to /api/tournament/:id/handprep.
  '''

  def get(self, id):
    ''' Returns tournament and pair number information this pair_id.

    Args: 
      id: tournament ID whose hands are being prepared. Tournament must already
          have been created.

    See api for request and response documentation.
    ''' 
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return
    
    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
        users.get_current_user(), tourney):
      return

    movement = BuildMovementAndMaybeSetStatus(
        self.response, tourney.no_pairs, tourney.no_boards)
    if not movement:
      return

    unplayed_list = []
    for pair_no in range(1, tourney.no_pairs + 1):
      unplayed_list.append({"pair_no" : pair_no,
                            "hands" : movement.GetUnplayedHands(pair_no)})
    suggested_prep_list = []
    for pair_no in range(1, tourney.no_pairs + 1):
      suggested_prep_list.append({"pair_no" : pair_no,
                            "hands" : movement.GetSuggestedHandPrep(pair_no)})

    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(
        json.dumps({"unplayed_hands" : unplayed_list,
                    "preparation" : suggested_prep_list}, indent=2))
