import webapp2
import json

from generic_handler import GenericHandler
from google.appengine.api import users
from google.appengine.ext import ndb
from handler_utils import AVG_VALUES
from handler_utils import BuildMovementAndMaybeSetStatus
from handler_utils import CheckUserLoggedInAndMaybeReturnStatus
from handler_utils import CheckValidHandPlayersCombinationAndMaybeSetStatus
from handler_utils import is_int
from handler_utils import SetErrorStatus
from handler_utils import ValidateHandResultMaybeSetStatus
from models import Tournament
from models import PlayerPair
from python import boardgenerator


class TourneyListHandler(GenericHandler):
  def get(self):
    user = users.get_current_user()
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return

    # TODO: Implement paging if ever needed.
    tourneys = Tournament._query(Tournament.owner_id == 
        user.user_id()).fetch(projection=[Tournament.name])
    tourney_list =  [{"id": str(t.key.id()), "name": t.name} for t in tourneys]
    self.response.set_status(200)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({"tournaments": tourney_list}, indent=2))

  @ndb.toplevel
  def post(self):
    user = users.get_current_user()
    request_dict = self._ValidateNewTournamentInfoAndMaybeSetStatus(user)
    if not request_dict:
      return

    name = request_dict['name']
    no_pairs = request_dict['no_pairs']
    no_boards = request_dict['no_boards']
    player_list = request_dict.get('players')
    allow_score_overwrites = request_dict.get('allow_score_overwrites', False)

    tourney = Tournament.CreateAndPersist(owner_id=user.user_id(),
                                          name=name,
                                          no_pairs=no_pairs,
                                          no_boards=no_boards,
                                          boards=boardgenerator.GenerateBoards(35))
    tourney.PutPlayers(player_list, 0)

    if allow_score_overwrites:
      tourney.Unlock()
    else:
      tourney.MakeLockable()
    self.response.set_status(201)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({"id": str(tourney.key.id())}))


  @ndb.toplevel
  def put(self):
    ''' Creates a new tournament with all the preexisting hands based on the 
        the parameters specified in the request.
    '''
    user = users.get_current_user()
    new_tournament_dict = self._ValidateNewTournamentInfoAndMaybeSetStatus(user)
    if not new_tournament_dict:
      return

    name = new_tournament_dict['name']
    no_pairs = new_tournament_dict['no_pairs']
    no_boards = new_tournament_dict['no_boards']
    player_list = new_tournament_dict.get('players')
    allow_score_overwrites = new_tournament_dict.get('allow_score_overwrites',
                                                     False)

    tourney = Tournament.CreateAndPersist(owner_id=user.user_id(),
                                          name = name,
                                          no_pairs=no_pairs,
                                          no_boards=no_boards,
                                          boards=boardgenerator.GenerateBoards(35))
    tourney.PutPlayers(player_list, 0)

    if allow_score_overwrites:
      tourney.Unlock()
    else:
      tourney.MakeLockable()

    hands_list = self._ParseHandsFromRequestAndMaybeSetStatus()
    if hands_list is None:
      return

    for hand in hands_list:
      board_no = hand.get("board_no")
      ns_pair = hand.get("ns_pair")
      ew_pair = hand.get("ew_pair")
      if not CheckValidHandPlayersCombinationAndMaybeSetStatus(
         self.response, tourney, int(board_no), int(ns_pair), int(ew_pair)):
        return
      calls = hand.setdefault("calls", {})
      ns_score = hand.get("ns_score")
      ew_score = hand.get("ew_score")
      notes = hand.get("notes")
      if not ValidateHandResultMaybeSetStatus(self.response, int(board_no),
                                              int(ns_pair), int(ew_pair),
                                              ns_score, ew_score, calls):
        return
      tourney.PutHandScore(int(board_no), int(ns_pair), int(ew_pair), calls,
                           ns_score, ew_score, notes, 0)

    self.response.set_status(201)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({"id": str(tourney.key.id())}))


  def _ParseTournamentInfoFromRequestAndMaybeSetStatus(self):
    ''' Parses the body of the request. Checks if the body is valid JSON with
    all the proper fields set. Checks if the number of boards and number of 
    pairs are valid numbers. If not sets the response with the appropriate
    status and error message.

    Returns:
      Dict version of the request. If an the request or its memebrs were invalid
      returns None.
    '''
    try:
      request_dict = json.loads(self.request.body)
    except ValueError:
      SetErrorStatus(self.response, 500, "Invalid Input",
                     "Unable to parse request body as JSON object")
      return None
    if not isinstance(request_dict.get('no_pairs'), int):
      SetErrorStatus(self.response, 400, "Invalid Input",
                     "no_pairs must be an integer")
      return None
    elif not isinstance(request_dict.get('no_boards'), int):
      SetErrorStatus(self.response, 400, "Invalid Input",
                     "no_boards must be an integer")
      return None
    elif request_dict.get('players'):
      player_list = request_dict.get('players')
      for player in player_list:
        if not player['pair_no']:
          SetErrorStatus(self.response, 400, "Invalid Input",
                         "Player must have corresponding pair number if present.")
          return None
        if not isinstance(player['pair_no'], int):
          SetErrorStatus(self.response, 400, "Invalid Input",
                         "Player pair number must be an integer, was {}".format(
                             player['pair_no']))
          return None
    return request_dict

  def _ParseHandsFromRequestAndMaybeSetStatus(self):
    ''' Parses the hands from the body of the request. Checks if the body is
    valid JSON with all the proper fields set. Checks if each hand has valid
    scores. If not sets the response with the appropriate status and error
    message.

    Returns:
      List of hand dicts. If the request or its memebrs were invalid returns
      None.
    '''
    try:
      request_dict = json.loads(self.request.body)
    except ValueError:
      SetErrorStatus(self.response, 500, "Invalid Input",
                     "Unable to parse request body as JSON object")
      return None
    for hand in request_dict.get("hands", []):
      ns_score = hand.get('ns_score')
      ew_score = hand.get('ew_score')
      if not isinstance(ns_score, int):
        if not isinstance(ns_score, basestring):
          SetErrorStatus(self.response, 400, "Invalid Input", 
                         "ns_score must be int or string, was " + 
                         type(ns_score).__name__)
          return None
        if ns_score.strip().upper() not in AVG_VALUES:
          SetErrorStatus(self.response, 400, "Invalid Input",
                         "ns_score must be an integer or avg, was " + 
                         str(ns_score))
          return None
        if isinstance(ew_score, int):
          SetErrorStatus(self.response, 400, "Invalid Input",
                         "Cannot have one team with an avg score and another "
                         "with a real Tichu value ")
          return None
      if not isinstance(ew_score, int):
        if not isinstance(ew_score, basestring):
          SetErrorStatus(self.response, 400, "Invalid Input", 
                         "ew_score must be int or string, was " + 
                         type(ew_score).__name__)
          return None
        if ew_score.strip().upper() not in AVG_VALUES:
          SetErrorStatus(self.response, 400, "Invalid Input",
                         "ew_score must be an integer or avg, was " + 
                         str(ew_score))
          return None
        if isinstance(ns_score, int):
          SetErrorStatus(self.response, 400, "Invalid Input",
                         "Cannot have one team with an avg score and another "
                         "with a real Tichu value")
          return None
    return request_dict.get("hands", [])


  def _CheckValidTournamentInfoAndMaybeSetStatus(self, name, no_pairs,
                                                 no_boards, players=None):
    ''' Checks if the input is valid and sane. 
        If not sets the response with the appropriate status and error message.
        Assumes no_pairs and no_boards are integers.
    '''
    if name == "":
      SetErrorStatus(self.response, 400, "Invalid input",
                     "Tournament name must be nonempty")
      return False
    elif no_pairs < 2:
      SetErrorStatus(self.response, 400, "Invalid input",
                     "Number of pairs must be > 1, was {}".format(no_pairs))
      return False
    elif no_boards < 1:
      SetErrorStatus(self.response, 400, "Invalid input",
                     "Number of boards must be > 0, was {}".format(no_boards))
      return False
    elif players:
      for player in players:
        if player['pair_no'] < 1 or player['pair_no'] > no_pairs:
          SetErrorStatus(self.response, 400, "Invalid Input",
                         "Player pair must be between 1 and no_pairs, was {}.".format(
                             player['pair_no']))
          return False
    return BuildMovementAndMaybeSetStatus(
        self.response, no_pairs, no_boards) is not None


  def _ValidateNewTournamentInfoAndMaybeSetStatus(self, user):
    ''' Check basic request information to see if a new tournament can be
    created.
 
    Returns:
      Dict with tournament information.
    
    '''
    if not CheckUserLoggedInAndMaybeReturnStatus(self.response, user):
      return None

    request_dict = self._ParseTournamentInfoFromRequestAndMaybeSetStatus()
    if not request_dict:
      return None

    if not self._CheckValidTournamentInfoAndMaybeSetStatus(
        request_dict['name'], request_dict['no_pairs'],
        request_dict['no_boards'], request_dict.get('players')):
      return None
    return request_dict
