import webapp2
import json

from generic_handler import GenericHandler
from google.appengine.api import users
from google.appengine.ext import ndb
from handler_utils import is_int
from handler_utils import GetPairIdFromRequest
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import SetErrorStatus
from models import HandScore
from models import PlayerPair
from models import Tournament
from movements import Movement


class MovementHandler(GenericHandler):
  ''' Class to handle requests to /api/tournaments/:id/movement/:pair_no '''

  def get(self, id, pair_no):
    ''' Fetch movement for tournament with id and team pair_no. 

    Args:
      id: String. Tournament id. 
      pair_no: Integer. Pair number for the team whose movement we're getting.

    See api for request and response documentation.
    '''
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not self._CheckValidPairMaybeSetStatus(tourney, pair_no):
      return

    player_pair = PlayerPair.GetByPairNo(tourney, int(pair_no))
    if not player_pair:
      SetErrorStatus(self.response, 404, "Invalid Request",
                     "Player pair {} not in tournament".format(pair_no))
      return

    if not self._CheckUserAllowedToSeeMovementMaybeSetStatus(
        tourney, player_pair):
      return

    no_hands_per_round, no_rounds = Movement.NumBoardsPerRoundFromTotal(
        tourney.no_pairs, tourney.no_boards)
    try:
      movement = Movement.CreateMovement(
          tourney.no_pairs, no_hands_per_round, no_rounds).GetMovement(
              int(pair_no))
    except ValueError:
      SetErrorStatus(self.response, 500, "Corrupted Data",
                     "No valid movement for this tourney's config")
      return

    movement_list = []
    for round in movement:
      movement_list.append(
          self._GetJsonRoundWithScore(round, tourney, int(pair_no)))

    combined_dict = {
      'name' : tourney.name,
      'players' : player_pair.player_list(),
      'movement': movement_list
    }

    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(json.dumps(combined_dict, indent=2))

  def _GetJsonRoundWithScore(self, round, tourney, pair_no):
    ''' Converts round information to a json interpretable string adding 
    scored hands if any exist.

    Args:
      round: MovementRound. Contains all player/hand information about a specific
        matchup from the point of view of Pair pair_no. 
      tourney: Tournament. Tournament in which this is happening.
      pair_no: Pair from whose point of view this movement is seen.

    Returns:
      Dict as expected by api. Includes any scores that have already been added.
    '''
    hands = round.hands
    round_str = round.to_dict()
    opp = round.opponent
    if opp:
      opp_pp = PlayerPair.GetByPairNo(tourney, opp)
      if opp_pp:
        round_str["opponent_names"] = [x.get("name") for x in
            opp_pp.player_list()]
    if hands:
      del round_str['hands']
    for h in hands:
      if round.is_north:
        hand_score = HandScore.GetByHandParams(tourney, h, pair_no, 
                                               round.opponent)
      else:
        hand_score = HandScore.GetByHandParams(tourney, h, round.opponent,
                                               pair_no)
      if hand_score:
        round_str.setdefault('hands', []).append({
          'hand_no' : h,
          'score': {
              'calls' : hand_score.calls_dict(),
              'ns_score' : hand_score.get_ns_score(),
              'ew_score' : hand_score.get_ew_score(),
              'notes' : hand_score.notes,
        }})
      else:
        round_str.setdefault('hands', []).append({ 'hand_no' : h })
    return round_str

  def _CheckValidPairMaybeSetStatus(self, tourney, pair_no):
    ''' Test if the provided pair number is valid for tourney. 

    Args:
      tourney: Tournament. Tournament the pair number is being validated for.
      pair_no: Integer. Pair number for the team we are validating.
    '''
    error = "Invalid Input"
    if (not is_int(pair_no)) or int(pair_no) < 1 or int(pair_no) > tourney.no_pairs:
      SetErrorStatus(self.response, 404, error,
                     "Pair number {} is invalid".format(pair_no))
      return False
    return True

  def _CheckUserAllowedToSeeMovementMaybeSetStatus(self, tourney, player_pair):
    error  = "Forbidden User"
    user = users.get_current_user()
    if user and tourney.owner_id == user.user_id():
      return True
    pair_id = GetPairIdFromRequest(self.request)
    if not pair_id:
      SetErrorStatus(self.response, 403, error,
                     "User does not own tournament and is not authenticated " +
                     "with a pair code to see this movement")
      return False
    if pair_id != player_pair.id:
      SetErrorStatus(self.response, 403, error,
                     "User does not own tournament and is authenticated with " +
                     "the wrong code for pair {}".format(player_pair.pair_no))
      return False
    return True