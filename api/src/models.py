import datetime
import json
import random
from python import boardgenerator

from google.appengine.ext import ndb


class Tournament(ndb.Model):
  ''' Model for all the information needed to describe a Tournament
     
  Attributes:
    owner_id: Google ID for the owner of the tournament. Required.
    name: name of the tournament. Required.
    no_boards: Number of boards in the tournament. Required.
    no_pairs: Number of pairs in the tournament. Required.
  '''
  owner_id = ndb.StringProperty()
  name = ndb.StringProperty()
  no_boards = ndb.IntegerProperty()
  no_pairs = ndb.IntegerProperty()

  @classmethod
  def CreateAndPersist(cls, boards, **kwargs):
    '''Creates and persists a new tournament with the given properties and
      populates its boards.

    Args:
      boards: List of handgenerator board objects to persist with this
          tournament.
    '''
    tournament = cls(**kwargs)
    tournament.put()
    i = 0
    for board in boards:
      i+=1
      board = Board(board_number=i,
                    board=board.ToJson(),
                    parent=tournament.key)
      board.put()

    return tournament

  def PutPlayers(self, player_list, no_pairs):
    ''' Create a new PlayerPair Entity corresponding to each player pair for 
        pair numbers 1 ... no_pairs saving any useful information from 
        player_list and put it into Datastore as a child of this Tournament.
        Also, the no_players has changed, generates a unique 
        (for this tournament) id associated with each pair.

    Args:
      player_list: list of dicts with keys pair_no (req), name (opt), 
        and email (opt)
      no_pairs: the total number of pairs in this tournament. Exactly this many
        PlayerPairs are created.
    '''
    pair_dict = {}
    if player_list:
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
      str_pair_members = json.dumps(pair_members) if pair_members else ''
      if override_existing:
          player_pair = player_list[i-1]
          player_pair.players = str_pair_members
      else:
        player_pair = PlayerPair(players=str_pair_members,
                                 pair_no=i, id=random_ids[i-1],
                                 parent=self.key)
      player_pair.key = PlayerPair.CreateKey(self, i)
      player_pair.put()

  def PutHandScore(self, hand_no, ns_pair, ew_pair, hand_calls, hand_ns_score,
                   hand_ew_score, hand_notes, changed_by):
    ''' Create a new HandScore Entity corresponding to this hand and put it 
        into datastore.

    Args:
      hand_no: Integer. Number of this hand.
      ns_pair: Integer. Number of the North/South pair.
      ew_pair: Integer. Number of the East/West pair.
      hand_calls: Dict representation of the calls to this hand
      hand_ns_score: Integer. Score for the North/South pair.
      hand_ew_score: Integer. Score for the East/West pair.
      hand_notes: String. Notes for the hand.
      changed_by: Integer. Pair number of the requestor. 0 if director.
    '''
    hand_score = HandScore(calls=json.dumps(hand_calls), notes=hand_notes,
                           ns_score=hand_ns_score, ew_score=hand_ew_score,
                           deleted=False)
    hand_score.key = HandScore.CreateKey(self, hand_no, ns_pair, ew_pair)
    hand_score.PutChangeLog(changed_by)
    hand_score.put()

  def _RandomId(self, num_ids):
    ''' Generate a list of num_ids unique random 4 character capitalized ids.
    '''
    seen = set()
    ret = []
    for i in range(num_ids):
      id = None
      while (not id) or (id in seen):
        id = ''.join(
            random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for j in range(4))
      seen.add(id)
      ret.append(id)
    return ret

  def GetScoredHandList(self):
    ''' Fetch the list of all hands that are associated with this tournament.

    Returns:
      List of dicts each corresponding to a non-deleted hand that has been scored
        in this tournament. Dicts have the following structure:
        {
          "calls": {
            "north": "T",
            "east": "GT",
            "west": "",
            "south": ""
           },
          "ns_score": 150,
          "ew_score": -150,
          "notes": "hahahahahaha what a fool"
          "board_no": 1,
          "ns_pair": 2, 
          "ns_score": 100
          "ew_score": 0
        }
      calls and notes may be null.
    '''
    hand_list = []
    for hand_score in HandScore.query(ancestor=self.key).fetch():
      if hand_score.deleted:
        continue
      split_key = hand_score.key.id().split(":")
      hand_list.append(
          {'calls': hand_score.calls_dict(),
           'board_no': int(split_key[0]),
           'ns_pair': int(split_key[1]), 
           'ew_pair': int(split_key[2]),
           'ns_score': hand_score.ns_score,
           'ew_score': hand_score.ew_score,
           'notes': hand_score.notes})
    return hand_list

  def GetBoards(self):
    """Returns this tournaments boards.

    Returns: List of boardgenerator board objects sorted by id.
    """
    boards = []
    for board in Board.query(ancestor=self.key).fetch():
      boards.append(boardgenerator.Board.FromJson(board))

    return sorted(boards, key=lambda x: x.id)


class PlayerPair(ndb.Model):
  ''' Model for all the information about a player pair in a specific tournament.

  Must be a child of some tournament.

  Attribtes:
    players: json object describing a list of players. Should have length at
             most 2.
    pair_no: the number associated with this pair in this tournament
    id: a 4 character capitalized letter string that identifies this pair.
  '''
  players = ndb.JsonProperty()
  pair_no = ndb.IntegerProperty()
  id = ndb.StringProperty()

  def player_list(self):
    return json.loads(self.players) if self.players else []

  @classmethod
  def CreateKey(cls, parent_tourney, pair_no):
    ''' Create a key for pair number pair_no in parent_tourney.

    Args:
      parent_tourney: Tournament. Tournament in which this hand happened.
      pair_no: Integer. Pair number for a pair whose key we are getting. 

    Returns:
      ndb.Key that has parent_tourney as a parent.
    '''
    return ndb.Key(cls._get_kind(), pair_no, parent=parent_tourney.key)
    
  @classmethod
  def GetByPairNo(cls, parent_tourney, pair_no):
    ''' Fetches a PlayerPair given its parent tournament and pair number.

    Args:
      parent_tourney: Tournament. Tournament in which this hand happened.
      pair_no: Integer. Pair number for the pair we are fetching.

    Returns:
      PlayerPair with this pair_no if it exists in the tournament. None 
      otherwise.
    '''
    return cls.CreateKey(parent_tourney, pair_no).get()

class HandScore(ndb.Model):
  ''' Model for all the information about a single hand.

  Must be a child of some tournament. Must be keyed as a concatenation of hand
  number, ns pair number, and ew pair number.

  Attributes:
    calls: json object describing the calls for the hand. Can be None.
    notes: hand related notes. Can be None.
    ns_score: North/South score. Can be None for deleted hands only.
    ew_score: East/West score. Can be None for deleted hands only. 
    deleted: True iff the hand used to exist but has been deleted. Object is
             kept around for change log stability.
  '''
  calls = ndb.JsonProperty()
  notes = ndb.TextProperty()
  ns_score = ndb.IntegerProperty()
  ew_score = ndb.IntegerProperty()
  deleted = ndb.BooleanProperty()

  def calls_dict(self):
    ''' Returns the calls property as a dictionary if set. None otherwise.'''
    return json.loads(self.calls) if self.calls else None

  @classmethod
  def CreateKey(cls, parent_tourney, hand_no, ns_pair, ew_pair):
    ''' Create a key for this tournament, hand, opponents combination.

    Args:
      parent_tourney: Tournament. Tournament in which this hand happened.
      hand_no: Integer. Number of this hand.
      ns_pair: Integer. Number of the North/South pair.
      ew_pair: Integer. Number of the East/West pair.

    Returns:
      ndb.Key that has parent_tourney as a parent.
    '''
    return ndb.Key(cls._get_kind(),
                   cls.CreateKeyId(hand_no, ns_pair, ew_pair), 
                   parent=parent_tourney.key)

  @classmethod
  def CreateKeyId(cls, hand_no, ns_pair, ew_pair):
    ''' Create a string id for this tournament, hand, opponents combination.

    Args:
      hand_no: Integer. Number of this hand.
      ns_pair: Integer. Number of the North/South pair.
      ew_pair: Integer. Number of the East/West pair.

    Returns:
      string to be used as id for a HandPair
    '''
    return str(hand_no) + ":" + str(ns_pair) + ":" + str(ew_pair)

  @classmethod
  def GetByHandParams(cls, parent_tourney, hand_no, ns_pair, ew_pair):
    ''' Gets a HandScore given its parent, hand number, and opponents.

    Args:
      parent_tourney: Tournament. Tournament in which this hand happened.
      hand_no: Integer. Number of this hand.
      ns_pair: Integer. Number of the North/South pair.
      ew_pair: Integer. Number of the East/West pair.

    Returns:
      HandScore corresponding to these params if it exists in the tournament and
      has not been deleted. None otherwise.
    '''
    score = cls.CreateKey(parent_tourney, hand_no, ns_pair, ew_pair).get()
    return score if (score and not score.deleted) else None

  def Delete(self):
    ''' Mark this hand as deleted and add to Datastore. Also update changelog.

    Assumes this change has been made by the tournament's director.
    '''
    self.calls = None
    self.notes = None
    self.ns_score = None
    self.ew_score = None
    self.deleted = True
    self.PutChangeLog(0)
    self.put()
  
  def PutChangeLog(self, changed_by):
    ''' Create a change log for the current state of the hand.

    Uses current timestamp in seconds as key.

    Args:
        changed_by: Integer. Pair number for the user requesting the change.
    '''
    change_dict = {
      "calls" : self.calls_dict(),
      "notes" : self.notes,
      "ns_score" : self.ns_score,
      "ew_score" : self.ew_score,
    }
    epoch = datetime.datetime.utcfromtimestamp(0)
    nowtime = datetime.datetime.now()
    change_log = ChangeLog(changed_by=changed_by, change=json.dumps(change_dict))
    change_log.key = ndb.Key("ChangeLog", str((nowtime - epoch).total_seconds()),
                             parent=self.key)
    change_log.put()


class ChangeLog(ndb.Model):
  ''' Model that logs all the changes made to a specific hand.

  Is a child of some hand. Keyed by timestamp. This model is assumed to be 
  called regularly and not often parsed.
      
  Attributes:
    changed_by: Integer. Pair number of the user that requested the change. 0
      for the director.
    change: json object describing all the action of the hand. See api for 
      json format of a single change.  
  '''
  # Pair number of the user making the change. If 0, changed by director.
  changed_by = ndb.IntegerProperty()
  # The state of the hand the change is made. Encoded as JSON object as:
  change = ndb.JsonProperty()

  def to_dict(self):
    ''' Returns a dict version of this ChangeLog. See api for format '''
    return { 'changed_by' : self.changed_by,
             'change' : json.loads(self.change),
             'timestamp_sec' :  self.key.id() }


class Board(ndb.Model):
  '''Record of a single board with a parent tournament.

  Child of a tournament, keyed by board number.

  Attributes:
    board_number: Integer. Identifier of board within its parent tournament.
    board: json object describing the board (cards, positions, first eight).
  '''

  board_number = ndb.IntegerProperty()
  board = ndb.JsonProperty()