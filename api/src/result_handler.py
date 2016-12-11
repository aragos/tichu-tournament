import webapp2
import json

from python.calculator import Calculate
from python.calculator import GetMaxRounds
from google.appengine.api import users
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import CheckUserLoggedInAndMaybeReturnStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import is_int
from handler_utils import SetErrorStatus
from handler_utils import TourneyDoesNotExistStatus
from python.jsonio import ReadJSONInput
from python.jsonio import OutputJSON
from python.xlsxio import WriteResultsToXlsx
from python.xlsxio import OutputWorkbookAsBytesIO


class ResultHandler(webapp2.RequestHandler):
  def get(self, id):
    user = users.get_current_user()
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return

    if not is_int(id):
      TourneyDoesNotExistStatus(self.response, id)
      return

    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if (not tourney.hands) or (not tourney.owner_id):
      SetErrorStatus(self.response, 500, "Invalid tournament data",
                     "Tournament data is corrupted. Sorry.")
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
                                                       user.user_id(), tourney,
                                                       id):
      return

    boards = ReadJSONInput(tourney.hands)
    summaries = Calculate(boards, GetMaxRounds(boards))
    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(OutputJSON(json.loads(tourney.hands), summaries))


class XlxsResultHandler(webapp2.RequestHandler):
  def get(self, id):
    user = users.get_current_user()
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return

    if not is_int(id):
      TourneyDoesNotExistStatus(self.response, id)
      return

    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if (not tourney.hands) or (not tourney.owner_id):
      SetErrorStatus(self.response, 500, "Invalid tournament data",
                     "Tournament data is corrupted. Sorry.")
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
                                                       user.user_id(), tourney,
                                                       id):
      return

    boards = ReadJSONInput(tourney.hands)
    max_rounds = GetMaxRounds(boards)
    summaries = Calculate(boards, max_rounds)
    mp_summaries = summaries
    ap_summaries = summaries
    boards.sort(key=lambda bs : bs._board_no, reverse = False)
    wb = WriteResultsToXlsx(max_rounds, mp_summaries, ap_summaries, boards)
    self.response.out.write(OutputWorkbookAsBytesIO(wb).getvalue())
    self.response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    self.response.headers['Content-disposition'] = str('attachment; filename=' + 
        json.loads(tourney.metadata)["name"] + 'TournamentResults.xlsx')
    self.response.headers['Content-Transfer-Encoding'] = 'Binary'
    self.response.set_status(200)

