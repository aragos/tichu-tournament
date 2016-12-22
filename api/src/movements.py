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
  def __init__(self, no_pairs, no_hands_per_round):
    ''' Initializes the movement for this configuration.

        Raises:
          ValueError if we do not have a defined movement for this configuration.
    '''
    if no_hands_per_round == 3 and no_pairs == 10:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/10_pair_3_hands.txt')).read();
    elif no_hands_per_round == 2 and no_pairs == 10:
      json_data=open(os.path.join(os.getcwd(), 
                     'api/src/movement_files/10_pair_2_hands.txt')).read();
    else:
      raise ValueError("No movements available for the configuration {} " + 
                           "pairs with {} hands per round".format(
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
      Returns 0 if no movement with such a configuration exists.
  '''
  if total_boards == 24 and no_pairs == 10:
    return 3
  elif total_boards == 16 and no_pairs == 10:
    return 2
  else:
    return 0