from python import board

def ListOfModelBoardsToListOfBoards(model_boards):
  ''' Transforms a list of Board objects to a list of Boards and returns the
  list sorted by board number.
  '''
  boards = []
  for model_board in model_boards:
    boards.append(board.Board.FromJson(model_board))
  return sorted(boards, key=lambda x: x.id)

def ListOfScoredHandsToListOfDicts(all_hand_scores):
  ''' Transforms a list of ScoredHand objects to a list of dicts 
  representing all non-deleted scored hands data.
  Example dict:
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
    }
  '''
  hand_list = []
  for hand_score in all_hand_scores:
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