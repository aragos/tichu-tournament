import json

from google.appengine.ext import ndb
from models import Tournament
from models import HandScore
from movements import Movement


def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def CheckValidHandPlayersCombinationAndMaybeSetStatus(response, tourney,
    board_no, ns_pair, ew_pair):
  ''' Test if the input board number and player pairs are valid in this tourney.
   
  Args:
    response: Response.
    tourney: Tournament. Existing tournament that is used to check config 
      validity.
    board_no: String. String representation of hand number.
    ns_pair: String. String representation of pair number of team playing
      North/South.
    ew_pair: String. String representation of pair number of team playing
      East/West.

  Side effects:
    Sets response to status 400 with a detailed error if either the inputs are
      invalid or the proposed players do not play this board against each other
      in this tournament.

  Returns:
    True iff the Hand/Player Pairs combination is legal in this tourney.
  '''
  # First basic sanity checks on inputs.
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

  # Now check if they make sense in this tournament setup.
  movements = BuildMovementAndMaybeSetStatus(response, tourney.no_pairs,
                                             tourney.no_boards)
  if not movements:
    SetErrorStatus(response, 400, error, detail)
    return False
  return CheckValidMatchupForMovementAndMaybeSetStatus(response, movements,
      int(board_no), int(ns_pair), int(ew_pair))

def BuildMovementAndMaybeSetStatus(response, no_pairs, no_boards):
  ''' Build a unique valid Movement for this tourney.
   
  Args:
    response: Response.
    no_pairs: Integer. Number of pairs in the tournament.
    no_boards: Integer. Number of hands in the tournament.

  Side effects:
    Sets response to status 400 with a detailed error if configuration is 
      invalid.

  Returns:
    A valid movement if it is feasible, or None if no such movement exists
    for the configuration of boards and pairs in tourney.
  '''
  # Check if a valid movement exists for this pair/board combination.
  no_hands_per_round, no_rounds = Movement.NumBoardsPerRoundFromTotal(
      no_pairs, no_boards)
  try:
    movements = Movement(no_pairs, no_hands_per_round, no_rounds)
  except ValueError:
    SetErrorStatus(response, 400, "Invalid Tournament Config",
                   "No valid configuration {} pairs and {} boards".format(
                       no_pairs, no_boards))
    return None
  return movements

def CheckValidMatchupForMovementAndMaybeSetStatus(response, movement, board_no,
                                                  ns_pair, ew_pair):
  ''' Test if the ns_pair plays ew_pair for board_no in this movements.
   
  Args:
    response: Response.
    movement: Movement. 
    board_no: Integer. Hand number.
    ns_pair: Integer. Pair number of team playing North/South.
    ew_pair: Integer. Pair number of team playing East/West.

  Side effects:
    Sets response to status 400 with a detailed error if configuration is 
      invalid.

  Returns:
    True iff the Hand/Player Pairs combination is legal in this Movement scheme.
  '''
  error = "Invalid Hand-Players Combination"
  detail = ("NS pair {} and EW pairs {} do not play board {} against each " + 
           "other in this tournament format").format(ns_pair, ew_pair, board_no)
  for round in movement.GetMovement(ns_pair):
    if round['opponent'] != ew_pair:
      continue
    if round['position'][1] != "N":
      SetErrorStatus(response, 400, error, detail)
      return False
    if not board_no in round['hands']:
      SetErrorStatus(response, 400, error, detail)
      return False
    return True

  # There is no round where ns_pair plays ew_pair.
  SetErrorStatus(response, 400, error, detail)
  return False

def CheckUserLoggedInAndMaybeReturnStatus(response, user):
  ''' Test if the user is logged in.
   
  Args:
    response: Response.
     

  Side effects:
    Sets response to status 401 with a detailed error if the user is not logged
      in.

  Returns:
    True iff the user is logged in.
  '''
  if not user:
    SetErrorStatus(response, 401, "User is not logged in.",
                   "Seriously, not logged in, not even a little.")
    return False
  return True

def CheckUserOwnsTournamentAndMaybeReturnStatus(response, user, tourney):
  ''' Test if the user owns this tourney.
   
  Args:
    response: Response.
    user: google.appengine.api.users.User. Maybe None if user is not logged in.
    tourney: Tournament. Tournament whose ownership is being checked.

  Side effects:
    Sets response to status 401 if the user is not logged in and 401 if the user
      does not own the tournament.

  Returns:
    True iff the user owns the tournament.
  '''
  if not CheckUserLoggedInAndMaybeReturnStatus(response, user):
    return False
  if tourney.owner_id != user.user_id():
    SetErrorStatus(response, 403, "Forbidden User",
                   "User is not director of tournament with id {}".format(id))
    return False
  return True

def GetTourneyWithIdAndMaybeReturnStatus(response, id):
  ''' Fetches a tournament with requested id.
   
  Args:
    response: Response.
    id: String. Unique id assigned to the desired tournament.

  Side effects:
    Sets response to status 403 with a detailed error if tournament does not
      exist.

  Returns:
    Tournament corresponding to the id or None if it does not exist.
  '''
  if not is_int(id):
    TourneyDoesNotExistStatus(response, id)
    return None
  tourney = Tournament.get_by_id(int(id));
  if not tourney:
    TourneyDoesNotExistStatus(response, id)
    return None
  return tourney

def TourneyDoesNotExistStatus(response, id, debug=True):
  SetErrorStatus(response, 404, "Invalid tournament ID",
                 "Tournament with id {} does not exit".format(id))

def GetPairIdFromRequest(request):
  ''' Get the obfuscated pair id from the request headers if present.

  Args:
    request. Request.

  Returns:
    The 4 character obfuscated pair id from the headers if they are present.
    None otherwise.
  '''
  pair_id = request.headers.get('X-tichu-pair-code')
  return pair_id

def SetErrorStatus(response, status, error=None, detail=None):
  ''' Set an error status on response.

  Args:
    response: Reponse.
    status: Integer. HTTP status for the response.
    error: String. Brief error explanation.
    detail: String. Detailed error explanation.

  Side effects:
    Sets "Content-Type" headers to "application/json" along with the error code
      and message.
  '''
  response.set_status(status)
  if error and detail:
    response.headers['Content-Type'] = 'application/json'
    error_message = {"error": error, "detail": detail}
    response.out.write(json.dumps(error_message))
