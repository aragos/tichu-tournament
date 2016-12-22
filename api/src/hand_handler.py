import webapp2
import json

from python.calculator import HandResult
from python.calculator import Calls
from python.calculator import InvalidCallError
from python.calculator import InvalidScoreError
from google.appengine.api import users
from google.appengine.ext import ndb
from handler_utils import CheckUserLoggedInAndMaybeReturnStatus
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import is_int
from handler_utils import SetErrorStatus
from models import HandScore
from models import PlayerPair
from models import Tournament


class HandHandler(webapp2.RequestHandler):
  def head(self, id, board_no, ns_pair, ew_pair):
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not self._CheckValidHandParametersMaybeSetStatus(
        tourney.no_boards, tourney.no_pairs, board_no,
        ns_pair, ew_pair):
      return

    if HandScore.CreateKey(tourney, board_no, ns_pair, ew_pair).get():
      self.response.set_status(200)
      return 
    self.response.set_status(204)


  def put(self, id, board_no, ns_pair, ew_pair):
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not self._CheckValidHandParametersMaybeSetStatus(
        tourney.no_boards, tourney.no_pairs, board_no,
        ns_pair, ew_pair):
      return

    request_dict = self._ParseRequestInfoAndMaybeSetStatus()
    if not request_dict:
      return
    calls = request_dict.get("calls")
    ns_score = request_dict.get("ns_score")
    ew_score = request_dict.get("ew_score")
    notes = request_dict.get("notes")

    if not self._ValidateHandResultMaybeSetStatus(int(board_no), int(ns_pair),
                                                  int(ew_pair), ns_score,
                                                  ew_score, calls):
      return

    hr_dict = {"board_no": int(board_no),
               "ns_pair": int(ns_pair),
               "ew_pair": int(ew_pair),
               "calls": calls,
               "ns_score": int(ns_score),
               "ew_score": int(ew_score),
               "notes": notes}

    hand_score = HandScore.CreateKey(tourney, board_no, ns_pair, ew_pair).get()
    if not hand_score:
      tourney.PutHandScore(int(board_no), calls, int(ns_pair), int(ew_pair), notes,
                           int(ns_score), int(ew_score))
    else:
      if not self._CheckUserCanOverwriteMaybeSetStatus(tourney, int(ns_pair),
                                                       int(ew_pair)):
        return
      else:
        tourney.PutHandScore(int(board_no), calls, int(ns_pair), int(ew_pair),
                             notes, int(ns_score), int(ew_score))
    self.response.set_status(204)
 
 
  def delete(self, id, board_no, ns_pair, ew_pair):
    user = users.get_current_user()
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return

    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
                                                       user.user_id(), tourney,
                                                       id):
      return

    if not self._CheckValidHandParametersMaybeSetStatus(
        tourney.no_boards, tourney.no_pairs, board_no,
        ns_pair, ew_pair):
      return

    hand_score = HandScore.CreateKey(tourney, board_no, ns_pair, ew_pair).get()
    if not hand_score:
      SetErrorStatus(self.response, 404, "Invalid Request",
                     "Hand not set in tournament")
      return
    hand_score.key.delete()
    self.response.set_status(204) 


  def _CheckValidHandParametersMaybeSetStatus(self, total_boards, total_pairs,
                                              board_no, ns_pair, ew_pair):
    error = "Invalid Hand Parameters"
    if (not is_int(board_no)) or int(board_no) < 1 or int(board_no) > total_boards:
      SetErrorStatus(self.response, 404, error,
                     "Board number {} is invalid".format(board_no))
      return False
    elif (not is_int(ns_pair)) or int(ns_pair) < 1 or int(ns_pair) > total_pairs:
      SetErrorStatus(self.response, 404, error,
                     "Pair number {} is invalid".format(ns_pair))
      return False
    elif (not is_int(ew_pair)) or int(ew_pair) < 1 or int(ew_pair) > total_pairs:
      SetErrorStatus(self.response, 404, error,
                     "Pair number {} is invalid".format(ew_pair))
      return False
    elif ew_pair == ns_pair:
      SetErrorStatus(self.response, 404, error, "NS and EW pairs are the same")
      return False
    return True


  def _ValidateHandResultMaybeSetStatus(self, board_no, ns_pair, ew_pair,
                                        ns_score, ew_score, calls):
    error =  "Invalid Score"
    if (not is_int(ns_score)):
      SetErrorStatus(self.response, 400, error,
                     "NS score {} is invalid".format(ns_score))
      return False
    elif (not is_int(ew_score)):
      SetErrorStatus(self.response, 400, error,
                     "EW score {} is invalid".format(ew_score))
      return False
    else: 
      try:
        HandResult(board_no, ns_pair, ew_pair, int(ns_score),
                   int(ew_score), Calls.FromDict(calls))
      except InvalidScoreError as err:
        SetErrorStatus(self.response, 400, error,
                     "These scores are not a valid Tichu score")
        return False
      except InvalidCallError as err:
        SetErrorStatus(self.response, 400, error,
                      "{} are not valid Tichu calls".format(calls))
        return False
    return True


  def _CheckUserCanOverwriteMaybeSetStatus(self, tourney, ns_pair, ew_pair):
    user = users.get_current_user()
    error = "Forbidden User"
    if user and tourney.owner_id == user.user_id():
      return True
    pair_id = self.request.headers.get('X-tichu-pair-code')
    if not pair_id:
      SetErrorStatus(self.response, 403, error,
                     "User does not own tournament and is not authenticated with" + 
                     "a pair code to overwrite this hand.")
      return False
    player_pairs = PlayerPair.query(
          ndb.OR(PlayerPair.pair_no == int(ns_pair),
                 PlayerPair.pair_no == int(ew_pair)),
          ancestor=tourney.key).fetch(projection=[PlayerPair.id])
    if (not player_pairs) or (pair_id not in [p.id for p in player_pairs]):
      SetErrorStatus(self.response, 403, error,
                     "User does not own tournament and is authenticated with the " + 
                     "wrong code for involved pairs")
      return False
    return True


  def _ParseRequestInfoAndMaybeSetStatus(self):
    ''' Parses the body of the request. Checks if the body is valid JSON with
        all the proper fields set. If not sets the response with the appropriate
        status and error message.
    '''
    try:
      request_dict = json.loads(self.request.body)
    except ValueError:
      SetErrorStatus(self.response, 500, "Invalid Input",
                     "Unable to parse request body as JSON object")
      return None
    if not isinstance(request_dict.get('ns_score'), int):
      SetErrorStatus(self.response, 400, "Invalid Input",
                     "ns_pairs must be an integer")
      return None
    elif not isinstance(request_dict.get('ew_score'), int):
      SetErrorStatus(self.response, 400, "Invalid Input",
                     "ew_boards must be an integer")
      return None
    elif request_dict.get('calls') is None:
      SetErrorStatus(self.response, 400, "Invalid Input",
                     "Calls must be set.")
      return None
    return request_dict
