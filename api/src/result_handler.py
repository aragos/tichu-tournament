import webapp2
import json

from python.calculator import Calculate
from python.calculator import GetMaxRounds
from google.appengine.api import users
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import CheckUserLoggedInAndMaybeReturnStatus
from handler_utils import GetHandListForTourney
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import is_int
from handler_utils import SetErrorStatus
from handler_utils import TourneyDoesNotExistStatus
from python.jsonio import ReadJSONInput
from python.jsonio import OutputJSON
from python.xlsxio import WriteResultsToXlsx
from python.xlsxio import OutputWorkbookAsBytesIO
from models import PlayerPair
from models import Tournament


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

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
                                                       user.user_id(), tourney,
                                                       id):
      return
    hand_list = GetHandListForTourney(tourney)
    boards = ReadJSONInput(hand_list)
    summaries = Calculate(boards, GetMaxRounds(boards))
    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(OutputJSON(hand_list, summaries))


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
 
    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
                                                       user.user_id(), tourney,
                                                       id):
      return
    
    boards = ReadJSONInput(GetHandListForTourney(tourney))
    max_rounds = GetMaxRounds(boards)
    summaries = Calculate(boards, max_rounds)
    mp_summaries = summaries
    ap_summaries = summaries
    boards.sort(key=lambda bs : bs._board_no, reverse = False)
    wb = WriteResultsToXlsx(max_rounds, mp_summaries, ap_summaries, boards,
                            name_list=self._GetPlayerListForTourney(tourney))
    self.response.out.write(OutputWorkbookAsBytesIO(wb).getvalue())
    self.response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    self.response.headers['Content-disposition'] = str('attachment; filename=' + 
        tourney.name + 'TournamentResults.xlsx')
    self.response.headers['Content-Transfer-Encoding'] = 'Binary'
    self.response.set_status(200)


  def _GetPlayerListForTourney(self, tourney):
    name_list = range(1, tourney.no_pairs + 1)
    for player_pair in PlayerPair.query(ancestor=tourney.key).fetch():
      if player_pair.players:
        player_list = json.loads(player_pair.players)
        name_list[player_pair.pair_no - 1] = (player_list[0].get("name"),
                                          player_list[1].get("name"))
      else:
        name_list[player_pair.pair_no - 1] = (None, None)
    return name_list

