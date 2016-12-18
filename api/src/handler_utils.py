from google.appengine.ext import ndb
import json


def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False


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
  tourney_key = ndb.Key("Tournament", int(id))
  tourney = tourney_key.get()
  if not tourney:
    TourneyDoesNotExistStatus(response, id)
    return
  return tourney


def TourneyDoesNotExistStatus(response, id, debug=True):
  SetErrorStatus(response, 404, "Invalid tournament ID",
                 "Tournament with id {} does not exit".format(id))


def SetErrorStatus(response, status, error=None, detail=None):
  response.set_status(status)
  if error and detail:
    response.headers['Content-Type'] = 'application/json'
    error_message = {"error": error, "detail": detail}
    response.out.write(json.dumps(error_message))
