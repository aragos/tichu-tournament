import webapp2
import json

from generic_handler import GenericHandler
from google.appengine.api import users
from google.appengine.ext import ndb
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import GetPairIdFromRequest
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import is_int
from handler_utils import SetErrorStatus
from models import HandScore
from models import PlayerPair
from python.calculator import Calls
from python.calculator import HandResult
from python.calculator import Board



class HandResultsHandler(GenericHandler):
  ''' Class to handle requests to 
      /api/tournaments/:id/handresults/:hand_no/
  '''
  def get(self, id, board_no):
    '''Gets all the scored results for a particular hand in the tournament.

    Args:
      id: String. Tournament id. 
      board_no: Integer. Hand number.

    See api for request and response documentation.
    '''
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if (not is_int(board_no)) or int(board_no) < 1 or int(board_no) > tourney.no_boards:
      SetErrorStatus(self.response, 404, "Invalid Hand Parameters",
                     "Board number {} is invalid".format(board_no))
      return

    has_access, pair_no, all_matchups = self._CheckUserHasAccessMaybeSetStatus(tourney,
        int(board_no))
    if not has_access:
      return

    position = self.request.headers.get('X-position')
    if not self._CheckValidPositionAndMaybeSetStatus(position):
      return

    scores = self._GetAllPlayedScores(tourney, int(board_no), all_matchups)
    if not self._CheckPlayerScoredHandsAndMaybeSetStatus(pair_no, all_matchups,
                                                         scores):
      return

    list_of_results = self._ScoresToJson(position, scores, all_matchups)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(json.dumps({"results" : list_of_results}, indent=2))


  def _IsNorth(self, position):
    ''' Returns true iff position corresponds to "N".
    
    Args:
     position: String. Either "N" or "E". Raises ValueError otherwise.
    '''
    if position == "N":
      return True
    elif position == "E":
      return False
    raise ValueError("Unknown position " + position)


  def _ScoresToJson(self, position, scores, all_matchups):
    ''' Returns a list of JSON objects that correspond to the API response
        for the get call.

    Args:
      position: String. "N" or "E". ValueError is raised otherwise.
      scores: list of HandScores corresponding to a specific hand.
      all_matchups: List of (Integer, Integer) pairs. All matchups for this
                    board possible in the tournament.
      board_no: Integer. This hand's number.

    See api for full response documentation.
    '''
    list_of_results = []
    hr_list = []
    for i in [k for k in xrange(len(scores)) if scores[k]]:
      ns_pair = all_matchups[i][0]
      ew_pair = all_matchups[i][1]
      calls = scores[i].calls_dict()
      hr_list.append(HandResult(1, ns_pair, ew_pair,
                                scores[i].get_ns_score(),
                                scores[i].get_ew_score(),
                                Calls.FromDict(calls)))
    if len(hr_list) == 0:
      return list_of_results
    board = Board(1, hr_list)
    is_north = self._IsNorth(position)
    for bsl in board.ScoreBoard():
      list_of_results.append({
          'calls' : bsl.hr().calls().ToDict(),
          'ns_score' : bsl.hr().ns_score(),
          'ew_score' : bsl.hr().ew_score(),
          'ns_pair': bsl.hr().ns_pair_no(),
          'ew_pair': bsl.hr().ew_pair_no(),
          'mps': bsl.ns_mps if is_north else bsl.ew_mps,
      })
    list_of_results.sort(key=lambda x : x['mps'], reverse=True)
    return list_of_results


  def _CheckValidPositionAndMaybeSetStatus(self, position):
    '''Returns true if the position is one of allowed positions.

    If not, set an error in the response.

    Args:
      position: String. Position returned by the get header.
    '''
    if position != "N" and position != "E":
      SetErrorStatus(self.response, 404, "Invalid Request", 
                     "Position {} is not valid. Must be one of N or E".format(position))
      return False
    return True


  def _CheckUserHasAccessMaybeSetStatus(self, tourney, hand_no):
    '''Tests if the current user has access to the results of this hand.

    Uses the pair id code, if any, set in the request header to see if the user
    is in one of the teams that is set to play this hand in this movement. 
    Directors always have access.

    Args:
      tourney: Tournament. Current tournament.
      hand_no: Integer. Number of the hand.

    Returns:
      A (Boolean, Integer, [(Integer, Integer)]) tuple. First member is True iff
      the user should have access to the hand provided they played it (or is a
      director). The second member is the pair number of the user (0 for director).
      Only set if first member is True. The last member is the list of 
      (nw_pair, ew_pair) tuples that correspond to the pairs that play hand_no in
      this movement.
    '''
    user = users.get_current_user()
    movement = tourney.GetMovement()
    all_matchups = movement.GetListOfPlayersForHand(hand_no)
    if user and tourney.owner_id == user.user_id():
      return (True, 0, all_matchups)
    if tourney.IsUnlocked():
      SetErrorStatus(self.response, 403, "Forbidden User", 
                     "The tournament is not set up to show hand " +
                     "results to players.")
      return (False, None, None)

    error = "Forbidden User"
    pair_id = GetPairIdFromRequest(self.request)
    player_pairs = PlayerPair._query(ndb.GenericProperty('id') == 
        pair_id).fetch(1, projection=[PlayerPair.pair_no])
    if not pair_id or not player_pairs:
      SetErrorStatus(self.response, 403, error,
                     "User does not own tournament and is not authenticated " + 
                     "with a pair code to see the results of this hand.")
      return (False, None, None)
    pair_no = player_pairs[0].pair_no;
    if not self._PlayerInMatchupList(pair_no, all_matchups):
      SetErrorStatus(self.response, 403, error,
                     "User does not play this hand.")
      return (False, None, None)
    return (True, pair_no, all_matchups)


  def _CheckPlayerScoredHandsAndMaybeSetStatus(self, pair, all_matchups, scores):
    '''Returns true if pair is present in one of the scored matchups

    Directors always return true.
    Args:
      pair: Integer. Pair number we are checking.
      all_matchups: List of (Integer, Integer) pairs. All matchups for this
                    board possible in the tournament.
      scores: List of HandScores. List of all scored hands with their scores.
    '''
    if pair == 0:
      return True

    scored_matchups = []
    for i in xrange(len(scores)):
      if scores[i]:
        scored_matchups.append(all_matchups[i])
    if not self._PlayerInMatchupList(pair, scored_matchups):
      SetErrorStatus(self.response, 403, "Forbidden User",
                     "Pair {} has not yet played this hand.".format(pair))
      return False
    return True


  def _GetAllPlayedScores(self, tourney, board_no, matchups):
     '''Returns all played scores for given matchups for a board.

     Args:
       tourney: Tournament. Parent tournament of the hands.
       board_no: Integer. Number of the hand whose scores we're looking up.
       matchups: List of Integer pairs. Matchups of pairs for a hand.
     Returns:
       HandScores from the matchup set that are already scored.
     '''
     hand_request = []
     for ns_pair, ew_pair in matchups:
       hand_request.append((board_no, ns_pair, ew_pair))
     return HandScore.GetByMultipleHands(tourney, hand_request)


  def _PlayerInMatchupList(self, pair, matchups):
    '''Checks if pair is in the list of matchups.
    
    Args:
      pair: Integer. Pair number.
      matchups: List of Integer pairs. Matchups of pairs for a hand.
    '''
    for p1, p2 in matchups:
      if pair == p1 or pair == p2:
        return True
    return False