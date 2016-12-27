import json

from google.appengine.ext import ndb
from models import Tournament
from models import HandScore
from movements import Movement
from movements import NumBoardsPerRoundFromTotal


def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def CheckValidMovementConfigAndMaybeSetStatus(response, no_pairs, no_boards):
  # Check if a valid movement exists for this pair/board combination.
  no_hands_per_round, no_rounds = NumBoardsPerRoundFromTotal(no_pairs,
                                                             no_boards)
  try:
    movements = Movement(no_pairs, no_hands_per_round, no_rounds)
  except ValueError:
    SetErrorStatus(response, 400, 
                   "No valid configuration {} pairs and {} boards".format(
                       no_pairs, no_boards))
    return None
  return movements
  
  
def CheckValidMatchupForMovementAndMaybeSetStatus(response, movements, board_no,
                                                  ns_pair, ew_pair):
  error = "Invalid Hand-Players Combination"
  detail = "NS and EW pairs do not play each other in this tournament format"
  if not movements:
    SetErrorStatus(response, 400, error, detail)
    return
  for round in movements.GetMovement(ns_pair):
    if round['opponent'] != ew_pair:
      continue
    if round['position'][1] != "N":
      SetErrorStatus(response, 400, error, detail)
      return False
    if not board_no in round['hands']:
      SetErrorStatus(response, 400, error, detail)
      return False
    return True
  SetErrorStatusSetErrorStatus(response, 400, error, detail)
  return False
    
def CheckValidHandParametersMaybeSetStatus(response, tourney,
                                           board_no, ns_pair, ew_pair):
    error = "Invalid Hand Parameters"
    if (not is_int(board_no)) or int(board_no) < 1 or int(board_no) > tourney.no_boards:
      SetErrorStatus(response, 404, error,
                     "Board number {} is invalid".format(board_no))
      return False
    elif (not is_int(ns_pair)) or int(ns_pair) < 1 or int(ns_pair) > tourney.no_pairs:
      SetErrorStatus(response, 404, error,
                     "Pair number {} is invalid".format(ns_pair))
      return False
    elif (not is_int(ew_pair)) or int(ew_pair) < 1 or int(ew_pair) > tourney.no_pairs:
      SetErrorStatus(response, 404, error,
                     "Pair number {} is invalid".format(ew_pair))
      return False
    elif ew_pair == ns_pair:
      SetErrorStatus(response, 404, error, "NS and EW pairs are the same")
      return False
    return True

def CheckUserLoggedInAndMaybeReturnStatus(response, user=None):
  if not user:
    UserNotLoggedInStatus(response)
    return False
  else:
    return True


def UserNotLoggedInStatus(response, debug=True):
  SetErrorStatus(response, 401, "User is not logged in.",
                 "Seriously, not logged in, not even a little.")


def CheckUserOwnsTournamentAndMaybeReturnStatus(response, user_id, tourney, id):
  if tourney.owner_id != user_id:
    DoesNotOwnTournamentStatus(response, id)
    return False
  else:
    return True


def DoesNotOwnTournamentStatus(response, id, debug=True):
  SetErrorStatus(response, 403, "Forbidden User",
                 "User is not director of tournament with id {}".format(id))


def GetTourneyWithIdAndMaybeReturnStatus(response, id):
  if not is_int(id):
    TourneyDoesNotExistStatus(response, id)
    return
  tourney = Tournament.get_by_id(int(id));
  if not tourney:
    TourneyDoesNotExistStatus(response, id)
    return
  return tourney


def TourneyDoesNotExistStatus(response, id, debug=True):
  SetErrorStatus(response, 404, "Invalid tournament ID",
                 "Tournament with id {} does not exit".format(id))


def GetHandListForTourney(tourney):
  hand_list = []
  for hand_score in HandScore.query(ancestor=tourney.key).fetch():
    if hand_score.deleted:
      continue
    split_key = hand_score.key.id().split(":")
    hand_list.append(
        {'calls': json.loads(hand_score.calls),
         'board_no': int(split_key[0]),
         'ns_pair': int(split_key[1]), 
         'ew_pair': int(split_key[2]),
         'ns_score': hand_score.ns_score,
         'ew_score': hand_score.ew_score,
         'notes': hand_score.notes})
  return hand_list


def SetErrorStatus(response, status, error=None, detail=None):
  response.set_status(status)
  if error and detail:
    response.headers['Content-Type'] = 'application/json'
    error_message = {"error": error, "detail": detail}
    response.out.write(json.dumps(error_message))
