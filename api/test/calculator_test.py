import json
import unittest
import webtest
import os

import python.calculator
from calculator import Calculate
from calculator import OrderBy
from calculator import GetMaxRounds
from calculator import Board
from calculator import HandResult
from calculator import Calls
from calculator import OrderBy

class CalculatorTest(unittest.TestCase):
  def testMPs_one_hand(self):
    hand_results = []
    hand_results.append(HandResult(1, 1, 2, 400, 0, Calls("GT", "", "", "")))
    hand_results.append(HandResult(1, 3, 4, 150, 50, Calls("T", "", "", "")))
    hand_results.append(HandResult(1, 5, 6, 100, 0, Calls("", "", "", "")))
    hand_results.append(HandResult(1, 7, 8, 70, -70, Calls("", "", "T", "")))
    boards = [Board(1, hand_results)]
    hand_results = []
    hand_results.append(HandResult(2, 1, 3, 400, 0, Calls("GT", "", "", "")))
    hand_results.append(HandResult(2, 2, 7, 120, 80, Calls("T", "", "", "")))
    hand_results.append(HandResult(2, 4, 8, 300, 0, Calls("T", "", "", "")))
    hand_results.append(HandResult(2, 6, 5, 0, 300, Calls("", "", "T", "")))
    boards.append(Board(2, hand_results))
    team_summaries = Calculate(boards, 2)
    OrderBy(team_summaries, "MP")
    self.compareStats(team_summaries[0], 1, 1, 6, 11.05, 9)
    self.compareStats(team_summaries[1], 2, 4, 4.5, 9.70, 1)
    self.compareStats(team_summaries[2], 3, 7, 4, 0.43, 0)
    self.compareStats(team_summaries[3], 4, 5, 3.5, 1.56, 3)
    self.compareStats(team_summaries[4], 5, 6, 2.5, -1.56, 0)
    self.compareStats(team_summaries[5], 6, 8, 2, -1.42, 3)
    self.compareStats(team_summaries[6], 7, 2, 1, -9.63, 1)
    self.compareStats(team_summaries[7], 8, 3, 0.5, -10.13, 2)
    
  def testMPs_avg(self):
    hand_results = []
    hand_results.append(HandResult(1, 1, 2, 400, 0, Calls("GT", "", "", "")))
    hand_results.append(HandResult(1, 3, 4, 160, 40, Calls("T", "", "", "")))
    hand_results.append(HandResult(1, 5, 6, 100, 0, Calls("", "", "", "")))
    hand_results.append(HandResult(1, 7, 8, 70, -70, Calls("", "", "T", "")))
    hand_results.append(HandResult(1, 9, 10, 'AVG', 'AVG--', Calls("", "", "", "")))
    hand_results.append(HandResult(1, 11, 12, 'AVG++', 'AVG-', Calls("", "", "", "")))
    hand_results.append(HandResult(1, 13, 14, 'AVG+', 'AVG+', Calls("", "", "", "")))
    boards = [Board(1, hand_results)]
    team_summaries = Calculate(boards, 1)
    OrderBy(team_summaries, "MP")
    self.compareStats(team_summaries[0], 1, 1, 4.5, 5.35, 5)
    self.compareStats(team_summaries[1], 2, 6, 4.5, 4.51, 0)
    self.compareStats(team_summaries[2], 3, 11, 3.6, 3.21, 0)
    self.compareStats(team_summaries[3], 4, 4, 3.5, 4.26, 0)
    self.compareStats(team_summaries[4], 5, 7, 3.5, -3.93, 0)
    self.compareStats(team_summaries[5], 6, 13, 2.7, 1.07, 0)
    self.compareStats(team_summaries[6], 7, 14, 2.7, 1.07, 0)
    self.compareStats(team_summaries[7], 8, 8, 2.5, 3.93, 3)
    self.compareStats(team_summaries[8], 9, 3, 2.5, -4.26, 2)
    self.compareStats(team_summaries[9], 10, 9, 2.25, 0, 0)
    self.compareStats(team_summaries[10], 11, 12, 1.8, -1.07, 0)
    self.compareStats(team_summaries[11], 12, 5, 1.5, -4.51, 0)
    self.compareStats(team_summaries[12], 13, 2, 1.5, -5.35, 0)
    self.compareStats(team_summaries[13], 14, 10, 0.9, -3.21, 0)

  def compareStats(self, ts, place, team_no, mps, rps, aps):
    self.assertEqual(place, ts.mp_rank)
    self.assertEqual(team_no, ts.team_no)
    self.assertAlmostEqual(mps, ts.mps, delta=0.01)
    self.assertAlmostEqual(rps, ts.rps, delta=0.01)
    self.assertEqual(aps, ts.aps)