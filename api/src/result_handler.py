import webapp2
import json

from generic_handler import GenericHandler
from python.calculator import Calculate
from python.calculator import GetMaxRounds
from google.appengine.api import users
from handler_utils import BuildMovementAndMaybeSetStatus
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import SetErrorStatus
from python.jsonio import ReadJSONInput
from python.jsonio import OutputJSON
from python.xlsxio import WriteResultsToXlsx
from python.xlsxio import OutputWorkbookAsBytesIO
from models import PlayerPair
from models import Tournament

class CompleteScoringHandler(GenericHandler):
  ''' Handles calls to /api/tournament/:id/unscoredHands '''
  
  def get(self, id):
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
        users.get_current_user(), tourney):
      return
    
    movement = BuildMovementAndMaybeSetStatus(
        self.response, tourney.no_pairs, tourney.no_boards)
    if not movement:
      return
    scored_hands = self._TuplesToDict(tourney.ScoredHands())
    unscored_hands = []
    for i in xrange(1, tourney.no_pairs + 1):
      for round in movement.GetMovement(i):
        hands = round.get('hands')
        if not hands:
          continue
        for hand in hands:
          position = round.get('position')
          opponent = round.get('opponent')
          if hand not in scored_hands.get(i, []):
            if position[1] == 'N':
              unscored_hands.append({"hand" : hand, "ns_pair": i,
                                     "ew_pair" : opponent})

    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(json.dumps({"unscored_hands" : unscored_hands},
                                       indent=2))

  def _TuplesToDict(self, hands):
    ''' Take tuples representing each hand and dump them into a per-pair dict.

    Args:
      hands: list of tuples (hand, ns_pair, ew_pair).

    Returns:
      Dictionary from user to list of hand numbers already played.
    '''
    ret = {}
    for hand in hands:
      ret.setdefault(hand[1], []).append(hand[0])
      ret.setdefault(hand[2], []).append(hand[0])
    return ret


class ResultHandler(GenericHandler):
  def get(self, id):
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
        users.get_current_user(), tourney):
      return
    hand_list = tourney.GetScoredHandList()
    boards = ReadJSONInput(hand_list)
    summaries = Calculate(boards, GetMaxRounds(boards))
    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(OutputJSON(hand_list, summaries))


class XlxsResultHandler(GenericHandler):
  def get(self, id):
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return
 
    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
        users.get_current_user(), tourney):
      return
    boards = ReadJSONInput(tourney.GetScoredHandList())
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
        player_list = player_pair.player_list()
        if not player_list:
          continue
        elif len(player_list) == 1:
          name_list[player_pair.pair_no - 1] = (player_list[0].get("name"),
                                                None)
        else:
          name_list[player_pair.pair_no - 1] = (player_list[0].get("name"),
                                                player_list[1].get("name"))
      else:
        name_list[player_pair.pair_no - 1] = (None, None)
    return name_list

