import json
import os

class Movement:
  ''' Class that defines a movement structure within a tournament. It is 
      wholly defined by the number of pairs participating and the number of
      hands per round. The movement is guaranteed to be valid, in that it 
      provides a fair and feasible tournament (all hands played the same number
      of times, no impossible opponent combinations, etc).
      
      Attributes:
        pair_dict: Dictionary from pair number to movement pair movement
          where pair movement is a list of dicts describing a round as below.
          {
             "round": 1
             "position": "3N"
             "opponent": 2
             "hands": [3, 4, 5]
              "relay_table": 5
          }
  ''' 
  def __init__(self, no_pairs, no_hands_per_round, no_rounds=None):
    ''' Initializes the movement for this configuration.

        Raises:
          ValueError if we do not have a defined movement for this configuration.
    '''
    if no_hands_per_round == 3 and no_pairs == 10 and no_rounds == 7:
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
    else:
      raise ValueError(("No movements available for the configuration {} " + 
                           "pairs with {} hands per round").format(
                               no_pairs, no_hands_per_round))
    self.pair_dict = json.loads(json_data)

  def GetMovement(self, pair_no):
    ''' Returns a dictionary for this movement type.
        
        Returns: Dictionary from pair number to movement pair movement
          where pair movement is a list of dicts describing a round as below.
          {
             "round": 1
             "position": "3N"
             "opponent": 2
             "hands": [3, 4, 5]
              "relay_table": 5
          }
    '''
    return self.pair_dict[str(pair_no)]


def NumBoardsPerRoundFromTotal(no_pairs, total_boards):
  ''' Determines how many boards are to be used per round from the total 
      number of pairs and boards in a tournament.
      Returned value is not the only feasible value but the best one as 
      determined by us.
      
      Returns:
        Tuple (number of boards per round, maximum number of rounds).
        (0, 0) if no movement configuration exists for this input.
  '''
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
  else:
    return (0, 0)