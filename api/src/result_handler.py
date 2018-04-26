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

def GetPlayerListForTourney(tourney):
  ''' Returns a list of tuples of names for every pair.'''
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

class CompleteScoringHandler(GenericHandler):
  ''' Handles calls to /api/tournament/:id/handStatus '''
  
  def get(self, id):
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
        users.get_current_user(), tourney):
      return
    
    movement = BuildMovementAndMaybeSetStatus(
        self.response, tourney.no_pairs, tourney.no_boards,
        tourney.legacy_version_id)
    if not movement:
      return

    name_list= GetPlayerListForTourney(tourney)
    scored_hands = self._TuplesToDict(tourney.ScoredHands())
    unscored_hands = []
    round_list = []
    for round_no in xrange (1, movement.GetNumRounds() + 1):
      round_dict = {}
      round_dict["round"] = round_no
      round_dict["scored_hands"] = []
      round_dict["unscored_hands"] = []
      for team_no in xrange(1, tourney.no_pairs + 1):
        round = movement.GetMovement(team_no)[round_no - 1]
        hands = round.hands
        if not hands or not round.is_north:
          continue
        for hand in hands:
          hand_dict = {"hand" : hand, "ns_pair": team_no, 
                       "ns_names": list(name_list[team_no - 1]),
                       "ew_pair" : round.opponent,
                       "ew_names": list(name_list[round.opponent - 1]),
                       "table" : round.table }
          if hand in scored_hands.get(team_no, []):
            scored_unscored = "scored_hands" 
          else: 
            scored_unscored = "unscored_hands"
          round_dict[scored_unscored].append(hand_dict)
      round_dict["scored_hands"].sort(key=lambda x : x["table"])
      round_dict["unscored_hands"].sort(key=lambda x : x["table"])
      round_dict["scored_hands"].sort(key=lambda x : x["hand"])
      round_dict["unscored_hands"].sort(key=lambda x : x["hand"])
      round_list.append(round_dict)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(json.dumps({"rounds" : round_list }, indent=2))

  def _TuplesToDict(self, hands):
    ''' Take tuples representing each hand and dump them into a per-pair dict.

    Args:
      hands: list of tuples (hand, ns_pair, ew_pair).

    Returns:
      Dictionary from team to list of hand numbers already played.
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
                            name_list=GetPlayerListForTourney(tourney))
    self.response.out.write(OutputWorkbookAsBytesIO(wb).getvalue())
    self.response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    self.response.headers['Content-disposition'] = str('attachment; filename=' + 
        tourney.name + 'TournamentResults.xlsx')
    self.response.headers['Content-Transfer-Encoding'] = 'Binary'
    self.response.set_status(200)


