import itertools
import math

class InvalidCallError(Exception):
    def __init__(self, call, side):
         self.value = "Invalid call value " + call + " from " + side
    def __str__(self):
        return repr(self.value)
        
class InvalidScoreError(Exception):
    def __init__(self, board_no, ns_pair_no, ew_pair_no):
         self.value = "Invalid score: for board no: " + str(board_no) +\
             ", pairs: " + str(ns_pair_no) + ", and " + str(ew_pair_no)
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

class HandResult:
    """ Contains all information about a single hand between two teams. """
    
    def __init__(self, board_no, ns_pair_no, ew_pair_no, ns_score, ew_score,
                 calls):
        """ So far doesn't deal with avg, avg+, or avg- """
        self._ns_pair_no = ns_pair_no
        self._ew_pair_no = ew_pair_no
        self._ns_score = ns_score
        self._ew_score = ew_score
        self._calls = calls
        self._diff = ns_score - ew_score
        self._board_no = board_no
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
        permutations = itertools.permutations(["N", "W", "S", "E"])
        for permutation in permutations:
            if self._IsScoreValid(permutation):
                return
        raise InvalidScoreError(self._board_no, self._ns_pair_no,
                                self.ew_pair_no)

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
        ns_bounds = [x + ns_tichu_factor for x in ns_bounds]
        ew_bounds = [x + ew_tichu_factor for x in ew_bounds]
        
        if (self._ns_score not in range(ns_bounds[0], ns_bounds[1] + 1) or
            self._ew_score not in range(ew_bounds[0], ew_bounds[1] + 1)):
            return False
        return True

class BoardScoreLine:
    def __init__(self, hr):
        self._hr = hr
    
    def hr(self):
        return self._hr
        
    def __str__(self):
        if ((self.ns_mps + self.ew_mps + self.ns_rps + self.ew_rps)):
            return ("{0:4d} {1:9d}     {2:s} {3:10d} {4:10d}      {5:.1f}"\
                    "      {6:.1f}     {7:.2f}    {8:.2f}\n")\
                .format(self._hr.ns_pair_no(), self._hr.ew_pair_no(), 
                        str(self._hr.calls()), self._hr.ns_score(),
                        self._hr.ew_score(), self.ns_mps, self.ew_mps,
                        self.ns_rps, self.ew_rps)
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
        return sum([x.diff() for x in self._hand_results])/len(self._hand_results)

    def _log_rps(self, rps):
        if rps > 0:
            return math.log1p(rps)
        else: 
            return -math.log1p(-rps)

    def _mp_comp(self, current, other):
        if current < other:
            return 0
        if current == other:
            return 0.5
        return 1
        
    def ScoreBoard(self): 
        self._board_score = []
        self._hand_results.sort(key=lambda hr: hr.diff(), reverse=True)
        avg_score = self._get_avg_score_diff()
        # This is n^2. You can do it in O(n) but will be uglier. Since
        # we will have 4/5 entries each time, this is OK.
        iter = self._hand_results
        for hr in iter:
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
            self._board_score.append(bs)
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

class TeamSummary:
    def __init__(self, team_no):
        self.mps = 0
        self.rps = 0
        self.team_no = team_no
        self.board_mps = {}
        self.board_rps = {}
        self.rank = ""
        
    def __str__(self):
        ret = ("""Team {0} Rank {1} MPs {2} RPs {3} \nBoard no MPs RPs\n""") \
                .format(self.team_no, self.rank, self.mps, self.rps)
        keys = sorted(self.board_mps.keys())
        for key in keys:
          ret += "{0} {1} {2}\n".format(key, self.board_mps[key], 
                                        self.board_rps[key])
        return ret

def UpdateTeamSummary(team_summaries, board_no, pair_no, mps, rps): 
    ts = team_summaries.setdefault(pair_no, TeamSummary(pair_no))
    ts.mps += mps
    ts.rps += rps
    assert(board_no not in ts.board_mps)
    assert(board_no not in ts.board_rps)
    ts.board_mps[board_no] = mps
    ts.board_rps[board_no] = rps

def Calculate(boards, rank_by = "MP"):
    """ Boards is a list of Boards """

    team_summaries = {}
    for bs in boards:
        for bsl in bs.ScoreBoard():
            hr = bsl.hr()
            UpdateTeamSummary(team_summaries, hr._board_no, hr.ns_pair_no(),
                              bsl.ns_mps, bsl.ns_rps)
            UpdateTeamSummary(team_summaries, hr._board_no, hr.ew_pair_no(),
                              bsl.ew_mps, bsl.ew_rps)
    
    ret = team_summaries.values()
    if rank_by == "MP" :
        # Secondary sort by rps.
        ret.sort(key=lambda ts : ts.rps, reverse = True) 
        ret.sort(key=lambda ts : ts.mps, reverse = True)
    elif rank_by == "RP":
        # Secondary sort by mps.
        ret.sort(key=lambda ts : ts.mps, reverse = True)
        ret.sort(key=lambda ts : ts.rps, reverse = True) 
    return ret
