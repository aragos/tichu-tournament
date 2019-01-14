"""Generates Tichu boards and renders them to pdf.
"""

import json
import random


class Color:
  """Type representing a Tichu suit (stars, falchions, pagodas or jades).

  Attributes:
    value: Integer. The color's ranking (1-4) for sorting purposes.
  """
  def __init__(self, value):
    self.value = value


class Card:
  """Representation of a single card within a board.

  Attributes:
    color: Color object representing the cards suit.
    shortName: String for rendering the card within hand overviews.
    order: Integer unique to each card by which cards can be sorted.
  """

  _CARDS = []

  def __init__(self, color, shortName, order):
    self.color = color
    self.shortName = shortName
    self.order = order

  def ToJson(self):
    """Returns this card's JSON representation.
    """
    return self.order

  @classmethod
  def FromJson(cls, order):
    """Returns a card given the cards order.

    Arguments:
      order: Integer uniquely identifying this card's order.
    """
    return cls.AllCards()[order]

  @classmethod
  def AllCards(cls):
    """Returns a list of all cards in Tichu, sorted by their order.

    The cards are cached across calls but this method will always return a new
    list when called.
    """
    if not cls._CARDS:
      cards = []
      for color in _COLORS:
        offset = color.value + 2
        for i in range(2, 10):
          cards.append(Card(color, i, 4 * (i - 2) + offset))
        cards.append(Card(color, "T", 4 * 8 + offset))
        cards.append(Card(color, "J", 4 * 9 + offset))
        cards.append(Card(color, "Q", 4 * 10 + offset))
        cards.append(Card(color, "K", 4 * 11 + offset))
        cards.append(Card(color, "A", 4 * 12 + offset))
      cards.append(Card(SPECIAL_COLOR, "H", 0))
      cards.append(Card(SPECIAL_COLOR, "1", 1))
      cards.append(Card(SPECIAL_COLOR, "P", 54))
      cards.append(Card(SPECIAL_COLOR, "Dr", 55))
      cls._CARDS = sorted(cards, key=lambda x: x.order)

    return cls._CARDS[:]


class Position:
  """A position on boards (north, south, east, west).

  Not specific to any board instance.

  Attributes:
    name: String position name, used for rendering.
    id: Integer multiplier by which cards are matched to positions within
        boards. Unique to each position.
  """
  def __init__(self, name, id):
    self.name = name
    self.id = id


# Position constants.
NORTH = Position("North", 0)
EAST = Position("East", 1)
SOUTH = Position("South", 2)
WEST = Position("West", 3)
_POSITIONS = [NORTH, EAST, SOUTH, WEST]

# Color constants.
BLUE = Color(0)
GREEN = Color(1)
BLACK = Color(2)
RED = Color(3)
SPECIAL_COLOR = Color(-1)
_COLORS = [BLUE, GREEN, BLACK, RED]


class Board:
  """A board within a tournament.

  Attributes:
    id: Integer. Unique ID by which this board can be identified within the
        tournament.
    cards: List of card objects, sorted according to position: The first
        eight entries represent the first eight cards of the position with
        ID 0, the next six cards the remainder of that position's hand. Then
        follow the first eight cards of position with ID 1 and so on.
  """
  def __init__(self, id, cards = None):
    """Creates a board with the given ID.

    Arguments:
      cards: Optional. If not specified a new set of cards will be randomly
          generated.
    """
    self.id = id
    if not cards:
      cards = Card.AllCards()
      random.shuffle(cards)
    self.cards = cards

  def GetFull(self, position):
    """Returns the full hand for the given position.

    Returns: A list of card objects, sorted by reverse order (thus, with the
        highest ordered cards first).
    """
    return sorted(self.cards[position.id*14:(position.id+1)*14], key=lambda x: -x.order)

  def GetFirstEight(self, position):
    """Returns the first eight cards for the given position.

    Returns: A list of card objects, sorted by reverse order (thus, with the
        highest ordered cards first).
    """
    return sorted(self.cards[position.id*14:(position.id+1)*14-6], key=lambda x: -x.order)

  def ToJson(self):
    """Returns a JSON representation of this board.

    The returned representation can be deserialized by this type's FromJson
    method.
    """
    cards = []
    for card in self.cards:
      cards.append(card.ToJson())

    return json.dumps({'id': self.id, 'cards': cards})

  @classmethod
  def FromJson(cls, modelBoard):
    """Returns a board object created from the passed JSON representation.

    The JSON representation must have been created by the ToJson method of this
    type.
    """
    decoded = json.loads(modelBoard.board)
    return cls(id=modelBoard.board_number, cards=[Card.FromJson(c) for c in decoded['cards']])


def GenerateBoards(count):
  '''Returns a list of randomly generated boards.

  Args:
    count: Integer. Number of boards to generate.
  '''
  for id in range(1,count+1):
    yield Board(id)