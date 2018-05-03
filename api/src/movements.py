import json
import os

# Dictionary of tuple (num pairs, num hands per round, num rounds) to the movement.
_MOVEMENTS = {}

class MovementRound:
  '''Class that defines a single round in a movement within a tournament. 

  A MovementRound is seen from the point of view of a single pair.

  Attributes:
    round: Integer. Round number.
    table: Integer. Table number.
    is_north: Boolean. True if the pair sits in North/South position. False for
      East/West.
    hands: List of Integers. List of hand numbers to be played in this round.
    opponent: Integer. Pair number of the opponent for this round.
    relay_table: Boolean. True if these hands are shared with another table.
  '''
  def __init__(self, round, table, is_north, hands, opponent, relay_table):
    self.round = round
    self.table = table
    self.is_north = is_north
    self.hands = hands
    self.opponent = opponent
    self.relay_table = relay_table

  def to_dict(self):
    ''' Transforms to json dict format.

    Returns:
      Dict of format:
        {
         "round": 1
         "position": "3N"
         "opponent": 2
         "hands": [3, 4, 5]
         "relay_table": true
        }
    '''
    if not self.hands:
      return { "round" : self.round }
    return {"round" : self.round,
            "position" : str(self.table) + ("N" if self.is_north else "E"),
            "hands" : self.hands,
            "opponent" : self.opponent,
            "relay_table" : self.relay_table}


class Movement:
  ''' Class that defines a movement structure within a tournament. It is 
  wholly defined by the number of pairs participating and the number of
  hands per round. The movement is guaranteed to be valid, in that it 
  provides a fair and feasible tournament (all hands played the same number
  of times, no impossible opponent combinations, etc).
      
  Attributes:
    pair_dict: Dictionary from pair number to movement pair movement
      where pair movement is a list MovementRounds.
  '''
  def __init__(self, no_pairs, no_hands_per_round, no_rounds=None,
               legacy_version_id=None):
    ''' Initializes the movement for this configuration.

        Raises:
          ValueError if we do not have a defined movement for this configuration.
    '''
    if legacy_version_id == 1:
      if no_hands_per_round == 2 and no_pairs == 7 and no_rounds == 7:
        json_data=open(os.path.join(os.getcwd(), 
                       'api/src/movement_files/7_pair_2_hands_7_rounds_legacy1.txt')).read()
      elif no_hands_per_round == 3 and no_pairs == 10 and no_rounds == 7:
        json_data=open(os.path.join(os.getcwd(), 
                       'api/src/movement_files/10_pair_3_hands_legacy1.txt')).read()
    elif no_hands_per_round == 3 and no_pairs == 10 and no_rounds == 7:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/10_pair_3_hands.txt')).read()
    elif no_hands_per_round == 2 and no_pairs == 10 and no_rounds == 7:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/10_pair_2_hands.txt')).read()
    elif no_hands_per_round == 3 and no_pairs == 9 and no_rounds == 8:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/9_pair_3_hands_8_rounds.txt')).read()
    elif no_hands_per_round == 2 and no_pairs == 9 and no_rounds == 8:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/9_pair_2_hands.txt')).read()
    elif no_hands_per_round == 2 and no_pairs == 9 and no_rounds == 7:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/9_pair_2_hands_7_rounds.txt')).read()
    elif no_hands_per_round == 3 and no_pairs == 9 and no_rounds == 7:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/9_pair_3_hands_7_rounds.txt')).read()
    elif no_hands_per_round == 2 and no_pairs == 8 and no_rounds == 6:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/8_pair_2_hands_6_rounds.txt')).read()
    elif no_hands_per_round == 3 and no_pairs == 8 and no_rounds == 6:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/8_pair_3_hands_6_rounds.txt')).read()
    elif no_hands_per_round == 2 and no_pairs == 7 and no_rounds == 7:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/7_pair_2_hands_7_rounds.txt')).read()
    elif no_hands_per_round == 3 and no_pairs == 7 and no_rounds == 7:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/7_pair_3_hands_7_rounds.txt')).read()
    elif no_hands_per_round == 2 and no_pairs == 11 and no_rounds == 7:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/11_pair_2_hands_7_rounds.txt')).read()
    elif no_hands_per_round == 3 and no_pairs == 11 and no_rounds == 7:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/11_pair_3_hands_7_rounds.txt')).read()
    elif no_hands_per_round == 2 and no_pairs == 11 and no_rounds == 6:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/11_pair_2_hands_7_rounds_6_max.txt')).read()
    elif no_hands_per_round == 3 and no_pairs == 11 and no_rounds == 6:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/11_pair_3_hands_7_rounds_6_max.txt')).read()
    elif no_hands_per_round == 3 and no_pairs == 6 and no_rounds == 5:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/6_pair_3_hands_5_rounds.txt')).read()
    elif no_hands_per_round == 4 and no_pairs == 6 and no_rounds == 5:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/6_pair_4_hands_5_rounds.txt')).read()
    elif no_hands_per_round == 4 and no_pairs == 5 and no_rounds == 5:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/5_pair_4_hands_5_rounds.txt')).read()
    elif no_hands_per_round == 3 and no_pairs == 12 and no_rounds == 5:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/12_pair_3_hands_5_rounds.txt')).read()
    elif no_hands_per_round == 3 and no_pairs == 12 and no_rounds == 6:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/12_pair_3_hands_6_rounds.txt')).read()
    elif no_hands_per_round == 2 and no_pairs == 12 and no_rounds == 6:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/12_pair_2_hands_6_rounds.txt')).read()
    else:
      raise ValueError(("No movements available for the configuration {} " + 
                           "pairs with {} hands per round").format(
                               no_pairs, no_hands_per_round))
    self.pair_dict = {}
    for team, rounds in json.loads(json_data).items():
      list_of_rounds = []
      for round in rounds:
        position_str = round.get("position")
        list_of_rounds.append(MovementRound(
            round["round"], 
            int(position_str[0:(len(position_str) - 1)]) if position_str else None,
            position_str[(len(position_str) - 1):len(position_str)] == "N" if position_str else None,
            round.get("hands", []),
            round.get("opponent"),
            round.get("relay_table")))
      self.pair_dict[int(team)] = list_of_rounds
    self._CalculateUnplayedHands()
    self._CalculateSuggestedPrep()

  @classmethod
  def CreateMovement(cls, no_pairs, no_hands_per_round, no_rounds=None,
                     legacy_version_id=None):
    ''' Static factory method to create and cache movements '''
    key = (no_pairs, no_hands_per_round, no_rounds, legacy_version_id)
    if _MOVEMENTS.get(key):
      return _MOVEMENTS.get(key)
    movement = Movement(no_pairs, no_hands_per_round, no_rounds, 
                        legacy_version_id)
    _MOVEMENTS[key] = movement
    return movement

  def GetMovement(self, pair_no):
    ''' Construct a dictionary for this movement.

    Returns: 
      List of MovementRounds for this pair.
    '''
    return self.pair_dict[pair_no]

  def GetUnplayedHands(self, pair_no):
    ''' Construct hands that this pair will not play.

    Returns:
      A list of hands that pair will not play and can prepair.
    '''
    return self.unplayed_hands.get(pair_no, [])
    
  def GetSuggestedHandPrep(self, pair_no):
    ''' Construct hands that this pair can prepare.

    Returns:
      A list of hands that pair should prepair.
    '''
    return self.suggested_prep.get(pair_no, [])

  def GetNumRounds(self):
    '''Returns the total number of rounds in this movement.'''
    return len(self.pair_dict[1])

  def GetListOfPlayersForHand(self, board_no):
    '''Returns a list of (ns_pair, ew_pair) tuples that play board_no.'''
    pairs = []
    for pair_no, rounds in self.pair_dict.items():
      for round in rounds:
        if board_no in round.hands and round.is_north:
          pairs.append((pair_no, round.opponent))
    return pairs

  @staticmethod
  def NumBoardsPerRoundFromTotal(no_pairs, total_boards):
    ''' Determine how many boards are to be used per round from the total 
        number of pairs and boards in a tournament.

    Returned value is not the only feasible value but the best one as 
    determined by us.

    Returns:
      Tuple (number of boards per round, maximum number of rounds).
        (0, 0) if no movement configuration exists for this input.
    '''
    if total_boards == 21 and no_pairs == 12:
      return (3, 6)
    if total_boards == 18 and no_pairs == 12:
      return (3, 5)
    if total_boards == 14 and no_pairs == 12:
      return (2, 6)
    if total_boards == 14 and no_pairs == 11:
      return (2, 7)
    if total_boards == 21 and no_pairs == 11:
      return (3, 7)
    if total_boards == 16 and no_pairs == 11:
      return (2, 6)
    if total_boards == 24 and no_pairs == 11:
      return (3, 6)
    if total_boards == 24 and no_pairs == 10:
      return (3, 7)
    elif total_boards == 16 and no_pairs == 10:
      return (2, 7)
    elif total_boards == 18 and no_pairs == 9:
      return (2, 8)
    elif total_boards == 27 and no_pairs == 9:
      return (3, 8)
    elif total_boards == 14 and no_pairs == 9:
      return (2, 7)
    elif total_boards == 21 and no_pairs == 9:
      return (3, 7)
    elif total_boards == 16 and no_pairs == 8:
      return (2, 6)
    elif total_boards == 24 and no_pairs == 8:
      return (3, 6)
    elif total_boards == 14 and no_pairs == 7:
      return (2, 7)
    elif total_boards == 21 and no_pairs == 7:
      return (3, 7)
    elif total_boards == 15 and no_pairs == 6:
      return (3, 5)
    elif total_boards == 20 and no_pairs == 6:
      return (4, 5)
    elif total_boards == 20 and no_pairs == 5:
      return (4, 5)
    else:
      return (0, 0)
      
  def _CalculateUnplayedHands(self):
    ''' Get the list, for each pair, of hands that the pair does not play. 

    Side effects:
     Sets attribute unplayed_hands. Dict from string representation of pair
       number to the list of hands not played by that pair.
    '''
    self.total_boards = 0
    seen_hands = {}
    self.unplayed_hands = {}
    for team, rounds in self.pair_dict.items():
      for round in rounds:
        if not round.hands:
          continue
        self.total_boards = max(max(round.hands), self.total_boards)
        seen_hands[team] = seen_hands.get(team, set()).union(round.hands)
    for team, hand_list in seen_hands.items():
      for hand in range(1, self.total_boards + 1):
        if hand not in hand_list:
          self.unplayed_hands.setdefault(team, []).append(hand)
          
  def _CalculateSuggestedPrep(self):
    ''' Get the list, for each pair, of hands that we suggest the pair prepares. 

    Not guaranteed to be optimal, but tries to spread out the burden as much
    as possible. Each hand in the movement is guaranteed to be in someone's 
    list.

    Side effects:
     Sets attribute suggested_prep. Dict from string representation of pair
       number to the list of hands the pair should prepare.
    '''
    self.suggested_prep = {}
    if not self.unplayed_hands:
      return
    max_unplayed_hands =  max([len(x) for x in self.unplayed_hands.values()])
    hands = set()
    for i in range(max_unplayed_hands):
      for team in range (1, len(self.pair_dict) + 1):
        unplayed_hands = self.GetUnplayedHands(team)
        for j in range (i, len(unplayed_hands)):
          hand = unplayed_hands[j]
          if not hand in hands:
            hands.add(hand)
            self.suggested_prep.setdefault(team, []).append(hand)
            break

