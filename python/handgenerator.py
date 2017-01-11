import json
import math
import random

from svglib.svglib import svg2rlg
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


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


_PAGE_WIDTH = LETTER[0]
_LEFT_MARGIN = 0
_TOP_MARGIN = 0
_IMG_WIDTH = 40
_IMG_HEIGHT = 60
_IMG_MARGIN = 2
_COLOR_ID_WIDTH = 14
_CARD_ID_HEIGHT = 11


_FIRST_MARGIN = 40
_FIRST_LABEL_HEIGHT = 11
_FIRST_LABEL_MARGIN = 4
_FIRST_WIDTH = 4 * _IMG_WIDTH + 3 * _IMG_MARGIN
_FIRST_HEIGHT = 2 * _IMG_HEIGHT + _FIRST_LABEL_HEIGHT + _IMG_MARGIN + _FIRST_LABEL_MARGIN
_FIRST_REMAINING_WIDTH = _PAGE_WIDTH - (2 * _FIRST_WIDTH + _FIRST_MARGIN + 2 * _LEFT_MARGIN)
_FIRST_1_X = _FIRST_REMAINING_WIDTH / 2
_FIRST_1_Y = 70
_FIRST_2_X = _FIRST_1_X + _FIRST_WIDTH + _FIRST_MARGIN
_FIRST_2_Y = _FIRST_HEIGHT + _FIRST_MARGIN + _FIRST_1_Y


_FULL_MARGIN = 20
_FULL_WIDTH = 90
_FULL_HEIGHT = 5 * _CARD_ID_HEIGHT
_FULL_REMAINING_WIDTH = _PAGE_WIDTH - (3*_FULL_WIDTH + 2*_FULL_MARGIN + 2*_LEFT_MARGIN)
_FULL_1_X = _FULL_REMAINING_WIDTH/2
_FULL_2_X = _FULL_1_X + _FULL_WIDTH + _FULL_MARGIN
_FULL_3_X = _FULL_2_X + _FULL_WIDTH + _FULL_MARGIN
_FULL_1_Y = 2*_FIRST_HEIGHT + _FIRST_MARGIN + 150
_FULL_2_Y = _FULL_1_Y + _FULL_HEIGHT + _FULL_MARGIN
_FULL_3_Y = _FULL_2_Y + _FULL_HEIGHT + _FULL_MARGIN

_CENTER_LABEL_MARGIN = 3
_CENTER_X = _FULL_2_X - _FULL_MARGIN/2
_CENTER_Y = _FULL_2_Y - _FULL_MARGIN/2
_CENTER_WIDTH = _FULL_WIDTH + _FULL_MARGIN
_CENTER_HEIGHT = _FULL_HEIGHT + _FULL_MARGIN

_NORTH = Position(
  "North",
  0,
  (_FIRST_1_X, _FIRST_1_Y),
  (_FULL_2_X, _FULL_1_Y),
  (_CENTER_X + _CENTER_WIDTH / 2, _CENTER_Y + _CENTER_LABEL_MARGIN)
)
_EAST = Position(
  "East",
  1,
  (_FIRST_2_X, _FIRST_1_Y),
  (_FULL_3_X, _FULL_2_Y),
  (_CENTER_X + _CENTER_WIDTH - _CENTER_LABEL_MARGIN, _CENTER_Y + _CENTER_HEIGHT / 2)
)
_SOUTH = Position(
  "South",
  2,
  (_FIRST_1_X, _FIRST_2_Y),
  (_FULL_2_X, _FULL_3_Y),
  (_CENTER_X + _CENTER_WIDTH / 2, _CENTER_Y + _CENTER_HEIGHT - _CENTER_LABEL_MARGIN)
)
_WEST = Position(
  "West",
  3,
  (_FIRST_2_X, _FIRST_2_Y),
  (_FULL_1_X, _FULL_2_Y),
  (_CENTER_X + _CENTER_LABEL_MARGIN, _CENTER_Y + _CENTER_HEIGHT / 2)
)
_POSITIONS = [_NORTH, _EAST, _SOUTH, _WEST]
_SPECIAL_COLOR = Color("special", None, -1, (0,0,0), (0, 5*_CARD_ID_HEIGHT))
_COLORS = [
  Color("blau", "pagoda", 0, (37,143,209), (0, _CARD_ID_HEIGHT)),
  Color("gruen", "jade", 1, (45,117,56), (0, 2*_CARD_ID_HEIGHT)),
  Color("schw", "falchion", 2, (0,0,0), (0, 3*_CARD_ID_HEIGHT)),
  Color("rot", "star", 3, (237,69,59), (0, 4*_CARD_ID_HEIGHT)),
]

def CreateCards():
  cards = []
  for color in _COLORS:
    offset = color.value + 2
    for i in range(2, 10):
      cards.append(Card(color, i, 4 * (i - 2) + offset, color.name + str(i)))
    cards.append(Card(color, "T", 4 * 8 + offset, color.name + "10"))
    cards.append(Card(color, "J", 4 * 9 + offset, color.name + "B"))
    cards.append(Card(color, "Q", 4 * 10 + offset, color.name + "D"))
    cards.append(Card(color, "K", 4 * 11 + offset, color.name + "K"))
    cards.append(Card(color, "A", 4 * 12 + offset, color.name + "As"))
  cards.append(Card(_SPECIAL_COLOR, "H", 0, "Hund"))
  cards.append(Card(_SPECIAL_COLOR, "1", 1, "_MJ"))
  cards.append(Card(_SPECIAL_COLOR, "P", 54, "Phoenix"))
  cards.append(Card(_SPECIAL_COLOR, "Dr", 55, "Drache"))
  return cards

_CARDS = CreateCards()

class Board:
  def __init__(self, id, cards = None):
    self.id = id
    if not cards:
      cards = _CARDS[:]
      random.shuffle(cards)
    self.cards = cards

  def GetFull(self, position):
    return sorted(self.cards[position.id*14:(position.id+1)*14], key=lambda x: -x.order)

  def GetFirstEight(self, position):
    return sorted(self.cards[position.id*14:(position.id+1)*14-6], key=lambda x: -x.order)

  def ToJson(self):
    return json.dumps({'id': self.id, 'cards': self.cards})

  @classmethod
  def FromJson(cls, jsonBoard):
    decoded = json.load(jsonBoard)
    cls(id=decoded['id'], cards=decoded['cards'])


class HandRenderer:
  def __init__(self, id, canvas):
    self.id = id
    self.canvas = canvas
    self.hand = Hand(id)

  def Render(self):
    for position in _POSITIONS:
      self._RenderFirstEight(position)
      self._RenderFull(position)

    self._RenderCenter()
    self.canvas.showPage()

  def _RenderFirstEight(self, position):
    cards = self.hand.GetFirstEight(position)

    offset = _Offsets(position.firstEightOffset, (_FIRST_WIDTH / 2, _FIRST_LABEL_HEIGHT))
    self.canvas.setFont('Helvetica-Bold', 10)
    self.canvas.setFillColorRGB(0, 0, 0)
    self.canvas.drawCentredString(
        offset[0], offset[1], "Hand %s, %s, First 8 Cards" % (self.hand.id, position.name))
    for i in range(8):
      offset = _Offsets(
        position.firstEightOffset,
        (0, _FIRST_LABEL_HEIGHT + _FIRST_LABEL_MARGIN),
        ((i%4)*_IMG_WIDTH+_IMG_MARGIN, math.floor(i/4)*(_IMG_HEIGHT+_IMG_MARGIN)))
      self.canvas.drawImage(
          "3/kl%s.gif" % cards[i].id, offset[0], offset[1], _IMG_WIDTH, -_IMG_HEIGHT)

  def _RenderFull(self, position):
    cards = self.hand.GetFull(position)

    for color in _COLORS + [_SPECIAL_COLOR]:
      self.canvas.setFillColorRGB(
          float(color.rgbcolor[0])/256,
          float(color.rgbcolor[1])/256,
          float(color.rgbcolor[2])/256)

      if color.symbol:
        offset = _Offsets(position.fullOffset, color.offset, (0, 1))
        color.symbol.drawOn(self.canvas, offset[0], offset[1])

      cardNames = []
      for i in range(14):
        if cards[i].color == color:
          cardNames.append(str(cards[i].shortName))
      self.canvas.setFont('Helvetica', 10)
      offset = _Offsets(position.fullOffset, color.offset, (_COLOR_ID_WIDTH, 0))
      self.canvas.drawString(offset[0], offset[1],  ' '.join(cardNames))

  def _RenderCenter(self):
    self.canvas.setStrokeColorRGB(0, 0, 0)
    self.canvas.setFillColorRGB(1, 1, 1)
    self.canvas.setLineWidth(.5)
    offset = _Offsets((_CENTER_X, _CENTER_Y))
    self.canvas.rect(offset[0], offset[1], _CENTER_WIDTH, -_CENTER_HEIGHT)

    self.canvas.setFillColorRGB(0, 0, 0)

    # _TODO: Calculate line height instead of eyeballing half of it for offset.
    offset = _Offsets((_CENTER_X, _CENTER_Y), (_CENTER_WIDTH / 2, _CENTER_HEIGHT / 2), (0, 14))
    self.canvas.setFont('Helvetica-Bold', 40)
    self.canvas.drawCentredString(offset[0], offset[1], str(self.hand.id))

    self.canvas.setFont('Helvetica-Bold', 10)
    i = 180
    for position in _POSITIONS:
      self.canvas.saveState()
      offset = _Offsets(position.labelOffset)
      self.canvas.translate(offset[0], offset[1])
      self.canvas.rotate(i)
      i -= 90
      self.canvas.drawCentredString(0, 0, position.name)
      self.canvas.restoreState()


def _Offsets(*args):
  x = 0
  y = 0
  for arg in args:
    x += arg[0]
    y += arg[1]
  return (x, LETTER[1] - y)


def GenerateBoards(count):
  '''Returns a list of randomly generated boards.

  Args:
    count: Integer. Number of boards to generate.
  '''
  for id in range(1,count):
    yield Board(id)



#c = canvas.Canvas("hands.pdf", pagesize=LETTER)
#for id in range(1,25):
#  HandRenderer(id, c).Render()
#c.save()