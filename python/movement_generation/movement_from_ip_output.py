#!/usr/bin/python

### This program generates a fair movement from AMPL output to a fairness IP 
### based on an existing movement.
### Example commandline: 
### python movement_from_ip_output.py  -m \
###    <path to an existing movement> -a ampl_output.txt -o <output file>
###
### If -o is noo specified, the input movement is overwritten.
### ampl_output.txt should contain the AbsolutePosition matrix from the output
### of an AMPL run with no titles or any other text.

import json
import os
import sys, getopt
from collections import defaultdict
import math

def ReadAmplOutputMatrix(ampl_data):
  '''Returns a dict showing when a pair is facing North.
  
     Dict has format {int: [int]} where key is a pair number and the value is
     the list of hand set identifiers where the pair is facing North.
     
     This method reads the AbsolutePosition AMPL output matrix.
  '''
  absolute_positions = defaultdict(list)
  team_key = -1;
  hand_set_column_name = []
  pair = 0
  for line in ampl_data:
    values = line.rstrip().split(" ")
    if line.startswith(":"):
      continue
    pair+=1
    filtered_values = [x for x in values if x != "" and x != " "]
    for i in range(1, len(filtered_values)):
      if filtered_values[i] == "1":
        absolute_positions[pair].append(i)
  return absolute_positions


def GetNumHandsPerRound(movement):
  '''Determines the number of hands played in each round'''
  for (pair, pair_movements) in movement.items():
    for round in pair_movements:
      if not round.get('hands', None):
        continue; 
      return len(round['hands'])


def SetCurrentHandPositions(my_direction, me, opponent, round_no,
                            movement, used_tables_per_round):
  ''' Finds the next unused table in this round and sets the positions of 
      players for this hand. MOdifies used_tables_per_round with the used
      table.
  '''
  for table_no in xrange(1, int(math.floor(len(movement) / 2)) + 1):
    if table_no not in used_tables_per_round[round_no]:
      used_tables_per_round[round_no].append(table_no)
      movement[str(me)][round_no - 1]['position'] = str(table_no) + my_direction
      movement[str(opponent)][round_no - 1]['position'] = str(table_no) + "N" if my_direction == "E" else str(table_no) + "E"
      return


def main(argv):
  inputfile = ''
  outputfile = ''
  opts, args = getopt.getopt(argv, "a:o:m:n:")
  for opt, arg in opts:
      if opt in ("-m", "--movementfile"):
        input_movement_file = arg
      if opt in ("-a", "--amplfile"):
        input_ampl_file = arg
      elif opt in ("-o", "--ofile"):
        outputfile = arg
  json_data=open(os.path.join(os.getcwd(), input_movement_file)).read()
  ampl_data=open(os.path.join(os.getcwd(), input_ampl_file))

  movement = json.loads(json_data)
  absolute_positions = ReadAmplOutputMatrix(ampl_data)
  used_tables_per_round = defaultdict(list)
  num_hands_per_round = GetNumHandsPerRound(movement)
  for pair in xrange(1, len(movement)+1):
    for round in movement[str(pair)]:
      if not round.get('opponent', None):
        continue
      opponent = round['opponent']
      hands = round['hands']
      if opponent > pair:
        hand_set_identifier = hands[num_hands_per_round - 1] / num_hands_per_round
        direction = "N" if hand_set_identifier in absolute_positions[int(pair)] else "E"
        SetCurrentHandPositions(direction, int(pair), opponent, round['round'], 
                                movement, used_tables_per_round)

  if outputfile == "": 
    output = open(os.path.join(os.getcwd(), input_movement_file), "w")
  else:
    output = open(os.path.join(os.getcwd(), outputfile), "w")
  output.write(json.dumps(movement, sort_keys=True, indent = 2))
  output.close()


if __name__ == "__main__":
   main(sys.argv[1:])