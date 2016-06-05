import random

import math

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from svglib.svglib import svg2rlg


class Color:
  def __init__(self, name, symbol, value, rgbcolor, offset):
    self.name = name
    self.value = value
    self.rgbcolor = rgbcolor
    self.offset = offset
    if symbol:
      self.symbol = svg2rlg("icons/%s.svg" % symbol)
      self.symbol.scale(.18, .18)
    else:
      self.symbol = None


class Card:
  def __init__(self, color, shortName, order, id):
    self.color = color
    self.shortName = shortName
    self.order = order
    self.id = id


class Position:
  def __init__(self, name, id, firstEightOffset, fullOffset, labelOffset):
    self.name = name
    self.id = id
    self.firstEightOffset = firstEightOffset
    self.fullOffset = fullOffset
    self.labelOffset = labelOffset


PAGE_WIDTH = LETTER[0]
LEFT_MARGIN = 0
TOP_MARGIN = 0
IMG_WIDTH = 40
IMG_HEIGHT = 60
IMG_MARGIN = 2
COLOR_ID_WIDTH = 14
CARD_ID_HEIGHT = 11


FIRST_MARGIN = 40
FIRST_LABEL_HEIGHT = 11
FIRST_LABEL_MARGIN = 4
FIRST_WIDTH = 4 * IMG_WIDTH + 3 * IMG_MARGIN
FIRST_HEIGHT = 2 * IMG_HEIGHT + FIRST_LABEL_HEIGHT + IMG_MARGIN + FIRST_LABEL_MARGIN
FIRST_REMAINING_WIDTH = PAGE_WIDTH - (2 * FIRST_WIDTH + FIRST_MARGIN + 2 * LEFT_MARGIN)
FIRST_1_X = FIRST_REMAINING_WIDTH / 2
FIRST_1_Y = 70
FIRST_2_X = FIRST_1_X + FIRST_WIDTH + FIRST_MARGIN
FIRST_2_Y = FIRST_HEIGHT + FIRST_MARGIN + FIRST_1_Y


FULL_MARGIN = 20
FULL_WIDTH = 90
FULL_HEIGHT = 5 * CARD_ID_HEIGHT
FULL_REMAINING_WIDTH = PAGE_WIDTH - (3*FULL_WIDTH + 2*FULL_MARGIN + 2*LEFT_MARGIN)
FULL_1_X = FULL_REMAINING_WIDTH/2
FULL_2_X = FULL_1_X + FULL_WIDTH + FULL_MARGIN
FULL_3_X = FULL_2_X + FULL_WIDTH + FULL_MARGIN
FULL_1_Y = 2*FIRST_HEIGHT + FIRST_MARGIN + 150
FULL_2_Y = FULL_1_Y + FULL_HEIGHT + FULL_MARGIN
FULL_3_Y = FULL_2_Y + FULL_HEIGHT + FULL_MARGIN

CENTER_LABEL_MARGIN = 3
CENTER_X = FULL_2_X - FULL_MARGIN/2
CENTER_Y = FULL_2_Y - FULL_MARGIN/2
CENTER_WIDTH = FULL_WIDTH + FULL_MARGIN
CENTER_HEIGHT = FULL_HEIGHT + FULL_MARGIN

NORTH = Position(
  "North",
  0,
  (FIRST_1_X, FIRST_1_Y),
  (FULL_2_X, FULL_1_Y),
  (CENTER_X + CENTER_WIDTH / 2, CENTER_Y + CENTER_LABEL_MARGIN)
)
EAST = Position(
  "East",
  1,
  (FIRST_2_X, FIRST_1_Y),
  (FULL_3_X, FULL_2_Y),
  (CENTER_X + CENTER_WIDTH - CENTER_LABEL_MARGIN, CENTER_Y + CENTER_HEIGHT / 2)
)
SOUTH = Position(
  "South",
  2,
  (FIRST_1_X, FIRST_2_Y),
  (FULL_2_X, FULL_3_Y),
  (CENTER_X + CENTER_WIDTH / 2, CENTER_Y + CENTER_HEIGHT - CENTER_LABEL_MARGIN)
)
WEST = Position(
  "West",
  3,
  (FIRST_2_X, FIRST_2_Y),
  (FULL_1_X, FULL_2_Y),
  (CENTER_X + CENTER_LABEL_MARGIN, CENTER_Y + CENTER_HEIGHT / 2)
)
POSITIONS = [NORTH, EAST, SOUTH, WEST]
SPECIAL_COLOR = Color("special", None, -1, (0,0,0), (0, 5*CARD_ID_HEIGHT))
COLORS = [
  Color("blau", "pagoda", 0, (37,143,209), (0, CARD_ID_HEIGHT)),
  Color("gruen", "jade", 1, (45,117,56), (0, 2*CARD_ID_HEIGHT)),
  Color("schw", "falchion", 2, (0,0,0), (0, 3*CARD_ID_HEIGHT)),
  Color("rot", "star", 3, (237,69,59), (0, 4*CARD_ID_HEIGHT)),
]

def CreateCards():
  cards = []
  for color in COLORS:
    offset = color.value + 2
    for i in range(2, 10):
      cards.append(Card(color, i, 4 * (i - 2) + offset, color.name + str(i)))
    cards.append(Card(color, "T", 4 * 8 + offset, color.name + "10"))
    cards.append(Card(color, "J", 4 * 9 + offset, color.name + "B"))
    cards.append(Card(color, "Q", 4 * 10 + offset, color.name + "D"))
    cards.append(Card(color, "K", 4 * 11 + offset, color.name + "K"))
    cards.append(Card(color, "A", 4 * 12 + offset, color.name + "As"))
  cards.append(Card(SPECIAL_COLOR, "H", 0, "Hund"))
  cards.append(Card(SPECIAL_COLOR, "1", 1, "MJ"))
  cards.append(Card(SPECIAL_COLOR, "P", 54, "Phoenix"))
  cards.append(Card(SPECIAL_COLOR, "Dr", 55, "Drache"))
  return cards

CARDS = CreateCards()

class Hand:
  def __init__(self, id):
    self.id = id
    hand = CARDS[:]
    random.shuffle(hand)
    self.cards = hand

  def GetFull(self, position):
    return sorted(self.cards[position.id*14:(position.id+1)*14], key=lambda x: -x.order)

  def GetFirstEight(self, position):
    return sorted(self.cards[position.id*14:(position.id+1)*14-6], key=lambda x: -x.order)


class HandRenderer:
  def __init__(self, id, canvas):
    self.id = id
    self.canvas = canvas
    self.hand = Hand(id)

  def Render(self):
    for position in POSITIONS:
      self._RenderFirstEight(position)
      self._RenderFull(position)

    self._RenderCenter()
    self.canvas.showPage()

  def _RenderFirstEight(self, position):
    cards = self.hand.GetFirstEight(position)

    offset = Offsets(position.firstEightOffset, (FIRST_WIDTH / 2, FIRST_LABEL_HEIGHT))
    self.canvas.setFont('Helvetica-Bold', 10)
    self.canvas.setFillColorRGB(0, 0, 0)
    self.canvas.drawCentredString(
        offset[0], offset[1], "Hand %s, %s, First 8 Cards" % (self.hand.id, position.name))
    for i in range(8):
      offset = Offsets(
        position.firstEightOffset,
        (0, FIRST_LABEL_HEIGHT + FIRST_LABEL_MARGIN),
        ((i%4)*IMG_WIDTH+IMG_MARGIN, math.floor(i/4)*(IMG_HEIGHT+IMG_MARGIN)))
      self.canvas.drawImage(
          "3/kl%s.gif" % cards[i].id, offset[0], offset[1], IMG_WIDTH, -IMG_HEIGHT)

  def _RenderFull(self, position):
    cards = self.hand.GetFull(position)

    for color in COLORS + [SPECIAL_COLOR]:
      self.canvas.setFillColorRGB(
          float(color.rgbcolor[0])/256,
          float(color.rgbcolor[1])/256,
          float(color.rgbcolor[2])/256)

      if color.symbol:
        offset = Offsets(position.fullOffset, color.offset, (0, 1))
        color.symbol.drawOn(self.canvas, offset[0], offset[1])

      cardNames = []
      for i in range(14):
        if cards[i].color == color:
          cardNames.append(str(cards[i].shortName))
      self.canvas.setFont('Helvetica', 10)
      offset = Offsets(position.fullOffset, color.offset, (COLOR_ID_WIDTH, 0))
      self.canvas.drawString(offset[0], offset[1],  ' '.join(cardNames))

  def _RenderCenter(self):
    self.canvas.setStrokeColorRGB(0, 0, 0)
    self.canvas.setFillColorRGB(1, 1, 1)
    self.canvas.setLineWidth(.5)
    offset = Offsets((CENTER_X, CENTER_Y))
    self.canvas.rect(offset[0], offset[1], CENTER_WIDTH, -CENTER_HEIGHT)

    self.canvas.setFillColorRGB(0, 0, 0)

    # TODO: Calculate line height instead of eyeballing half of it for offset.
    offset = Offsets((CENTER_X, CENTER_Y), (CENTER_WIDTH/2, CENTER_HEIGHT/2), (0, 14))
    self.canvas.setFont('Helvetica-Bold', 40)
    self.canvas.drawCentredString(offset[0], offset[1], str(self.hand.id))

    self.canvas.setFont('Helvetica-Bold', 10)
    i = 180
    for position in POSITIONS:
      self.canvas.saveState()
      offset = Offsets(position.labelOffset)
      self.canvas.translate(offset[0], offset[1])
      self.canvas.rotate(i)
      i -= 90
      self.canvas.drawCentredString(0, 0, position.name)
      self.canvas.restoreState()


def Offsets(*args):
  x = 0
  y = 0
  for arg in args:
    x += arg[0]
    y += arg[1]
  return (x, LETTER[1] - y)



c = canvas.Canvas("hands.pdf", pagesize=LETTER)
for id in range(1,25):
  HandRenderer(id, c).Render()
c.save()