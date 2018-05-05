import datetime
import json
import random
from movements import Movement
from python import boardgenerator

from google.appengine.ext import ndb

AVG = 555
AVGP = 666
AVGPP = 777
AVGM = 888
AVGMM = 999

# Lock states. Internal codes for the lock state of the tournament.
INVALID = -1
# Teams involved in the hand can edit hand even if it's already been scored.
UNLOCKED = 0
# Teams involved in the hand can score a hand but cannot overwrite hands that
# have already been scored.
LOCKABLE = 1
# Only administrators can score any hands.
LOCKED = 2

class Tournament(ndb.Model):
  ''' Model for all the information needed to describe a Tournament
     
  Attributes:
    owner_id: Google ID for the owner of the tournament. Required.
    name: name of the tournament. Required.
    no_boards: Number of boards in the tournament. Required.
    no_pairs: Number of pairs in the tournament. Required.
    legacy_version_id: A legacy version of a movement used to make sure old
                       tournaments do not crash after movement changes. Usually
                       unset. 
    lock_status: The amount of write access non-administrators have to score 
                 hands. See full descriptions in constant definitions above.
  '''
  owner_id = ndb.StringProperty()
  name = ndb.StringProperty()
  no_boards = ndb.IntegerProperty()
  no_pairs = ndb.IntegerProperty()
  legacy_version_id = ndb.IntegerProperty()
  lock_status = INVALID

  @classmethod
  def CreateAndPersist(cls, boards, **kwargs):
    '''Creates and persists a new tournament with the given properties and
      populates its boards. 
    
    Boards are put asynchronously so a caller of this method should be 
    decorated with @ndb.toplevel.

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
      board.put_async()
    return tournament

  def PutPlayers(self, player_list, old_no_pairs):
    ''' Create a or update PlayerPair Entities corresponding to each player 
    pair in this tournament (1 ... no_pairs).
    
    This method saves any useful information from player_list and puts it into
    Datastore as a child of this Tournament. If the no_players has changed,
    generates a unique (for this tournament) id associated with each new pair,
    but keeps existing pair coedes the same. Playerpairs are put asynchronously 
    so a caller of this method should be decorated with @ndb.toplevel.

    Args:
      player_list: list of dicts with keys pair_no (req), name (opt), 
        and email (opt) Must have same length as current number of pairs.
      old_no_pairs: the total number of pairs this tournament used to have.
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
    
    existing_player_futures = self.GetAllPlayerPairsAsync(old_no_pairs)
        
    # If the number of players doesn't change, we just override some fields
    # in existing pairs. Otherwise, we delete existing pairs and create new 
    # ones.
    if (self.no_pairs > old_no_pairs):
      random_ids = self._RandomId(self.no_pairs - old_no_pairs)
    elif (self.no_pairs < old_no_pairs):
      ndb.delete_multi_async(
          [existing_player_futures[i].get_result().key for i in 
           xrange(self.no_pairs, old_no_pairs)])

    # The create a PlayerPair and put it into Datastore for each possible
    # number. Use reversed to start with new players and give futures more 
    # time to return.
    for i in reversed(range(1, self.no_pairs + 1)):
      pair_members = pair_dict.get(i) 
      str_pair_members = json.dumps(pair_members) if pair_members else ''
      if i <= old_no_pairs:
          player_pair = existing_player_futures[i-1].get_result()
          player_pair.players = str_pair_members
      else:
        player_pair = PlayerPair(players=str_pair_members,
                                 pair_no=i, id=random_ids[i-1-old_no_pairs],
                                 parent=self.key)
      player_pair.key = PlayerPair.CreateKey(self, i)
      player_pair.put_async()

  def GetAllPlayerPairsAsync(self, no_pairs=None):
    '''Returns a list of futures for the first no_pairs PlayerPairs associated
       with this tournament in pair number order.
    '''
    no_pairs = no_pairs if no_pairs else self.no_pairs
    return [PlayerPair.CreateKey(self, i + 1).get_async() for i in xrange(no_pairs)]

  def PutHandScore(self, hand_no, ns_pair, ew_pair, hand_calls, hand_ns_score,
                   hand_ew_score, hand_notes, changed_by):
    ''' Create a new HandScore Entity corresponding to this hand and put it 
        into datastore.
    
    Everything is put asynchronously so a caller of this method should be 
    decorated with @ndb.toplevel.

    Args:
      hand_no: Integer. Number of this hand.
      ns_pair: Integer. Number of the North/South pair.
      ew_pair: Integer. Number of the East/West pair.
      hand_calls: Dict representation of the calls to this hand
      hand_ns_score: Integer or String. Score for the North/South pair. If
         String, must be one of AVG, AVG+, AVG++, AVG-, AVG-- allowing for any
         capitalization.
      hand_ew_score: Integer or String. Score for the East/West pair. If
         String, must be one of AVG, AVG+, AVG++, AVG-, AVG-- allowing for any
         capitalization.
      hand_notes: String. Notes for the hand.
      changed_by: Integer. Pair number of the requestor. 0 if director.
    '''
    if not isinstance(hand_ns_score, int):
      hand_ns_score = self._TransformAvgScoreToInt(hand_ns_score)
      hand_ew_score = self._TransformAvgScoreToInt(hand_ew_score)

    hand_score = HandScore(calls=json.dumps(hand_calls), notes=hand_notes,
                           ns_score=hand_ns_score, ew_score=hand_ew_score,
                           deleted=False)
    hand_score.key = HandScore.CreateKey(self, hand_no, ns_pair, ew_pair)
    hand_score.put_async()
    hand_score.PutChangeLog(changed_by)

  def GetMovement(self):
    '''Returns a movement associated with this tournament. 

    Assumes that this is a valid tournament.
    '''
    no_hands_per_round, no_rounds = Movement.NumBoardsPerRoundFromTotal(
      self.no_pairs, self.no_boards)
    return Movement.CreateMovement(self.no_pairs, no_hands_per_round,
                                   no_rounds, self.legacy_version_id)

  def _TransformAvgScoreToInt(self, score):
    ''' Return the integer representation of an avg score. If score is not legal
        avg score, return None.
    '''
    score = score.strip()
    score = score[0:3].upper() + score[3:len(score)]
    if score == 'AVG':
      return AVG
    elif score == 'AVG+':
      return AVGP
    elif score == 'AVG++':
      return AVGPP
    elif score == 'AVG-':
      return AVGM
    elif score == 'AVG--':
      return AVGMM
    return None

  def _RandomId(self, num_ids):
    ''' Generate a list of num_ids unique random 4 character capitalized ids.
    
    Ensures that the ids are not used by any other pair in any other tournament.
    '''
    ret = []
    while (len(ret) < num_ids):
      futures = []
      ids = []
      for i in range(num_ids - len(ret)):
        id = ''.join(
            random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for j in range(4))
        ids.append(id)
        futures.append(PlayerPair._query(ndb.GenericProperty('id') == id).fetch_async(
            keys_only=True, limit=1))
      for i in xrange(len(futures)):
        player_pairs = futures[i].get_result()
        if not player_pairs:
          ret.append(ids[i])
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
           'ns_score': hand_score.get_ns_score(),
           'ew_score': hand_score.get_ew_score(),
           'notes': hand_score.notes})
    return hand_list

  def ScoredHands(self):
    ''' Find all hands already scored in the tournament.

    Return:
      A list of tuples (hand no, north/south team, east/west team) of all hands
      scores in this tournament.
    A less expensive and quicker method than GetScoredHandList(self).
    '''
    ret = []
    hands = HandScore.query(HandScore.deleted == False,
                            ancestor=self.key).fetch(keys_only=True)
    for hand in hands:
      ret.append(HandScore.DescriptionFromKeyId(hand.id()))
    return ret

  def GetBoards(self):
    """Returns this tournaments boards.

    Returns: List of boardgenerator board objects sorted by id.
    """
    boards = []
    for board in Board.query(ancestor=self.key).fetch():
      boards.append(boardgenerator.Board.FromJson(board))

    return sorted(boards, key=lambda x: x.id)

  def IsLocked(self):
    if self.lock_status == INVALID:
      ls = LockStatus.CreateKey(self).get()
      self.lock_status = ls.lock_status if ls else INVALID
    return self.lock_status == LOCKED
    
  def IsLockable(self):
    if self.lock_status == INVALID:
      ls = LockStatus.CreateKey(self).get()
      self.lock_status = ls.lock_status if ls else INVALID
    return self.lock_status == LOCKABLE
    
  def IsUnlocked(self):
    if self.lock_status == INVALID:
      ls = LockStatus.CreateKey(self).get()
      self.lock_status = ls.lock_status if ls else INVALID
    return (not self.lock_status) or self.lock_status == UNLOCKED
  
  def SetLockStatus(self):
    lock_status = LockStatus(lock_status=self.lock_status, key=LockStatus.CreateKey(self))
    lock_status.put()
  
  def Lock(self):
    self.lock_status = LOCKED
    self.SetLockStatus()
      
  def Unlock(self):
    self.lock_status = UNLOCKED
    self.SetLockStatus()
    
  def MakeLockable(self):
    self.lock_status = LOCKABLE
    self.SetLockStatus()

class LockStatus(ndb.Model):
  ''' Model for the status of lockability of a specific tournament.
  
  Refers to whether a tournament is locked (only administrator may edit hands),
  lockable (a hand cannot be overwritten after scoring excpt by admin), or UNLOCKED
  (can be overwritten any number of times). Must be a child of some tournament.
  
  Attributes:
    lock_status: int defined in constants above.
  '''
  lock_status = ndb.IntegerProperty()
  
  @classmethod
  def CreateKey(cls, parent_tourney):
    ''' Create a key for a parent_tourney.

    The id is always going to be 1 as there is at most 1 LockStatus per 
    tournament.
    Args:
      parent_tourney: Tournament. Tournament in which this hand happened.

    Returns:
      ndb.Key that has parent_tourney as a parent.
    '''
    return ndb.Key(cls._get_kind(), 1, parent=parent_tourney.key)

class PlayerPair(ndb.Model):
  ''' Model for all the information about a player pair in a specific tournament.

  Must be a child of some tournament.

  Attribtes:
    players: json object describing a list of players. Should have length at
             most 2. Each player is a dict with keys name, email.
    pair_no: the number associated with this pair in this tournament
    id: a 4 character capitalized letter string that identifies this pair.
  '''
  players = ndb.JsonProperty()
  pair_no = ndb.IntegerProperty()
  id = ndb.StringProperty()

  def player_list(self):
    ''' Return a list of players in this pair. '''
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
    
  @classmethod
  def GetByPairNoAsync(cls, parent_tourney, pair_no):
    '''Same as a above but returns a Future that will contain tha PlayerPair.'''
    return cls.CreateKey(parent_tourney, pair_no).get_async()

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
  # Special codes for avg, avg+, avg++, avg-, avg-- are listed as:
  # 555, 666, 777, 888, 999. 
  ns_score = ndb.IntegerProperty()
  ew_score = ndb.IntegerProperty()
  deleted = ndb.BooleanProperty()
  
  def get_ns_score(self):
    ''' Return the score of the North/South team. If the team has a special
    director-set score, returns the appropriate string, e.g. 'AVG+', 'AVG--'.
    '''
    if self.ns_score == AVG:
      return "AVG"
    elif self.ns_score == AVGP:
      return "AVG+"
    elif self.ns_score == AVGPP:
      return "AVG++"
    elif self.ns_score == AVGM:
      return "AVG-"
    elif self.ns_score == AVGMM:
      return "AVG--"
    else:
      return self.ns_score

  def get_ew_score(self):
    ''' Return the score of the East/West team. If the team has a special
    director-set score, returns the appropriate string, e.g. 'AVG+', 'AVG--'.
    '''
    if self.ew_score == AVG:
      return "AVG"
    elif self.ew_score == AVGP:
      return "AVG+"
    elif self.ew_score == AVGPP:
      return "AVG++"
    elif self.ew_score == AVGM:
      return "AVG-"
    elif self.ew_score == AVGMM:
      return "AVG--"
    else:
     return self.ew_score

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
  def DescriptionFromKeyId(self, id):
    ''' Parse a key id into a tuple describing the hand.

    Args:
      id: String. Key id for the hand to be parsed. Must have format returned by
        CreateKeyId.

    Returns:
      Tuple with members (hand_no, ns_pair, ew_pair).
    '''
    split = id.split(":")
    return (int(split[0]), int(split[1]), int(split[2]))

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

  @classmethod
  def GetByHandParamsAsync(cls, parent_tourney, hand_no, ns_pair, ew_pair):
    ''' Same as above, but does so asyncronously returning a Future of HandScore.
        NOTE one key difference is that this method does not check for deletion 
        of score. Caller must do that on their own.
    '''
    return cls.CreateKey(parent_tourney, hand_no, ns_pair, ew_pair).get_async()

  @classmethod
  def GetByMultipleHands(cls, parent_tourney, hands):
    ''' Gets multiple handscores from a parent_tourney.

    Args:
      parent_tourney: Tournament. Tournament that we are querying.
      hands: List of (hand_no, ns_pair, ew_pair) tuples.
    Returns:
      List of HandScores for the corresponding hands.    
    '''
    futures = map(lambda x : HandScore.GetByHandParamsAsync(
          parent_tourney, x[0], x[1], x[2]), hands);
    all_hands = []
    for f in futures:
      x = f.get_result()
      all_hands.append(x if (x and not x.deleted) else None)
    return all_hands

  def Delete(self):
    ''' Mark this hand as deleted and add to Datastore. Also update changelog.

    The delete is done asynchronosouly, so a caller of this method should have
    a @ndb.toplevel decoration.
    
    Assumes this change has been made by the tournament's director.
    '''
    self.calls = None
    self.notes = None
    self.ns_score = None
    self.ew_score = None
    self.deleted = True
    self.put_async()
    self.PutChangeLog(0)
  
  def PutChangeLog(self, changed_by):
    ''' Create a change log for the current state of the hand.

    Uses current timestamp in seconds as key. The put is done asynchronosouly,
    so a caller of this method should have a @ndb.toplevel decoration.

    Args:
        changed_by: Integer. Pair number for the user requesting the change.
    '''
    change_dict = {
      "calls" : self.calls_dict(),
      "notes" : self.notes,
      "ns_score" : self.get_ns_score(),
      "ew_score" : self.get_ew_score(),
    }
    epoch = datetime.datetime.utcfromtimestamp(0)
    nowtime = datetime.datetime.now()
    change_log = ChangeLog(changed_by=changed_by, change=json.dumps(change_dict))
    change_log.key = ndb.Key("ChangeLog", str((nowtime - epoch).total_seconds()),
                             parent=self.key)
    change_log.put_async()


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