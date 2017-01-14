import requests
import json

PROD_TOURNEY_ID = 5649391675244544
TOURNEY_ID = 5629499534213120


PAIR_IDS = "pair_ids": [
    "CUTQ", 
    "OBRH", 
    "XJTW", 
    "YOTH", 
    "CEET", 
    "RBJS", 
    "LIRD", 
    "ADMC", 
    "TIQU", 
    "OHWX"
  ]

PROD_PAIR_IDS = [
    "VYOE", 
    "ZXWP", 
    "FVCX", 
    "ELYX", 
    "EWBR", 
    "TWBJ", 
    "BBDX", 
    "CMPC", 
    "BYDP", 
    "BLPM"
  ]
  
URL = "https://http://localhost:8080"

PROD_URL = "https://tichu-tournament.appspot.com"


def GetMovements(pair_no):
  headers = {
    "Content-Type": "application/json",
    'X-tichu-pair-code' : PAIR_IDS[pair_no - 1]
  }
  r = requests.get(URL + "/api/tournaments/{}/movement/{}".format(
      TOURNEY_ID, pair_no),
      headers=headers)
  r.raise_for_status()

def PutHand(hand_no, ns_pair, ew_pair, calls, ns_score, ew_score):
  headers = {
    "Content-Type": "application/json",
    'X-tichu-pair-code' : PAIR_IDS[ns_pair - 1]
  }
  info_dict = {
    "calls" : {
      "north" : calls[0],
      "south" : calls[1],
      "east" : calls[2],
      "west" : calls[3]
     },
    "ns_score" : ns_score,
    "ew_score" : ew_score
  }

  r = requests.put("http://tichu-tournament.appspot.com/api/tournaments/{}/hands/{}/{}/{}".format(
      TOURNEY_ID, hand_no, ns_pair, ew_pair),
      headers=headers,
      data=json.dumps(info_dict))
  r.raise_for_status()

PutHand(1, 3, 8, ["", '', '', '' ], 60, 40)
PutHand(1, 10, 4, ["", '', '', 'T' ], 55, 145)
PutHand(1, 5, 6, ["T", '', '', 'T' ], -30, 130)
PutHand(1, 9, 2, ["T", '', '', 'T' ], 300, -100)
PutHand(2, 3, 8, ["", 'T', 'T', '' ], -90, 190)
PutHand(2, 10, 4, ["", 'GT', '', '' ], 190, 110)
PutHand(2, 5, 6, ["", 'GT', '', '' ], 205, 95)
PutHand(2, 9, 2, ["", '', '', '' ], -5, 105)
PutHand(3, 10, 5, ["T", '', 'T', '' ], -60, 160)
PutHand(3, 9, 3, ["", '', 'T', '' ], 40, 160)
PutHand(3, 1, 4, ["", '', 'T', '' ], 65, 135)
PutHand(3, 6, 7, ["GT", '', '', '' ], 280, 20)
PutHand(4, 10, 5, ["", 'T', '', '' ], 195, 5)
PutHand(4, 9, 3, ["", 'T', '', '' ], 170, 30)
PutHand(4, 1, 4, ["T", '', '', '' ], 300, 0)
PutHand(4, 6, 7, ["", 'T', '', '' ], 135, 65)
PutHand(5, 6, 10, ["", '', '', 'T' ], 55, 145)
PutHand(5, 8, 7, ["", 'T', '', '' ], 185, 15)
PutHand(5, 2, 5, ["", '', '', 'T' ], 45, 155)
PutHand(5, 9, 4, ["", 'T', '', '' ], 170, 30)
PutHand(6, 6, 10, ["", 'T', '', '' ], 145, 55)
PutHand(6, 8, 7, ["", 'GT', '', '' ], -170, 70)
PutHand(6, 2, 5, ["", 'GT', '', '' ], 235, 65)
PutHand(6, 9, 4, ["", 'T', '', '' ], 80, 120)
PutHand(7, 5, 9, ["T", '', '', '' ], 110, 90)
PutHand(7, 8, 1, ["T", '', '', '' ], 160, 40)
PutHand(7, 7, 10, ["", '', '', 'T' ], 75, 125)
PutHand(7, 3, 6, ["", '', '', '' ], 60, 40)
PutHand(8, 5, 9, ["", '', '', 'GT' ], 40, -140)
PutHand(8, 8, 1, ["", '', '', '' ], 55, 45)
PutHand(8, 7, 10, ["", '', '', 'GT' ], 25, 275)
PutHand(8, 3, 6, ["", '', '', 'GT' ], 10, 290)
PutHand(9, 1, 2, ["", '', '', 'GT' ], 15, 285)
PutHand(9, 4, 7, ["", '', '', 'GT' ], 30, 270)
PutHand(9, 9, 6, ["", '', '', 'GT' ], 15, 285)
PutHand(9, 8, 10, ["", 'T', '', 'GT' ], 165, -165)
PutHand(10, 1, 2, ["", 'T', '', '' ], 180, 20)
PutHand(10, 4, 7, ["", '', 'GT', '' ], 80, 220)
PutHand(10, 9, 6, ["", 'T', 'GT', '' ], -20, 220)
PutHand(10, 8, 10, ["", '', 'GT', '' ], 100, -200)
PutHand(11, 2, 3, ["", '', '', 'T' ], 110, 90)
PutHand(11, 4, 6, ["", '', '', 'GT' ], 100, 200)
PutHand(11, 1, 7, ["", '', '', 'GT' ], 85, 215)
PutHand(11, 5, 8, ["", '', '', 'T' ], 70, 130)
PutHand(12, 2, 3, ["", 'GT', '', '' ], 215, 85)
PutHand(12, 4, 6, ["", 'GT', '', '' ], -180, 80)
PutHand(12, 1, 7, ["", 'GT', 'T', '' ], -200, 300)
PutHand(12, 5, 8, ["", 'GT', '', '' ], -200, 200)
PutHand(13, 4, 3, ["", '', '', 'GT' ], 0, 400)
PutHand(13, 6, 1, ["", '', '', 'GT' ], 50, -150)
PutHand(13, 8, 9, ["T", '', '', 'GT' ], 160, -160)
PutHand(13, 2, 10, ["", '', '', 'GT' ], 85, 215)
PutHand(14, 4, 3, ["T", '', '', '' ], 140, 60)
PutHand(14, 6, 1, ["", '', 'GT', '' ], 25, -125)
PutHand(14, 8, 9, ["T", '', '', '' ], 105, 95)
PutHand(14, 2, 10, ["", '', 'T', '' ], 5, 195)
PutHand(15, 2, 7, ["", 'GT', '', '' ], 400, 0)
PutHand(15, 1, 9, ["", 'T', '', '' ], 300, 0)
PutHand(15, 3, 10, ["", 'T', '', '' ], 180, 20)
PutHand(15, 4, 5, ["", 'GT', '', '' ], 260, 40)
PutHand(16, 2, 7, ["", 'GT', '', '' ], 275, 25)
PutHand(16, 1, 9, ["", '', 'T', '' ], 80, -80)
PutHand(16, 4, 5, ["", 'GT', '', '' ], 275, 25)
PutHand(16, 3, 10, ["", '', 'T', '' ], 40, 160)

for j in range (20):
  for i in range(1, 11):
    GetMovements(i)