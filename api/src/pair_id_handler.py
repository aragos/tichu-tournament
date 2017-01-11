import webapp2
import json

from generic_handler import GenericHandler
from google.appengine.api import users
from google.appengine.ext import ndb
from handler_utils import BuildMovementAndMaybeSetStatus
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import is_int
from handler_utils import TourneyDoesNotExistStatus
from handler_utils import SetErrorStatus
from models import HandScore
from models import Tournament
from models import PlayerPair

class PairIdHandler(GenericHandler):
  ''' Handles requests to /api/tournament/pairno/:pair_id. Responsible for
      identifying the tournament/pair combination corresponding to an 
      opaque secret pair_id code.
  '''

  def get(self, pair_id):
    ''' Returns tournament and pair number information this pair_id.

        Args: 
          pair_id: Opaque secret ID used to look up information for the user.
    ''' 
    player_pairs = PlayerPair._query(ndb.GenericProperty('id') == 
        pair_id).fetch(projection=[PlayerPair.pair_no])
    if not player_pairs:
      SetErrorStatus(self.response, 404, "Invalid Id",
                     "Pair number with this ID does not exist")
      return
    info_dict = {
      'tournament_infos' : [ {'pair_no' : p.pair_no,
                              'tournament_id' : str(p.key.parent().id()) } for p in player_pairs ]
    }

    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(json.dumps(info_dict, indent=2))


class TourneyPairIdHandler(GenericHandler):
  ''' Handles requests to /api/tournament/:id/pairids/:pair_no. Responsible for
      finding the opaque ID generated for this pair, unique to this tournament.
  '''
  def get(self, id, pair_no):
    ''' Returns the opaque pair ID for pair with pair nubmer pair_no in this
        Tournament.

        Args: 
          id: Tournament ID for this tournament.
          pair_no: The pair number whose ID has to be looked up.
    ''' 
    if not is_int(pair_no):
      SetErrorStatus(self.response, 404, "Invalid Pair Number", 
                    "Pair number must be an integer, was {}".format(pair_no))
      return

    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return
    
    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response, 
        users.get_current_user(), tourney):
      return
    player_pairs = PlayerPair._query(ndb.GenericProperty('pair_no') == 
        int(pair_no), ancestor=tourney.key).fetch(1, projection=[PlayerPair.id])
    if not player_pairs:
      SetErrorStatus(self.response, 404, "Invalid Id",
                     "Pair pair number {} does not exist in this " + 
                         "tournament".format(pair_no))
      return
    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(json.dumps({'pair_id' : player_pairs[0].id}, indent=2))


class TourneyPairIdsHandler(GenericHandler):
  ''' Handles requests to /api/tournament/:id/pairids. Responsible for
      finding the opaque IDs generated for all pairs in this tournament.
  '''
  def get(self, id):
    ''' Returns tournament and pair number information this pair_id.

        Args: 
          id: Tournament ID for this tournament
        Returns: 
          a list of all unique ids in order. Length will necessarily equal
          to the number of pairs in this tournament.
    ''' 
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return
    
    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response,
        users.get_current_user(), tourney):
      return

    player_pairs = PlayerPair._query(ancestor=tourney.key).fetch(
        projection=[PlayerPair.id, PlayerPair.pair_no])
    player_pairs.sort(key = lambda p : p.pair_no)
    if not player_pairs:
      SetErrorStatus(self.response, 500, "Corrupted Data",
                     "Could not find any players for this tournament. " + 
                         "Consider resetting tournament info.")

    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(200)
    self.response.out.write(
        json.dumps({"pair_ids" : [p.id for p in player_pairs]}, indent=2))