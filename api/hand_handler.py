import webapp2
import json

from python.calculator import HandResult
from python.calculator import Calls
from python.calculator import InvalidCallError
from python.calculator import InvalidScoreError
from google.appengine.api import users
from handler_utils import CheckUserLoggedInAndMaybeReturnStatus
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import is_int
from handler_utils import SetErrorStatus
from handler_utils import TourneyDoesNotExistStatus
from models import Tournament


class HandHandler(webapp2.RequestHandler):
  def head(self, id, board_no, ns_pair, ew_pair):
    if not is_int(id):
      TourneyDoesNotExistStatus(self.response, id)
      return

    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if (not tourney.metadata) or (not tourney.owner_id):
      self.response.set_status(500)
      return

    metadata_dict = json.loads(tourney.metadata)
    hand_list = json.loads(tourney.hands) if tourney.hands else []
    if not self._CheckValidHandParametersMaybeSetStatus(
        metadata_dict["no_boards"], metadata_dict["no_pairs"], board_no,
        ns_pair, ew_pair):
      return

    if not self._is_hand_present(hand_list, int(board_no),
                                 int(ns_pair), int(ew_pair)):
      self.response.set_status(204)
      return
    self.response.set_status(200)


  def put(self, id, board_no, ns_pair, ew_pair):
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    metadata_dict = json.loads(tourney.metadata)
    hand_list = json.loads(tourney.hands) if tourney.hands else []
    if not self._CheckValidHandParametersMaybeSetStatus(
        metadata_dict["no_boards"], metadata_dict["no_pairs"], board_no,
        ns_pair, ew_pair):
      return

    calls_json = self.request.get("calls")
    ns_score = self.request.get("ns_score")
    ew_score = self.request.get("ew_score")
    notes = self.request.get("notes")

    if not self._ValidateHandResultMaybeSetStatus(int(board_no), int(ns_pair),
                                                  int(ew_pair), ns_score,
                                                  ew_score, calls_json):
      return

    hr_dict = {"board_no": int(board_no),
               "ns_pair": int(ns_pair),
               "ew_pair": int(ew_pair),
               "calls": json.loads(calls_json),
               "ns_score": int(ns_score),
               "ew_score": int(ew_score),
               "notes": notes}

    if not self._is_hand_present(hand_list, int(board_no), int(ns_pair),
                                 int(ew_pair)):
      hand_list.append(hr_dict)
    else:
      if not self._CheckUserCanOverwriteMaybeSetStatus(tourney.owner_id):
        return
      else:
        for hand in hand_list:
          if self._is_hand_equal(int(board_no), int(ns_pair), int(ew_pair),
                                 hand):
            hand.update(hr_dict)
            break
    tourney.hands = json.dumps(hand_list)
    tourney.put()
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

    metadata_dict = json.loads(tourney.metadata)
    hand_list = json.loads(tourney.hands) if tourney.hands else []
    if not self._CheckValidHandParametersMaybeSetStatus(
        metadata_dict["no_boards"], metadata_dict["no_pairs"], board_no,
        ns_pair, ew_pair):
      return

    if not self._is_hand_present(hand_list, int(board_no), int(ns_pair),
                                 int(ew_pair)):
      SetErrorStatus(self.response, 404, "Invalid Score",
                     "Hand not set in tournament")
      return

    hand_list = [hand for hand 
                 in hand_list 
                 if not self._is_hand_equal(int(board_no), int(ns_pair),
                                            int(ew_pair), hand)]
    tourney.hands = json.dumps(hand_list)
    tourney.put()
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
                                        ns_score, ew_score, calls_json):
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
                   int(ew_score), Calls.FromJson(calls_json))
      except InvalidScoreError as err:
        SetErrorStatus(self.response, 400, error,
                     "These scores are not a valid Tichu score")
        return False
      except InvalidCallError as err:
        SetErrorStatus(self.response, 400, error,
                      "{} are not valid Tichu calls".format(calls_json))
        return False
    return True


  def _CheckUserCanOverwriteMaybeSetStatus(self, owner_id):
    user = users.get_current_user()
    error = "Forbidden User"
    if not user:
      SetErrorStatus(self.response, 403, error,
                     "User must be logged in to overwrite existing score.")
      return False
    elif user.user_id() != owner_id:
      SetErrorStatus(self.response, 403, error,
                     "Score already exists and user is not director of this tournament")
      return False
    return True


  def _is_hand_present(self, hand_list, board_no, ns_pair, ew_pair):
    return any(self._is_hand_equal(board_no, ns_pair, ew_pair, hand) 
               for hand in hand_list)


  def _is_hand_equal(self, board_no, ns_pair, ew_pair, hand):
    return (hand["board_no"] == board_no and 
            hand["ns_pair"] == ns_pair and 
            hand["ew_pair"] == ew_pair)
