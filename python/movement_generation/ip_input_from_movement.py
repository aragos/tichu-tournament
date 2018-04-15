#!/usr/bin/python

### This program generates an AMPL input to a fairness IP based on an existing 
### movement. 
### Example commandline: 
### python ip_input_from_movement.py  -i \
###    <path to an existing movement> -o ampl_data.txt
###  
### After this is finished, use submit ample_data.txt, model.mod and command.txt
### to https://neos-server.org/neos/solvers/lp:Gurobi/AMPL.html.

import json
import os
import sys, getopt
from collections import defaultdict


def GetNumHandsPerRound(movement):
  '''Determines the number of hands played in each round'''
  for (pair, pair_movements) in movement.items():
    for round in pair_movements:
      if not round.get('hands', None):
        continue; 
      return len(round['hands'])


def GetHandToPairsDict(movement, num_hands_per_round):
  '''Returns a dict of mappings from hand set no to pairs that played it.
  
    Note that hand set identifier is not a hand number. It is the ordered number
    of the set of hands played by one set of opponents during one round. i.e.
    [1, 2, 3] is set 1, [4, 5, 6] is set 2.
    Returned dict has signature {int: [int]}. Values are guaranteed to be sorted.
  '''
  hand_to_pairs = defaultdict(list)
  for (pair, pair_movements) in movement.items():
    for round in pair_movements:
      if not round.get('opponent', None):
        continue;
      hand_set_identifier = round['hands'][num_hands_per_round - 1] / num_hands_per_round
      hand_to_pairs[hand_set_identifier].append(int(pair))
  for (k, v) in hand_to_pairs.items():
    v.sort()
  return hand_to_pairs

def main(argv):
  inputfile = ''
  outputfile = ''
  opts, args = getopt.getopt(argv, "i:o:n:")
  for opt, arg in opts:
      if opt in ("-i", "--ifile"):
        inputfile = arg
      elif opt in ("-o", "--ofile"):
        outputfile = arg
  json_data=open(os.path.join(os.getcwd(), inputfile)).read()
  output = open(os.path.join(os.getcwd(), outputfile), "w")

  movement = json.loads(json_data)

  num_hands_per_round = GetNumHandsPerRound(movement)
  hand_to_pairs = GetHandToPairsDict(movement, num_hands_per_round)
  max_boards = max(hand_to_pairs.keys())
      
  output.write('param MaxBoards := {};\n'.format(max_boards))
  output.write('param MaxOpponents := {};\n'.format(str(len(movement))))

  output.write('set eligible_comparisons := ')
  for (pair, pair_movements) in movement.items():
    for round in pair_movements:
      if not round.get('opponent', None):
        continue; 
      hand_set_identifier = round['hands'][num_hands_per_round - 1] / num_hands_per_round
      opp = round['opponent']
      for p in hand_to_pairs[hand_set_identifier]:
        if p > int(pair) and p != opp:
          output.write('({}, {}, {}) '.format(pair, p, hand_set_identifier))

  output.write(';\nset played_boards := ')
  for (pair, pair_movements) in movement.items():
    for round in pair_movements:
      if not round.get('opponent', None):
        continue; 
      hand_set_identifier = round['hands'][num_hands_per_round - 1] / num_hands_per_round
      opp = round['opponent']
      if opp > int(pair):
        output.write('({}, {}, {}) '.format(pair, opp, hand_set_identifier))
  output.write(';')
  output.close()


if __name__ == "__main__":
   main(sys.argv[1:])