import json
from calculator import Calls
from calculator import HandResult
from calculator import OrderBy
from calculator import Board
from calculator import Calculate
from calculator import TeamSummary


def ReadJSONInput(hand_list):
  """ Reads input from a list of hands. 
    
  Returns:
    
  """

  board_no_to_hr_list = {}
  for hand in hand_list:
    board_no = hand["board_no"]
    ns_pair = hand["ns_pair"]
    ew_pair = hand["ew_pair"]
    calls = hand["calls"]
    hr_list = board_no_to_hr_list.setdefault(board_no, [])
    hr_list.append(HandResult(board_no, ns_pair, ew_pair,
                              hand["ns_score"], hand["ew_score"],
                              Calls(calls["north"], calls["south"],
                                    calls["east"], calls["west"])))
  board_list = []
  for k, v in board_no_to_hr_list.items():
    board_list.append(Board(k, v))
  return board_list
  

def OutputJSON(hand_list, team_summaries):
  pair_summaries = []
  for ts in team_summaries:
    pair_summaries.append({"pair_no": ts.team_no, "mps": ts.mps, "rps": ts.rps, "aps" : ts.aps})
  for hand in hand_list:
    board_no = hand["board_no"]
    ns_pair = hand["ns_pair"]
    ew_pair = hand["ew_pair"]
    for ts in team_summaries: 
      if ts.team_no == ns_pair:
         hand["ns_mps"] = ts.board_mps[board_no]
         hand["ns_rps"] = ts.board_rps[board_no]
         hand["ns_aps"] = ts.board_aps[board_no]
      if ts.team_no == ew_pair:
         hand["ew_mps"] = ts.board_mps[board_no]
         hand["ew_rps"] = ts.board_rps[board_no]
         hand["ew_aps"] = ts.board_aps[board_no]
  ret = {"pair_summaries": pair_summaries, "hands": hand_list}
  return json.dumps(ret, sort_keys=True, indent=2)
