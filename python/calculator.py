import itertools
import json
import math

class InvalidCallError(Exception):
    def __init__(self, call, side):
         self.value = "Invalid call value " + call + " from " + side
    def __str__(self):
        return repr(self.value)
        
class InvalidScoreError(Exception):
    def __init__(self, board_no, ns_pair_no, ew_pair_no):
         self.value = "Invalid score: for board no: " + str(board_no) +\
             ", pairs: " + str(ns_pair_no) + " and " + str(ew_pair_no)
    def __str__(self):
        return repr(self.value)

class Calls:
    """ Summaries of all calls in the hand. """

    def __init__(self, n_call = "", s_call = "", e_call = "", w_call = ""):
        """ Raises an exception if any of the calls are invalid """
        self._call_dict = {"N": n_call.upper().strip(),
                           "S": s_call.upper().strip(),
                           "E": e_call.upper().strip(), 
                           "W": w_call.upper().strip()}
        # Check validity
        for name, call in self._call_dict.items():
            self._ValidCall(call, name)

    def __str__(self):
        ret = ""
        for name, call in self._call_dict.items():
          if call != "":
            ret += name + "(" + call + "),"
        if ret != "":
            return ret[:(len(ret) - 1)]
        return ret

    def n_call(self):
        """ Returns North's call """
        return self._call_dict["N"]

    def s_call(self):
        """ Returns South's call """
        return self._call_dict["S"]

    def e_call(self):
        """ Returns East's call """
        return self._call_dict["E"]

    def w_call(self):
        """ Returns West's call """
        return self._call_dict["W"]

    def _ValidCall(self, call, side):
        """ Validates a call. Raises exception if something other than T,
            GT, or an empty string is passed. """
        if call != "" and call != "T" and call != "GT":
          raise InvalidCallError(call, side)
    
    @classmethod
    def FromJson(cls, call_json):
        """ Loads from json object. Raises an exception if any of the
            calls are invalid. 
        """
        json_dict = json.loads(call_json)
        return cls(json_dict.get("north", ""), json_dict.get("south", ""), 
                   json_dict.get("east", ""), json_dict.get("west", ""))
                     
    @classmethod
    def FromDict(cls, dict):
        """ Loads from a dictionary. Raises an exception if any of the
            calls are invalid. 
        """
        return cls(dict.get("north", ""), dict.get("south", ""), 
                   dict.get("east", ""), dict.get("west", "")) if dict else cls('', '', '', '')

class HandResult:
    """ Contains all information about a single hand between two teams. """
    
    def __init__(self, board_no, ns_pair_no, ew_pair_no, ns_score, ew_score,
                 calls):
        """ So far doesn't deal with avg, avg+, or avg- """
        self._ns_pair_no = ns_pair_no
        self._ew_pair_no = ew_pair_no
        self._calls = calls
        self._board_no = board_no
        if isinstance(ns_score, int) and isinstance(ew_score, int): 
          self._ns_score = ns_score
          self._ew_score = ew_score
          self._diff = ns_score - ew_score
        else:
          self._ns_score = ns_score.upper().strip()
          self._ew_score = ew_score.upper().strip()
          self._diff = "AVG"
        self._ValidateScore()

    def ns_pair_no(self):
        return self._ns_pair_no

    def ew_pair_no(self):
        return self._ew_pair_no

    def ns_score(self):
        return self._ns_score

    def ew_score(self):
        return self._ew_score

    def calls(self):
        return self._calls

    def diff(self):
        return self._diff;

    def board_no(self):
        return self._board_no;
    
    @staticmethod
    def _TichuScore(call):
      if call == "T":
          return 100
      if call == "GT":
          return 200
      return 0
    
    def _TichuBonus(self, first_out, player):
        team_to_call = {"N": self._calls.n_call(), "S": self._calls.s_call(),
                        "E": self._calls.e_call(), "W": self._calls.w_call()}
        return (1 if first_out == player else -1) * \
               HandResult._TichuScore(team_to_call[player])
    
    def _ValidateScore(self):
        if self._IsValidAvgScore():
          return
        permutations = itertools.permutations(["N", "W", "S", "E"])
        for permutation in permutations:
            if self._IsScoreValid(permutation):
                return
        raise InvalidScoreError(self._board_no, self._ns_pair_no,
                                self._ew_pair_no)

    def _IsValidAvgScore(self):
      avg_scores = ["AVG", "AVG+", "AVG-", "AVG++", "AVG--"]
      return (self._ns_score in avg_scores and
              self._ew_score in avg_scores and
              self._calls.n_call() == "" and
              self._calls.s_call() == "" and
              self._calls.e_call() == "" and
              self._calls.w_call() == "")

    def _TeamBounds(self, team1, team2, first_two):
        if (first_two == team1 or first_two == tuple(reversed(team1))):
            return ([200, 200], [0, 0])
        elif (first_two == team2 or first_two == tuple(reversed(team2))):
            return ([0, 0], [200, 200])
        return ([-25, 125], [-25, 125])
        
      
    def _IsScoreValid(self, out_order):
        assert len(out_order) == 4
        # Check that trick based score is valid.
        if (((self._ns_score + self._ew_score) % 100) != 0 or 
              self._ns_score % 5 != 0 or 
              self._ew_score % 5 != 0):
            return False

        ns_tichu_factor, ew_tichu_factor = 0, 0
        first_out = out_order[0]
        ns_team, ew_team = ("N", "S"), ("E", "W")

        # Add on factors for making/not making Tichu.
        for player in ns_team:
            ns_tichu_factor += self._TichuBonus(first_out, player) 
        for player in ew_team:
            ew_tichu_factor += self._TichuBonus(first_out, player)
        
        # Get bounds for legal scores of each team.
        ns_bounds, ew_bounds = \
            self._TeamBounds(ns_team, ew_team, out_order[0:2])
        one_two = sum(ns_bounds) == 400 or sum(ew_bounds) == 400
        ns_bounds = [x + ns_tichu_factor for x in ns_bounds]
        ew_bounds = [x + ew_tichu_factor for x in ew_bounds]
        
        if (self._ns_score not in range(ns_bounds[0], ns_bounds[1] + 1) or
            self._ew_score not in range(ew_bounds[0], ew_bounds[1] + 1)):
            return False
        elif ((not one_two) and 
              (self._ew_score + self._ns_score - 
                   ns_tichu_factor - ew_tichu_factor != 100)):
          return False
        return True

class BoardScoreLine:
    def __init__(self, hr):
        self._hr = hr
    
    def hr(self):
        return self._hr
        
    def __str__(self):
        if ((self.ns_mps + self.ew_mps + self.ns_rps + self.ew_rps)):
            return ("{0:4s} {1:9s}     {2:s} {3:10d} {4:10d}      {5:.1f}"\
                    "      {6:.1f}     {7:.2f}    {8:.2f}\n")\
                .format(self._hr.ns_pair_no(), self._hr.ew_pair_no(), 
                        str(self._hr.calls()), self._hr.ns_score(),
                        self._hr.ew_score(), self.ns_mps, self.ew_mps,
                        self.ns_rps, self.ew_rps)
        else:
            return "Scores have not been calculated for hand."
            
    def csv_str(self):
        if ((self.ns_mps + self.ew_mps + self.ns_rps + self.ew_rps)):
            return ("{0}, {1}, {2} , {3}, {4}, {5:.1f},"\
                    " {6:.1f}, {7:.2f}, {8:.2f}\n")\
                .format(self._hr.ns_pair_no(), self._hr.ew_pair_no(), 
                        str(self._hr.calls()), self._hr.ns_score(),
                        self._hr.ew_score(), self.ns_mps, self.ew_mps,
                        self.ns_rps, self.ew_rps)
        else:
            return "Scores have not been calculated for hand."
    
    def csv_row(self):
      ns = "NS Team"
      ew = "EW Team"
      calls = "Calls"
      ns_score = "NS Score"
      ew_score = "EW Score"
      ns_mps = "NS MPs"
      ew_mps = "EW MPs"
      ns_rps = "NS RPs"
      ew_rps = "EW RPs"
      ns_aps = "NS APs"
      ew_aps = "EW APs"
      if ((self.ns_mps + self.ew_mps + self.ns_rps + self.ew_rps)):
        return {ns: self._hr.ns_pair_no(),
                ew: self._hr.ew_pair_no(),
                calls: str(self._hr.calls()),
                ns_score: self._hr.ns_score(),
                ew_score: self._hr.ew_score(),
                ns_mps: "{0:.1f}".format(self.ns_mps),
                ew_mps: "{0:.1f}".format(self.ew_mps),
                ns_rps: "{0:.2f}".format(self.ns_rps),
                ew_rps: "{0:.2f}".format(self.ew_rps),
                ns_aps: "{0}".format(self.ns_aps),
                ew_aps: "{0}".format(self.ew_aps),}
      else:
          return "Scores have not been calculated for hand."
      

class Board:
    def __init__ (self, board_no, hand_results):
        assert(sum([x.board_no() == board_no for x in hand_results]) == 
            len(hand_results))
        # TODO: check that each pair occurs once and only once
        self._hand_results = hand_results
        self._board_no = board_no
        self._board_score = []
        
    def board_score(self):
        return self._board_score

    def _get_avg_score_diff(self):
        non_avg_hr = [hr for hr in self._hand_results if hr.diff() != "AVG"]
        return sum([x.diff() for x in non_avg_hr])/len(non_avg_hr)

    def _log_rps(self, rps):
        if rps > 0:
            return math.log1p(rps)
        else: 
            return -math.log1p(-rps)

    def _mp_comp(self, current, other):
        if other == "AVG":
          return 0.5
        if current < other:
            return 0
        if current == other:
            return 0.5
        return 1
    
    def _get_max_rps(self):
      max_rps = -1
      for bsl in self._board_score:
        max_rps = max(max_rps, bsl.ew_rps)
        max_rps = max(max_rps, bsl.ns_rps)
      return max_rps
      
    def _get_max_mps(self, side="n"):
      max_mps = 0
      for bsl in self._board_score:
        if side == "n":
          max_mps = max(max_mps, bsl.ns_mps)
        else:
          max_mps = max(max_mps, bsl.ew_mps)
      return max_mps

    def _called_t(self, hand_result, position, call_to_check):
      calls = hand_result.calls()
      call_fetcher = {"ns": (calls.n_call(), calls.s_call()), "ew": (calls.e_call(), calls.w_call())}
      calls_made = call_fetcher[position]
      if calls_made[0] == call_to_check or calls_made[1] == call_to_check:
        return 1
      return 0

    def _set_avg_mps_rps(self, side, avg_type, max_mps, max_rps, board_score_line):
      if avg_type == "AVG":
        mps_val = max_mps / 2
        rps_val = 0
      elif avg_type == "AVG+":
        mps_val = max_mps * 0.6
        rps_val = 0.2 * max_rps
      elif avg_type == "AVG++":
        mps_val = max_mps * 0.8
        rps_val = 0.6 * max_rps
      elif avg_type == "AVG-":
        mps_val = max_mps * 0.4
        rps_val = -0.2 * max_rps
      else:
        mps_val = max_mps * 0.2
        rps_val = -0.6 * max_rps
      if side == "n":
        board_score_line.ns_mps = mps_val
        board_score_line.ns_rps = rps_val
      else:
        board_score_line.ew_mps = mps_val
        board_score_line.ew_rps = rps_val

    def ScoreBoard(self): 
        self._board_score = []
        avg_score = self._get_avg_score_diff()
        # This is n^2. You can do it in O(n) but will be uglier. Since
        # we will have 4/5 entries each time, this is OK.
        iter = self._hand_results
        gt_calls_ns = sum([self._called_t(x, "ns", "GT") for x in self._hand_results])
        t_calls_ns = sum([self._called_t(x, "ns", "T") for x in self._hand_results])
        gt_calls_ew = sum([self._called_t(x, "ew", "GT") for x in self._hand_results])
        t_calls_ew = sum([self._called_t(x, "ew", "T") for x in self._hand_results])
        for hr in iter:
            if (hr.diff() == "AVG"):
              continue
            bs = BoardScoreLine(hr)
            bs.ns_mps, bs.ew_mps, bs.ns_rps, bs.ew_rps = 0, 0, 0, 0;
            bs.ns_mps = sum(
                [self._mp_comp(hr.diff(), x.diff())
                    for x in self._hand_results]) - 0.5
            bs.ew_mps = sum(
                [1 - self._mp_comp(hr.diff(), x.diff()) 
                    for x in self._hand_results]) - 0.5
            bs.ns_rps = self._log_rps(hr.diff() - avg_score)
            bs.ew_rps = self._log_rps(avg_score - hr.diff())
            # Now to calculate aggressiveness
            num_non_avg = len([x for x in self._hand_results if x.diff() != "AVG" ])
            if self._called_t(hr, "ns", "GT"):
              bs.ns_aps = (num_non_avg - gt_calls_ns) * 2 - t_calls_ns
            elif self._called_t(hr, "ns", "T"):
              bs.ns_aps = (num_non_avg - gt_calls_ns - t_calls_ns)
            else:
              bs.ns_aps = 0
            if self._called_t(hr, "ew", "GT"):
              bs.ew_aps = (num_non_avg - gt_calls_ew) * 2 - t_calls_ew
            elif self._called_t(hr, "ew", "T"):
              bs.ew_aps = (num_non_avg - gt_calls_ew - t_calls_ew)
            else:
              bs.ew_aps = 0
            self._board_score.append(bs)
        # Calculate max rp, and max mps
        max_rps = self._get_max_rps()
        max_ns_mps = self._get_max_mps("n")
        max_ew_mps = self._get_max_mps("e")
        for hr in iter:
          if (hr.diff() != "AVG"):
              continue
          bs = BoardScoreLine(hr)
          self._set_avg_mps_rps("n", hr.ns_score(), max_ns_mps, max_rps, bs)
          self._set_avg_mps_rps("e", hr.ew_score(), max_ew_mps, max_rps, bs)
          bs.ns_aps = 0
          bs.ew_aps = 0
          self._board_score.append(bs)

        self._board_score.sort(key = lambda bsl: bsl.ns_mps, reverse=True)
        return self._board_score

    def __str__(self):
        if (self._board_score):
            ret = ("""Board no {0} \nNS Pair   EW Pair     Calls      """ + 
                  """NS Score   EW Score   NS MPs   EW MPs   NS RPs   EW RPs \n""") \
                .format(self._board_no)
            for bs in self._board_score:
                hr = bs.hr()
                ret += str(bs)
            return ret
        else:
            return "Score has not been calculated for board " + \
                   str(self._board_no) + " or no hands are involved"
                   
    def csv_str(self):
      if (self._board_score):
            ret = ("Board no {0}\n""").format(self._board_no)
            for bs in self._board_score:
                ret += bs.csv_str()
            return ret
      else:
            return "Score has not been calculated for board " + \
                   str(self._board_no) + " or no hands are involved"
                   
    def csv_rows(self):
      board_no = "Board No"
      if (self._board_score):
          ret = []
          ret.append({board_no: ("Board {0}""").format(self._board_no), })
          for bs in self._board_score:
            ret.append(bs.csv_row())
          return ret
      else:
            return "Score has not been calculated for board " + \
                   str(self._board_no) + " or no hands are involved"

class TeamSummary:
    def __init__(self, team_no):
        self.mps = 0
        self.rps = 0
        self.aps = 0
        self.team_no = team_no
        self.board_mps = {}
        self.board_rps = {}
        self.board_aps = {}
        self.mp_rank = 0
        self.agg_rank = 0
        self.rp_rank = 0

    def UpdateSitOutBonuses(self, num_rounds):
        if len(self.board_mps) < num_rounds:
          self.mps = self.mps * float(num_rounds) / len(self.board_mps)
          self.aps = self.aps * float(num_rounds) / len(self.board_mps)
          self.rps = self.rps * float(num_rounds) / len(self.board_mps)
          
      
    def csv_rows(self, num_rounds):
        board_no = "Board No"
        mps = "MPs"
        rps = "RPs"
        ret = []
        ret.append({board_no:
            """Place {1}. Team {0}: MPs {2:.1f} RPs {3:.2f}""".format(self.team_no, self.mp_rank, self.mps, self.rps)})
        keys = sorted(self.board_mps.keys())
        for key in keys:
          ret.append({board_no : key, mps: self.board_mps[key], rps : self.board_rps[key]})
        if len(self.board_mps) < num_rounds:
          ret.append({board_no : "Sit-out Bonus",
                      mps: self.mps - self.mps * len(self.board_mps) / num_rounds,
                      rps: self.rps - self.rps * len(self.board_mps) / num_rounds})
        return ret
        

def UpdateTeamSummary(team_summaries, board_no, pair_no, position,
                      board_score_line):
    ts = team_summaries.setdefault(pair_no, TeamSummary(pair_no))
    assert(board_no not in ts.board_mps)
    assert(board_no not in ts.board_rps)
    assert(board_no not in ts.board_aps)
    if position is "ns": 
      mps = board_score_line.ns_mps
      rps = board_score_line.ns_rps
      aps = board_score_line.ns_aps
    elif position is "ew":
      mps = board_score_line.ew_mps
      rps = board_score_line.ew_rps
      aps = board_score_line.ew_aps
    ts.mps += mps
    ts.rps += rps
    ts.aps += aps
    ts.board_mps[board_no] = mps
    ts.board_rps[board_no] = rps
    ts.board_aps[board_no] = aps

def Calculate(boards, num_rounds):
    """ Boards is a list of Boards """

    team_summaries = {}
    for bs in boards:
        for bsl in bs.ScoreBoard():
            hr = bsl.hr()
            UpdateTeamSummary(team_summaries, hr._board_no, hr.ns_pair_no(),
                              "ns", bsl)
            UpdateTeamSummary(team_summaries, hr._board_no, hr.ew_pair_no(),
                              "ew", bsl)
    for ts in team_summaries.values():
      ts.UpdateSitOutBonuses(num_rounds)
      
    ret = team_summaries.values()
    
    # Calculate Ranks.
    # MP:
    OrderBy(ret, "MP")
    for i in range(len(ret)):
      ret[i].mp_rank = i + 1 
    
    # RP:
    OrderBy(ret, "RP")
    for i in range(len(ret)):
      ret[i].rp_rank = i + 1 
    
    # AP:
    OrderBy(ret, "AP")
    for i in range(len(ret)):
      ret[i].ap_rank = i + 1 

    return ret

def OrderBy(boards, rank_by = "MP"):
  if rank_by == "MP":
    # Secondary sort by rps.
    boards.sort(key=lambda ts : ts.rps, reverse = True) 
    boards.sort(key=lambda ts : ts.mps, reverse = True)
  elif rank_by == "RP":
    # Secondary sort by mps.
    boards.sort(key=lambda ts : ts.mps, reverse = True)
    boards.sort(key=lambda ts : ts.rps, reverse = True) 
  elif rank_by == "AP":
    # Secondary sort by mps.
    boards.sort(key=lambda ts : ts.mps, reverse = True)
    boards.sort(key=lambda ts : ts.aps, reverse = True) 
  else:
    raise KeyError("Bad error %s" % rank_by)
    
def GetMaxRounds(board_list):
  """ Gets the maximum number of rounds any team has played in the tournament. """
  if not board_list:
    return 0
  board_counts = {}
  for bs in board_list:
    for bsl in bs.ScoreBoard():
      hr = bsl.hr()
      board_counts[hr.ns_pair_no()] = 1 + board_counts.get(hr.ns_pair_no(), 0)
      board_counts[hr.ew_pair_no()] = 1 + board_counts.get(hr.ew_pair_no(), 0)
  return max(board_counts.values())


