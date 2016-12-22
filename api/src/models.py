import json
import random

from google.appengine.ext import ndb

class Tournament(ndb.Model):
  ''' Model for all the information needed to describe a Tournament
     
      Attributes:
        hands: json object describing a list of raw hand records including
               scores and calls. Required.
        owner_id: owner of the tournament. Required.
        name: name of the tournament. Required.
        no_boards: Number of boards in the tournament. Required.
        no_pairs: Number of pairs in the tournament. Required.
  '''
  owner_id = ndb.StringProperty()
  name = ndb.StringProperty()
  no_boards = ndb.IntegerProperty()
  no_pairs = ndb.IntegerProperty()

  def PutPlayers(self, player_list, no_pairs):
    ''' Creates a new PlayerPair Entity corresponding to each player pair for 
        pair numbers 1 ... no_pairs saving any useful information from 
        player_list and puts it into Datastore as a child of this Tournament.
        Also, if this is the no_players has changed, generates a unique 
        (for this tournament) id associated with each pair.

      Args:
        player_list: list of dicts with keys pair_no (req), name (opt), 
          and email (opt)
        no_pairs: the total number of pairs in this tournament. Exactly this many
          PlayerPairs are created today.
    '''
    if not player_list:
      return
      
    pair_dict = {}
    for player in player_list : 
      pair_no = player['pair_no']
      del player['pair_no']
      if pair_dict.get(pair_no):
        pair_dict[pair_no].append(player)
      else:
        pair_dict[pair_no]= [player]

    player_list = PlayerPair.query(ancestor=self.key).fetch()

    # If the number of players doesn't change, we just override some fields
    # in existing pairs. Otherwise, we delete existing pairs and create new 
    # ones.
    override_existing = len(player_list) == no_pairs
    if not override_existing:
      random_ids = self._RandomId(no_pairs)
      ndb.delete_multi([p.key for p in player_list])
    else:
      player_list.sort(key = lambda pp : pp.pair_no)
    
    # The create a PlayerPair and put it into Datastore for each possible
    # number.
    for i in range(1, no_pairs + 1):
      pair_members = pair_dict.get(i) 
      if pair_members:
        if override_existing:
          player_pair = player_list[i-1]
          player_pair.players = json.dumps(pair_members)
        else:
          player_pair = PlayerPair(players=json.dumps(pair_members),
                                   pair_no=i, id=random_ids[i-1],
                                   parent=self.key)
      else: 
        if override_existing:
          player_pair = player_list[i-1]
          player_pair.players = ''
        else:
          player_pair = PlayerPair(players='', pair_no=i, id=random_ids[i-1],
                                   parent=self.key)
      player_pair.put()


  def PutHandScore(self, hand_no, hand_calls, ns_pair, ew_pair, hand_notes,
                   hand_ns_score, hand_ew_score):
    ''' Creates a new HandScore Entity corresponding to this hand and puts it 
        into datastore.

      Args:
        hand_no: Integer. Number of this hand.
        hand_calls: Dict representation of the calls to this hand
        ns_pair: Integer. Number of the North/South pair.
        ew_pair: Integer. Number of the East/West pair.
        hand_notes: String. Notes for the hand.
        hand_ns_score: Integer. Score for the North/South pair.
        hand_ew_score: Integer. Score for the East/West pair.
    '''
    hand_score = HandScore(calls=json.dumps(hand_calls), notes=hand_notes,
                           ns_score=hand_ns_score, ew_score=hand_ew_score)
    hand_score.key = HandScore.CreateKey(self, hand_no, ns_pair, ew_pair)
    hand_score.put()


  def _RandomId(self, num_ids):
    ''' Generates a list of num_ids unique random 4 character capitalized ids.
    '''
    seen = set()
    ret = []
    for i in range(num_ids):
      id = None
      while (not id) or (id in seen):
        id = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for j in range(4))
      seen.add(id)
      ret.append(id)
    return ret


class PlayerPair(ndb.Model):
  ''' Model for all the information about a player pair in a specific tournament.
      Must be a child of some tournament.
     
      Fields:
        players: json object describing a list of players. Should have length
                 at most 2.
        pair_no: the number associated with this pair in this tournament
        id: a 4 character capitalized letter string that identifies this pair.
  '''
  players = ndb.JsonProperty()
  pair_no = ndb.IntegerProperty()
  id = ndb.StringProperty()
  
class HandScore(ndb.Model):
  ''' Model for all the information about a single hand that was played between
      two teams. Must be a child of some tournament. Must be keyed as 
      a concatenation of hand number, ns pair number, and ew pair number.
  '''
  calls = ndb.JsonProperty()
  notes = ndb.TextProperty()
  ns_score = ndb.IntegerProperty()
  ew_score = ndb.IntegerProperty()
  
  @classmethod
  def CreateKey(cls, parent_tourney, hand_no, ns_pair, ew_pair):
    return ndb.Key(cls._get_kind(),
                   cls.CreateKeyId(hand_no, ns_pair, ew_pair), 
                   parent=parent_tourney.key)

  @classmethod
  def CreateKeyId(cls, hand_no, ns_pair, ew_pair):
    return str(hand_no) + ":" + str(ns_pair) + ":" + str(ew_pair)
