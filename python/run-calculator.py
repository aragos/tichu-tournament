#!/usr/bin/python

from calculator import Calculate
from calculator import OrderBy
from calculator import GetMaxRounds
import xlsxio
import sys, getopt
      
def main(argv):
  inputfile = ''
  outputfile = ''
  opts, args = getopt.getopt(argv, "i:o:n:")
  for opt, arg in opts:
      if opt in ("-i", "--ifile"):
        inputfile = arg
      elif opt in ("-o", "--ofile"):
        outputfile = arg
  
  input_wb, board_list = xlsxio.ReadXlsxInput(inputfile)
  max_rounds = GetMaxRounds(board_list)
  summaries = Calculate(board_list, max_rounds)
  mp_summaries = summaries
  ap_summaries = summaries
  board_list.sort(key=lambda bs : bs._board_no, reverse = False)
  wb = xlsxio.WriteResultsToXlsx(max_rounds, mp_summaries, ap_summaries,
                                 board_list, input_wb)                       
  wb.save(outputfile)

if __name__ == "__main__":
   main(sys.argv[1:])