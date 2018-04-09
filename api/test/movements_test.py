import json
import unittest
import webtest
import os

from api.src import movements

class MovementTest(unittest.TestCase):
  def testConsistentOpponents_ten_three(self):
    movement = movements.Movement.CreateMovement(10, 3, 7)
    self.checkConsistentSchedule(movement, 10, 3)
    self.checkConsistentOpponents(movement, 10, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 10, 3)
    self.checkTableConsistency(movement, 10, 3)
    self.checkPrepareHands(movement, 10, 24)
    self.checkNumRounds(movement, 10, 7)

  def testConsistentOpponents_ten_two(self):
    movement = movements.Movement.CreateMovement(10, 2, 7)
    self.checkConsistentSchedule(movement, 10, 2)
    self.checkConsistentOpponents(movement, 10, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 10, 2)
    self.checkTableConsistency(movement, 10, 2)
    self.checkPrepareHands(movement, 10, 16)
    self.checkNumRounds(movement, 10, 7)

  def testConsistentOpponents_nine_two_eight(self):
    movement = movements.Movement.CreateMovement(9, 2, 8)
    self.checkConsistentSchedule(movement, 9, 2)
    self.checkConsistentOpponents(movement, 9, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 9, 2)
    self.checkTableConsistency(movement, 9, 2)
    self.checkPrepareHands(movement, 9, 18)
    self.checkNumRounds(movement, 9, 9)

  def testConsistentOpponents_nine_three_eight(self):
    movement = movements.Movement.CreateMovement(9, 3, 8)
    self.checkConsistentSchedule(movement, 9, 3)
    self.checkConsistentOpponents(movement, 9, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 9, 3)
    self.checkTableConsistency(movement, 9, 3)
    self.checkPrepareHands(movement, 9, 27)
    self.checkNumRounds(movement, 9, 9)
    
  def testConsistentOpponents_nine_two_seven(self):
    movement = movements.Movement.CreateMovement(9, 2, 7)
    self.checkConsistentSchedule(movement, 9, 2)
    self.checkConsistentOpponents(movement, 9, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 9, 2)
    self.checkTableConsistency(movement, 9, 2)
    self.checkPrepareHands(movement, 9, 14)
    self.checkNumRounds(movement, 9, 7)

  def testConsistentOpponents_nine_three_seven(self):
    movement = movements.Movement.CreateMovement(9, 3, 7)
    self.checkConsistentSchedule(movement, 9, 3)
    self.checkConsistentOpponents(movement, 9, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 9, 3)
    self.checkTableConsistency(movement, 9, 3)
    self.checkPrepareHands(movement, 9, 21)
    self.checkNumRounds(movement, 9, 7)
 
  def testConsistentOpponents_eight_two_six(self):
    movement = movements.Movement.CreateMovement(8, 2, 6)
    self.checkConsistentSchedule(movement, 8, 2)
    self.checkConsistentOpponents(movement, 8, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 8, 2)
    self.checkTableConsistency(movement, 8, 2)
    self.checkPrepareHands(movement, 8, 16)
    self.checkNumRounds(movement, 8, 6)

  def testConsistentOpponents_eight_three_six(self):
    movement = movements.Movement.CreateMovement(8, 3, 6)
    self.checkConsistentSchedule(movement, 8, 3)
    self.checkConsistentOpponents(movement, 8, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 8, 3)
    self.checkTableConsistency(movement, 8, 3)
    self.checkPrepareHands(movement, 8, 24)
    self.checkNumRounds(movement, 8, 6)
 
  def testConsistentOpponents_seven_two_seven(self):
    movement = movements.Movement.CreateMovement(7, 2, 7)
    self.checkConsistentSchedule(movement, 7, 2)
    self.checkConsistentOpponents(movement, 7, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 7, 2)
    self.checkTableConsistency(movement, 7, 2)
    self.checkPrepareHands(movement, 7, 14)
    self.checkNumRounds(movement, 7, 7)
 
  def testConsistentOpponents_seven_three_seven(self):
    movement = movements.Movement.CreateMovement(7, 3, 7)
    self.checkConsistentSchedule(movement, 7, 3)
    self.checkConsistentOpponents(movement, 7, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 7, 3)
    self.checkTableConsistency(movement, 7, 3)
    self.checkPrepareHands(movement, 7, 21)
    self.checkNumRounds(movement, 7, 7)
    
  def testConsistentOpponents_eleven_two_seven(self):
    movement = movements.Movement.CreateMovement(11, 2, 7)
    self.checkConsistentSchedule(movement, 11, 2)
    self.checkConsistentOpponents(movement, 11, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 11, 2)
    self.checkTableConsistency(movement, 11, 2)
    self.checkPrepareHands(movement, 11, 14)
    self.checkNumRounds(movement, 11, 7)

  def testConsistentOpponents_eleven_three_seven(self):
    movement = movements.Movement.CreateMovement(11, 3, 7)
    self.checkConsistentSchedule(movement, 11, 3)
    self.checkConsistentOpponents(movement, 11, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 11, 3)
    self.checkTableConsistency(movement, 11, 3)
    self.checkPrepareHands(movement, 11, 21)
    self.checkNumRounds(movement, 11, 7)
    
  def testConsistentOpponents_twelve_three_five(self):
    movement = movements.Movement.CreateMovement(12, 3, 5)
    self.checkConsistentSchedule(movement, 12, 3)
    self.checkConsistentOpponents(movement, 12, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 12, 3)
    self.checkTableConsistency(movement, 12, 3)
    self.checkPrepareHands(movement, 12, 18)
    self.checkNumRounds(movement, 12, 5)

  def testConsistentOpponents_eleven_two_seven_max_six(self):
    movement = movements.Movement.CreateMovement(11, 2, 6)
    self.checkConsistentSchedule(movement, 11, 2)
    self.checkConsistentOpponents(movement, 11, 2)
    self.checkHandsPlayedRightNumberOfTimes(movement, 11, 2)
    self.checkTableConsistency(movement, 11, 2)
    self.checkPrepareHands(movement, 11, 16)
    self.checkNumRounds(movement, 11, 7)

  def testConsistentOpponents_eleven_three_seven_max_six(self):
    movement = movements.Movement.CreateMovement(11, 3, 6)
    self.checkConsistentSchedule(movement, 11, 3)
    self.checkConsistentOpponents(movement, 11, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 11, 3)
    self.checkTableConsistency(movement, 11, 3)
    self.checkPrepareHands(movement, 11, 24)
    self.checkNumRounds(movement, 11, 7)

  def testConsistentOpponents_six_three_five(self):
    movement = movements.Movement.CreateMovement(6, 3, 5)
    self.checkConsistentSchedule(movement, 6, 3)
    self.checkConsistentOpponents(movement, 6, 3)
    self.checkHandsPlayedRightNumberOfTimes(movement, 6, 3)
    self.checkTableConsistency(movement, 6, 3)
    self.checkNumRounds(movement, 6, 5)

  def testConsistentOpponents_six_four_five(self):
    movement = movements.Movement.CreateMovement(6, 4, 5)
    self.checkConsistentSchedule(movement, 6, 4)
    self.checkConsistentOpponents(movement, 6, 4)
    self.checkHandsPlayedRightNumberOfTimes(movement, 6, 4)
    self.checkTableConsistency(movement, 6, 4)
    self.checkNumRounds(movement, 6, 5)

  def testConsistentOpponents_five_four_five(self):
    movement = movements.Movement.CreateMovement(5, 4, 5)
    self.checkConsistentSchedule(movement, 5, 4)
    self.checkConsistentOpponents(movement, 5, 4)
    self.checkHandsPlayedRightNumberOfTimes(movement, 5, 4)
    self.checkTableConsistency(movement, 5, 4)
    self.checkNumRounds(movement, 5, 5)

  def checkConsistentSchedule(self, movement, num_pairs, num_hands_per_round):
    for i in range(num_pairs):
      opponents_played = set()
      hands_played = set()
      rounds_played = set()
      for round in movement.GetMovement(i + 1):
        self.assertIsNotNone(round)
        if not round.hands:
          continue
        opp = round.opponent
        self.assertIsNotNone(opp)
        self.assertFalse(opp in opponents_played,
                         msg="Opponent {} for pair {} is played more than once".format(
                             opp, i + 1))
        opponents_played.add(opp)

        round_no = round.round
        self.assertIsNotNone(round_no)
        self.assertFalse(round_no in rounds_played,
                         msg="Round {} for pair {} is played more than " + 
                             "once".format(round_no, i + 1))
        rounds_played.add(round_no)

        hands = round.hands
        self.assertIsNotNone(hands)
        self.assertEqual(num_hands_per_round, len(hands),
                         msg="Round {} for pair {} has {} hands. Expected {}".format(
                             round_no, i + 1, len(hands), num_hands_per_round))
        for hand in hands:
          self.assertFalse(hand in hands_played, 
                           msg=("Hand {} for pair {} is played more than " + 
                               "once").format(hand, i + 1))
          hands_played.add(hand)
        table = round.table
        self.assertTrue(table <= num_pairs/2, 
                        msg="Invalid table specification {} for pair {}".format(
                            table, i + 1))

  def checkConsistentOpponents(self, movement, num_pairs, num_hands_per_round):
    for i in range(num_pairs):
      for round in movement.GetMovement(i + 1):
        hands = round.hands
        if not hands:
          continue
        round_no = round.round
        opp = round.opponent
        opp_movement = movement.GetMovement(opp)
        table = round.table
        found_match = False
        for opp_round in opp_movement:
          if round_no != opp_round.round:
            continue
          found_match = True
          self.assertEqual(hands, opp_round.hands, 
                           msg=("Round {} hands for pair {} are inconsistent " + 
                               "with opponent pair {}'s hands").format(
                                   round_no, i+1, opp))
          self.assertEqual(i + 1, opp_round.opponent,
                           msg=("Round {} opponent for pair {} is inconsistent " + 
                               "with pair {}").format(round_no, i + 1, opp))
          self.assertEqual(table, opp_round.table,
                           msg=("Pair {} and pair {} seem to be sitting at " + 
                               "different tables for round {}").format(
                                   i + 1, opp, round_no))
          self.assertNotEqual(round.is_north, opp_round.is_north,
                              msg=("Pair {} and pair {} seem to be sitting in " +
                                  "the same seat for round {}").format(
                                      i + 1, opp, round_no))
        self.assertTrue(found_match,
                        msg="Opponent {} of Pair {} doesn't seem to have them for round {}".format(
                            opp, i + 1, round_no))
  
  def checkHandsPlayedRightNumberOfTimes(self, movement, num_pairs,
                                         num_hands_per_round):
    non_relay_hands = {}
    relay_hands = {}
    total_times_played = {}
    for i in range(num_pairs):
      for round in movement.GetMovement(i + 1):
        round_no = round.round
        hands = round.hands
        if not hands:
          continue
        if round.relay_table:
          for hand in hands:
            if not relay_hands.get(round_no):
              relay_hands[round_no] = {}
            relay_hands[round_no][hand] = relay_hands[round_no].get(hand, 0) + 1
            total_times_played[hand] = total_times_played.get(hand, 0) + 1
        else: 
          for hand in hands:
            if not non_relay_hands.get(round_no):
              non_relay_hands[round_no] = {}
            non_relay_hands[round_no][hand] = non_relay_hands[round_no].get(
                hand, 0) + 1
            total_times_played[hand] = total_times_played.get(hand, 0) + 1
    
    for r, hl in non_relay_hands.items():
      for h, n in hl.items():
        self.assertEqual(2, n,
                         msg=("Non relay hand {} is played {} times in round " + 
                             "{}").format(h, n, r))
        self.assertTrue((not relay_hands.get(r)) or (not relay_hands[r].get(h)), 
                        msg="Non relay hand {} is present in relay table in round {}".format(h, r))

    for r, hl in relay_hands.items():
      for h, n in hl.items():
        self.assertTrue(n > 2,
                        msg=("Relay hand {} is played only {} times in round " + 
                            "{}. Must be > 2.").format(h, n, r))
        self.assertTrue(n % 2 == 0,
                        msg=("Relay hand {} is played {} times in round {}. " + 
                            "Must be divisible by 2").format(h, n, r))
        self.assertTrue((not non_relay_hands.get(r)) or (not non_relay_hands[r].get(h)), 
                        msg="Relay hand {} is present in non-relay table".format(h))
    first_number_played = total_times_played[1]
    for h, n in total_times_played.items():
      self.assertEqual(first_number_played, n, 
                       msg=("Hand {} is played {} times, wheras hand 1 is " + 
                           "played {} times.").format(h, n, first_number_played))

  def checkTableConsistency(self, movement, num_pairs, num_hands_per_round):
    positions = {}
    for i in range(num_pairs):
      for round in movement.GetMovement(i + 1):
        if not round.table:
          continue
        round_no = round.round
        table = round.table
        if not positions.get(table):
          positions[table] = {round_no : [i + 1]}
        else:
          positions[table][round_no] = positions[table].get(round_no, []) + [i + 1]
          
    for t, rt in positions.items():
      for r, n in rt.items():
        self.assertEqual(2, len(n), 
                         msg=("Table {} hosts a weird number of teams ({}) in " + 
                             "round {}.").format(t, n, r))

  def checkNumRounds(self, movement, num_pairs, total_rounds):
    for i in range(num_pairs):
      self.assertEqual(total_rounds, len(movement.GetMovement(i + 1)),
                       msg=("Pair {} has a wrong total number of rounds. " + 
                            "Expected {}, was {}").format(
                                i + 1, total_rounds,
                                len(movement.GetMovement(i + 1))))
      round_counter = 1
      for round in movement.GetMovement(i + 1):
        self.assertEqual(round_counter, round.round,
                       msg=("Pair {}'s {}th round, has number {}. ").format(
                                i + 1, round_counter, round.round))
        round_counter += 1

  def _handPreparedBySomeone(self, hand_no, movement, num_pairs):
    for j in range(num_pairs):
      if hand_no in movement.GetSuggestedHandPrep(j + 1):
        return True
    return False

  def checkPrepareHands(self, movement, num_pairs, num_boards):
    for i in range(num_pairs):
      prepare_list = movement.GetUnplayedHands(i + 1)
      for round in movement.GetMovement(i + 1):
        hands = round.hands
        for j in prepare_list:
          self.assertFalse(j in hands, 
                           msg=("Pair {} prepares hand {} that it also plays " + 
                                "in round {}").format(i + 1, j, round.round))
    for i in range(num_boards):
      self.assertTrue(self._handPreparedBySomeone(i + 1, movement, num_pairs),
                      msg="Hand number {} not prepared by anyone".format(i + 1))
                      
    
