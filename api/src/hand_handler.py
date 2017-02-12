import webapp2
import json

from generic_handler import GenericHandler
from google.appengine.api import users
from google.appengine.ext import ndb
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import CheckValidHandPlayersCombinationAndMaybeSetStatus
from handler_utils import GetPairIdFromRequest
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import SetErrorStatus
from models import HandScore
from models import PlayerPair
from models import Tournament
from python.calculator import HandResult
from python.calculator import Calls
from python.calculator import InvalidCallError
from python.calculator import InvalidScoreError


class HandHandler(GenericHandler):
  ''' Class to handle requests to 
      /api/tournaments/:id/hands/:hand_no/:ns_pair/:ew_pair
  '''
  def head(self, id, board_no, ns_pair, ew_pair):
    ''' Check if a hand with this configuration is present in tournament id. 

    Args:
      id: String. Tournament id. 
      board_no: Integer. Hand number.
      ns_pair: Integer. Pair number of team playing North/South.
      ew_pair: Integer. Pair number of team playing East/West.

    See api for request and response documentation.
    '''
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not CheckValidHandPlayersCombinationAndMaybeSetStatus(
        self.response, tourney, board_no, ns_pair, ew_pair):
      return

    hand_score = HandScore.GetByHandParams(tourney, board_no, ns_pair, ew_pair)
    if hand_score:
      self.response.set_status(200)
      return 
    self.response.set_status(204)

  def put(self, id, board_no, ns_pair, ew_pair):
    ''' Add a scored hand to the tournament with this id. 

    Args:
      id: String. Tournament id. 
      board_no: Integer. Hand number.
      ns_pair: Integer. Pair number of team playing North/South.
      ew_pair: Integer. Pair number of team playing East/West.
    
    See api for request and response documentation.
    '''
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not CheckValidHandPlayersCombinationAndMaybeSetStatus(
        self.response, tourney, board_no, ns_pair, ew_pair):
      return

    request_dict = self._ParsePutRequestInfoAndMaybeSetStatus()
    if not request_dict:
      return
    calls = request_dict.setdefault("calls", {})
    ns_score = request_dict.get("ns_score")
    ew_score = request_dict.get("ew_score")
    notes = request_dict.get("notes")

    if not self._ValidateHandResultMaybeSetStatus(int(board_no), int(ns_pair),
                                                  int(ew_pair), ns_score,
                                                  ew_score, calls):
      return

    user_has_access, change_pair_no = self._CheckUserHasAccessMaybeSetStatus(
        tourney, int(ns_pair), int(ew_pair))
    if not user_has_access:
      return
    else:
      tourney.PutHandScore(int(board_no), int(ns_pair), int(ew_pair), calls,
                           ns_score, ew_score, notes, change_pair_no)
    self.response.set_status(204)

  def delete(self, id, board_no, ns_pair, ew_pair):
    ''' Delete hand with these hand number and opponents from this tournament.

    Args:
      id: String. Tournament id. 
      board_no: Integer. Hand number.
      ns_pair: Integer. Pair number of team playing North/South.
      ew_pair: Integer. Pair number of team playing East/West.
    
    See api for request and response documentation.
    '''
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
        users.get_current_user(), tourney):
      return

    if not CheckValidHandPlayersCombinationAndMaybeSetStatus(
        self.response, tourney, board_no, ns_pair, ew_pair):
      return

    hand_score = HandScore.GetByHandParams(tourney, board_no, ns_pair, ew_pair)
    if not hand_score:
      SetErrorStatus(self.response, 404, "Invalid Request",
                     "Hand {} between pairs {} and {} is not set".format(
                         board_no, ns_pair, ew_pair))
      return
    hand_score.Delete()
    self.response.set_status(204) 

  def _ValidateHandResultMaybeSetStatus(self, board_no, ns_pair, ew_pair,
                                        ns_score, ew_score, calls):
    ''' Validates the proposed hand results as a real Tichu score.

    Args:
      board_no: Integer. Hand number.
      ns_pair: Integer. Pair number of team playing North/South.
      ew_pair: Integer. Pair number of team playing East/West.
      ns_score: Integer or String. Score of the North/South team. If string,
         must be one of AVG, AVG+, AVG++, AVG-, AVG-- allowing for any
         capitalization.
      ew_score: Integer or String. Score of the East/West team. If string,
         must be one of AVG, AVG+, AVG++, AVG-, AVG-- allowing for any
         capitalization.
      calls: Dictionary. Holds calls from each team. Can be None.
    Returns:
      True iff the proposed score is a valid Tichu score.s
    '''
    error =  "Invalid Score"
    try:
      HandResult(board_no, ns_pair, ew_pair, ns_score,
                 ew_score, Calls.FromDict(calls))
    except InvalidScoreError as err:
      SetErrorStatus(self.response, 400, error,
                     "These scores are not a valid Tichu score")
      return False
    except InvalidCallError as err:
      SetErrorStatus(self.response, 400, error,
                     "{} are not valid Tichu calls".format(calls))
      return False
    return True

  def _CheckUserHasAccessMaybeSetStatus(self, tourney, ns_pair, ew_pair):
    ''' Tests if the current user has access to a hand with given players.

    Uses the pair id code, if any, set in the request header to see if the user
    is in one of the teams playing the hand. Directors always have access.

    Args:
      tourney. Tournament. Current tournament.
      ns_pair: Integer. Pair number of team playing North/South.
      ew_pair: Integer. Pair number of team playing East/West.

    Returns:
      A (Boolean, Integer) pair. First member is True iff the user has access
      to the hand between ns_pair and ew_pair. Second member is the pair number
      of the user. Only set if first member is True.
    '''
    user = users.get_current_user()
    error = "Forbidden User"
    if user and tourney.owner_id == user.user_id():
      return (True, 0)
    pair_id = GetPairIdFromRequest(self.request)
    if not pair_id:
      SetErrorStatus(self.response, 403, error,
                     "User does not own tournament and is not authenticated " + 
                     "with a pair code to overwrite this hand.")
      return (False, None)
    player_pairs = PlayerPair.query(
          ndb.OR(PlayerPair.pair_no == int(ns_pair),
                 PlayerPair.pair_no == int(ew_pair)),
          ancestor=tourney.key).fetch()
    if (not player_pairs) or (pair_id not in [p.id for p in player_pairs]):
      SetErrorStatus(self.response, 403, error,
                     "User does not own tournament and is authenticated with " +
                     "the wrong code for involved pairs")
      return (False, None)
    return (True, next(p.pair_no for p in player_pairs if p.id == pair_id))

  def _ParsePutRequestInfoAndMaybeSetStatus(self):
    ''' Parse the body of the request.

    Checks if the body is valid JSON with all the proper fields set. If not,
    sets the response with the appropriate status and error message.

    Returns:
      a dict with all the request parameters if the required parameters are set.
      None if any of the required fields are unset or have the wrong type.
    '''
    try:
      request_dict = json.loads(self.request.body)
    except ValueError:
      SetErrorStatus(self.response, 500, "Invalid Input",
                     "Unable to parse request body as JSON object")
      return None
    ns_score = request_dict.get('ns_score')
    ew_score = request_dict.get('ew_score')
    if not isinstance(ns_score, int):
      if ns_score.strip()[0:3].upper() != "AVG":
        SetErrorStatus(self.response, 400, "Invalid Input",
                       "ns_score must be an integer or avg")
        return None
    elif not isinstance(ew_score, int):
      if ew_score.strip()[0:3].upper() != "AVG":
        SetErrorStatus(self.response, 400, "Invalid Input",
                       "ew_score must be an integer or avg")
      return None
    return request_dict
