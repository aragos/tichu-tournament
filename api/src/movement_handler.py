import webapp2
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from handler_utils import CheckUserLoggedInAndMaybeReturnStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import is_int
from handler_utils import SetErrorStatus
from handler_utils import UserNotLoggedInStatus
from models import Tournament
from models import PlayerPair
from models import HandScore
from movements import Movement
from movements import NumBoardsPerRoundFromTotal


class MovementHandler(webapp2.RequestHandler):
  def get(self, id, pair_no):
    ''' Returns pair movement if the reqiest contains a header with the correct
        string id corresponding to this pair_no in the tournament with this id.

        Args: 
          id: tournament ID to look up. Tournament must already have been
              created.
          pair_no: number of the pair to look up.
              
    ''' 
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return
    
    if not self._CheckValidHandParametersMaybeSetStatus(tourney, pair_no):
      return

    player_pairs = PlayerPair.query(ndb.GenericProperty('pair_no') == 
        int(pair_no), ancestor=tourney.key).fetch()
    if not player_pairs:
      SetErrorStatus(self.response, 404, 
                     "Player pair {} not in tournament".format(pair_no))
      return

    if not self._CheckUserAllowedToSeeMovementMaybeSetStatus(
        tourney, pair_no, player_pairs[0]):
      return

    movement = Movement(
        tourney.no_pairs,
        NumBoardsPerRoundFromTotal(tourney.no_pairs,
                                   tourney.no_boards)).GetMovement(int(pair_no))
    for hand in movement:
      if hand['position'][1] == "N":
        hand_score = HandScore.CreateKey(tourney, hand['round'], int(pair_no), hand['opponent']).get()
      else:
        hand_score = HandScore.CreateKey(tourney, hand['round'], hand['opponent'], int(pair_no)).get()
      if hand_score:
        hand['calls'] = json.loads(hand_score.calls)
        hand['ns_score'] = hand_score.ns_score
        hand['ew_score'] = hand_score.ew_score
        hand['notes'] = hand_score.notes

    combined_dict = {
      'name' : tourney.name,
      'players' : player_pairs[0].players,
      'movement': movement
    }

    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(json.dumps(combined_dict, indent=2))

  def _CheckValidHandParametersMaybeSetStatus(self, tourney, pair_no):
    error = "Invalid Input"
    if (not is_int(pair_no)) or int(pair_no) < 1 or int(pair_no) > tourney.no_pairs:
      SetErrorStatus(self.response, 404, error,
                     "Pair number {} is invalid".format(pair_no))
      return False
    return True

  def _CheckUserAllowedToSeeMovementMaybeSetStatus(self, tourney, pair_no, player_pair):
    error  = "Forbidden User"
    user = users.get_current_user()
    if user and tourney.owner_id == user.user_id():
      return True
    pair_id = self.request.headers.get('X-tichu-pair-code')
    if not pair_id:
      SetErrorStatus(self.response, 403, error,
                     "User does not own tournament and is not authenticated with" + 
                     "a pair code to see this movement")
      return False
    if pair_id != player_pair.id:
      SetErrorStatus(self.response, 403, error,
                     "User does not own tournament and is authenticated with the " + 
                     "wrong code for pair {}".format(pair_no))
      return False
    return True