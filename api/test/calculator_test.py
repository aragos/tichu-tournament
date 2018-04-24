import json
import unittest
import webtest
import os

import python.calculator
from calculator import Calculate
from calculator import OrderBy
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
    hand_results.append(HandResult(1, 9, 10, 'AVG', 'AVG--',
      Calls("", "", "", "")))
    hand_results.append(HandResult(1, 11, 12, 'AVG++', 'AVG-', 
      Calls("", "", "", "")))
    hand_results.append(HandResult(1, 13, 14, 'AVG+', 'AVG+',
      Calls("", "", "", "")))
    boards = [Board(1, hand_results)]
    team_summaries = Calculate(boards, 1)
    OrderBy(team_summaries, "MP")
    self.compareStats(team_summaries[0], 1, 11, 4.8, 3.21, 0)
    self.compareStats(team_summaries[1], 2, 1, 4.5, 5.35, 5)
    self.compareStats(team_summaries[2], 3, 6, 4.5, 4.51, 0)
    self.compareStats(team_summaries[3], 4, 13, 3.6, 1.07, 0)
    self.compareStats(team_summaries[4], 5, 14, 3.6, 1.07, 0)
    self.compareStats(team_summaries[5], 6, 4, 3.5, 4.26, 0)
    self.compareStats(team_summaries[6], 7, 7, 3.5, -3.93, 0)
    self.compareStats(team_summaries[7], 8, 9, 3, 0, 0)
    self.compareStats(team_summaries[8], 9, 8, 2.5, 3.93, 3)
    self.compareStats(team_summaries[9], 10, 3, 2.5, -4.26, 2)
    self.compareStats(team_summaries[10], 11, 12, 2.4, -1.07, 0)
    self.compareStats(team_summaries[11], 12, 5, 1.5, -4.51, 0)
    self.compareStats(team_summaries[12], 13, 2, 1.5, -5.35, 0)
    self.compareStats(team_summaries[13], 14, 10, 1.2, -3.21, 0)

  # For regression purposes. Hand with a bug in 2018-04-22 Tournament.
  def testMPs_avg2(self):
    hand_results = []
    hand_results.append(HandResult(6, 11, 4, 70, -170, Calls("", "", "", "GT")))
    hand_results.append(HandResult(6, 6, 9, 180, 20, Calls("T", "", "", "")))
    hand_results.append(HandResult(6, 5, 10, 'AVG', 'AVG', Calls("", "", "", "")))
    hand_results.append(HandResult(6, 1, 3, 15, 85, Calls("", "", "", "")))
    hand_results.append(HandResult(6, 8, 7, -35, 235,
      Calls("", "T", "GT", "")))
    boards = [Board(6, hand_results)]
    team_summaries = Calculate(boards, 1)
    OrderBy(team_summaries, "MP")
    self.compareStats(team_summaries[0], 1, 7, 3.5, 5.66, 4)
    self.compareStats(team_summaries[1], 2, 11, 3.5, 5.42, 0)
    self.compareStats(team_summaries[2], 3, 6, 2.5, 4.98, 2)
    self.compareStats(team_summaries[3], 4, 3, 2.5, 4.45, 0)
    self.compareStats(team_summaries[4], 5, 5, 2, 0, 0)
    self.compareStats(team_summaries[5], 6, 10, 2, 0, 0)
    self.compareStats(team_summaries[6], 7, 1, 1.5, -4.45, 0)
    self.compareStats(team_summaries[7], 8, 9, 1.5, -4.98, 0)
    self.compareStats(team_summaries[8], 9, 4, .5, -5.42, 4)
    self.compareStats(team_summaries[9], 10, 8, .5, -5.66, 2)

  def compareStats(self, ts, place, team_no, mps, rps, aps):
    self.assertEqual(place, ts.mp_rank)
    self.assertEqual(team_no, ts.team_no)
    self.assertAlmostEqual(mps, ts.mps, delta=0.01)
    self.assertAlmostEqual(rps, ts.rps, delta=0.01)
    self.assertEqual(aps, ts.aps)