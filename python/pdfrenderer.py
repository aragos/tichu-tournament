"""Generates Tichu boards and renders them to pdf.
"""

import math
import os

from board import *
from teams import ExtractTeamNames
from calculator import OrderBy
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from svglib.svglib import svg2rlg

_OVERVIEW_TABLE_STYLE = TableStyle(
  [('INNERGRID', (0, 0), (-1, -1), 0.25, "black"),
   ('BOX', (0, 0), (-1, -1), 0.25, "black"),
   ('BACKGROUND', (0, 0), (-1, 0), "#cccccc"),
   ('FONTNAME', (0, 0), (-1, 0), "Helvetica-Bold")])

_RESULTS_TABLE_STYLE = TableStyle([
  ('INNERGRID', (0, 0), (-1, -1), 0.25, "black"),
  ('BOX', (0, 0), (-1, -1), 0.25, "black"),
  ('BACKGROUND', (0, 0), (-1, 0), "#cccccc"),
  ('FONTNAME', (0, 0), (-1, 0), "Helvetica-Bold"),
])


class _PdfColor:
  """Type representing a Tichu suit (stars, falchions, pagodas or jades).

  Attributes:
    value: Integer. The color's ranking (1-4) for sorting purposes.
    name: String. The color's name, as it appears in board images.
    rgbcolor: Tuple of three integers. RGB color that this color is rendered
        in.
    offset: Tuple of two integers. Represents X and Y offset relative to the
        upper left corner of rendering card names in hand overviews, in
        pixels.
  """

  def __init__(self, name, symbol, value, rgbcolor, offset):
    self.value = value
    self.name = name
    self.rgbcolor = (float(rgbcolor[0]) / 256, float(rgbcolor[1]) / 256, float(rgbcolor[2]) / 256)
    self.offset = offset
    self._symbolName = symbol
    self._symbol = None

  def GetSymbol(self):
    """Returns this color's symbol image data.

    Lazily created and cached across calls.
    """
    if not self._symbol and self._symbolName:
      path = os.path.join(os.path.split(__file__)[0], "icons/%s.svg" % self._symbolName)
      self._symbol = svg2rlg(path)
      self._symbol.scale(.18, .18)

    return self._symbol


class _PdfCard:
  """Representation of a single card within a board.

  Attributes:
    color: Color object representing the cards suit.
    shortName: String for rendering the card within hand overviews.
    order: Integer unique to each card by which cards can be sorted.
    id: String name by which card images are identified.
  """

  _CARDS = []

  def __init__(self, color, shortName, order, id):
    self.color = color
    self.shortName = shortName
    self.order = order
    self.id = id

  @classmethod
  def FromCards(cls, cards):
    """Returns a list of the given cards, converted to PDF representations.
    """

    def toCardId(card):
      if card.shortName is "T":
        return "10"
      elif card.shortName is "J":
        return "B"
      elif card.shortName is "Q":
        return "D"
      elif card.shortName is "K":
        return "K"
      elif card.shortName is "A":
        return "As"
      else:
        return str(card.shortName)

    pdfCards = []
    for card in cards:
      if card.order is 0:
        pdfCards.append(_PdfCard(_SPECIAL_COLOR, card.shortName, card.order, "Hund"))
      elif card.order is 1:
        pdfCards.append(_PdfCard(_SPECIAL_COLOR, card.shortName, card.order, "MJ"))
      elif card.order is 54:
        pdfCards.append(_PdfCard(_SPECIAL_COLOR, card.shortName, card.order, "Phoenix"))
      elif card.order is 55:
        pdfCards.append(_PdfCard(_SPECIAL_COLOR, card.shortName, card.order, "Drache"))
      else:
        pdfCards.append(
          _PdfCard(
            _COLORS[card.color.value],
            card.shortName,
            card.order,
            _COLORS[card.color.value].name + toCardId(card)))

    return pdfCards


class _PdfPosition:
  """A position on boards (north, south, east, west).

  Not specific to any board instance.

  Attributes:
    boardPosition: Position. Model position object that is being decorated
        with PDF attributes.
    name: String position name, used for rendering.
    id: Integer multiplier by which cards are matched to positions within
        boards. Unique to each position.
    firstEightOffset: Tuple of two integers. Represents X and Y offset from
        top left by which this position's first eight card icons are drawn,
        in pixels.
    fullOffset: Tuple of two integers. Represents X and Y offset relative to
        the center rectangle's top left by which this position's full hand
        description is rendered, in pixels.
    fullWidthMultiplier: Float. Multiplier applied to the width of the rendered
        full hand description for this position. The description's top left
        location will be offset by (result of multiplication, 0).
    labelOffset: Tuple of two integers. Represents X and Y offset relative to
        the center rectangle's top left by which this position's label is
        placed in the hand overview's central box, in pixels.
  """

  def __init__(self, boardPosition, firstEightOffset, fullOffset, fullWidthMultiplier, labelOffset):
    self.boardPosition = boardPosition
    self.name = boardPosition.name
    self.id = boardPosition.id
    self.firstEightOffset = firstEightOffset
    self.fullOffset = fullOffset
    self.fullWidthMultiplier = fullWidthMultiplier
    self.labelOffset = labelOffset


# General constants used in rendering hands.
_PAGE_WIDTH = LETTER[0]
_LEFT_MARGIN = 0
_TOP_MARGIN = 70
_COLOR_ID_WIDTH = 14
_CARD_ID_HEIGHT = 11

# Constants used in rendering the first eight cards of each hand.
_IMG_WIDTH = 40
_IMG_HEIGHT = 60
_IMG_MARGIN = 2

_FIRST_MARGIN = 40
_FIRST_LABEL_HEIGHT = 11
_FIRST_LABEL_MARGIN = 4
_FIRST_WIDTH = 4 * _IMG_WIDTH + 3 * _IMG_MARGIN
_FIRST_HEIGHT = 2 * _IMG_HEIGHT + _FIRST_LABEL_HEIGHT + _IMG_MARGIN + _FIRST_LABEL_MARGIN
_FIRST_REMAINING_WIDTH = _PAGE_WIDTH - (2 * _FIRST_WIDTH + _FIRST_MARGIN + 2 * _LEFT_MARGIN)
_FIRST_1_X = _FIRST_REMAINING_WIDTH / 2
_FIRST_1_Y = _TOP_MARGIN
_FIRST_2_X = _FIRST_1_X + _FIRST_WIDTH + _FIRST_MARGIN
_FIRST_2_Y = _FIRST_HEIGHT + _FIRST_MARGIN + _FIRST_1_Y

# Constants used in rendering the full hand overview for each hand.
_CENTER_MARGIN = 10
_FULL_WIDTH = 90
_FULL_HEIGHT = 5 * _CARD_ID_HEIGHT
_FULL_1_Y = -_FULL_HEIGHT - _CENTER_MARGIN
_FULL_2_Y = _CENTER_MARGIN + 2  # adjust for center outline
_FULL_3_Y = _FULL_HEIGHT + 3 * _CENTER_MARGIN + 5  # adjust for center outline

# Constants used in rendering the center of full hand overviews.
_CENTER_LABEL_MARGIN = 3
_SETUP_CENTER_Y = 2 * _FIRST_HEIGHT + _FIRST_MARGIN + 150 + _FULL_HEIGHT + _CENTER_MARGIN
_RESULTS_CENTER_Y = _FULL_HEIGHT + _CENTER_MARGIN + _TOP_MARGIN
_CENTER_WIDTH = _FULL_WIDTH + 2 * _CENTER_MARGIN
_CENTER_HEIGHT = _FULL_HEIGHT + 2 * _CENTER_MARGIN
_CENTER_X = _PAGE_WIDTH / 2 - _CENTER_WIDTH / 2

# Constants used in rendering the results tables for each board.
_RESULTS_TABLE_TOP_MARGIN = 60
_RESULTS_TABLE_Y = _RESULTS_CENTER_Y + 2 * _FULL_HEIGHT + 2 * _CENTER_MARGIN + _RESULTS_TABLE_TOP_MARGIN

# Position constants.
_NORTH = _PdfPosition(
  NORTH,
  (_FIRST_1_X, _FIRST_1_Y),
  (_CENTER_WIDTH / 2, _FULL_1_Y),
  -0.5,
  (_CENTER_WIDTH / 2, _CENTER_LABEL_MARGIN)

)
_EAST = _PdfPosition(
  EAST,
  (_FIRST_2_X, _FIRST_1_Y),
  (_CENTER_WIDTH + _CENTER_MARGIN, _FULL_2_Y),
  0,
  (_CENTER_WIDTH - _CENTER_LABEL_MARGIN, _CENTER_HEIGHT / 2)
)
_SOUTH = _PdfPosition(
  SOUTH,
  (_FIRST_1_X, _FIRST_2_Y),
  (_CENTER_WIDTH / 2, _FULL_3_Y),
  -0.5,
  (_CENTER_WIDTH / 2, _CENTER_HEIGHT - _CENTER_LABEL_MARGIN)
)
_WEST = _PdfPosition(
  WEST,
  (_FIRST_2_X, _FIRST_2_Y),
  (-_CENTER_MARGIN, _FULL_2_Y),
  -1,
  (_CENTER_LABEL_MARGIN, _CENTER_HEIGHT / 2)
)
_POSITIONS = [_NORTH, _EAST, _SOUTH, _WEST]

# Color constants.
_SPECIAL_COLOR = _PdfColor("special", None, -1, (0, 0, 0), (0, 5 * _CARD_ID_HEIGHT))
_COLORS = [
  _PdfColor("blau", "pagoda", 0, (37, 143, 209), (0, _CARD_ID_HEIGHT)),
  _PdfColor("gruen", "jade", 1, (45, 117, 56), (0, 2 * _CARD_ID_HEIGHT)),
  _PdfColor("schw", "falchion", 2, (0, 0, 0), (0, 3 * _CARD_ID_HEIGHT)),
  _PdfColor("rot", "star", 3, (237, 69, 59), (0, 4 * _CARD_ID_HEIGHT)),
]


def _Offsets(*args):
  """Combines any number of given offsets, relative to the upper left corner.

  By default reportlab will render offsets from the bottom left which is
  unintuitive. This function assumes its inputs are relative to the *upper*
  left but returns a value compatible with reportlab.

  Arguments:
    *args: Any number of tuples of two integers, representing the X and Y
        offsets respectively, in pixels.
  """
  x = 0
  y = 0
  for arg in args:
    x += arg[0]
    y += arg[1]
  return x, LETTER[1] - y


class _BoardRenderer:
  """Renderer that converts board objects into PDF files.

  A board is represented by a single page with four "first eight" sections,
  containing the name of the relevant position, the board number and the first
  eight cards as icons. The page also contains an overview of the entire hand.

  Attributes:
    canvas: reportlab canvas object to draw on.
    board: A board object to render.
  """

  def __init__(self, board, canvas):
    self.canvas = canvas
    self.board = board

  def RenderFirstEight(self):
    """Renders the first eight on the current page.
    """
    for position in _POSITIONS:
      self._RenderFirstEight(position)

  def RenderFull(self, centerOffset, highlightFirstEight):
    """Renders the full board summary on the current page.

    Args:
      centerOffset: Tuple of two integers. X and Y offsets in pixels for the
          top left corner of the center rectangle around which the board
          summary is drawn.
      highlightFirstEight: Boolean. If true draws a highlight around the first
          eight cards in the full board summary.
    """
    for position in _POSITIONS:
      self._RenderFull(position, centerOffset, highlightFirstEight)

    self._RenderCenter(centerOffset)

  def _RenderFirstEight(self, position):
    cards = _PdfCard.FromCards(self.board.GetFirstEight(position))

    offset = _Offsets(position.firstEightOffset, (_FIRST_WIDTH / 2, _FIRST_LABEL_HEIGHT))
    self.canvas.setFont('Helvetica-Bold', 10)
    self.canvas.setFillColorRGB(0, 0, 0)
    self.canvas.drawCentredString(
      offset[0], offset[1], "Hand %s, %s, First 8 Cards" % (self.board.id, position.name))
    for i in range(8):
      offset = _Offsets(
        position.firstEightOffset,
        (0, _FIRST_LABEL_HEIGHT + _FIRST_LABEL_MARGIN),
        ((i % 4) * _IMG_WIDTH + _IMG_MARGIN, math.floor(i / 4) * (_IMG_HEIGHT + _IMG_MARGIN)))
      path = os.path.join(os.path.split(__file__)[0], "3/kl%s.jpg" % cards[i].id)
      self.canvas.drawImage(path, offset[0], offset[1], _IMG_WIDTH, -_IMG_HEIGHT)

  def _RenderFull(self, position, centerOffset, highlightFirstEight):
    cards = _PdfCard.FromCards(self.board.GetFull(position))
    firstEight = [c.order for c in self.board.GetFirstEight(position)]

    data = []
    tableStyle = [
      ("LEFTPADDING", (0, 0), (-1, -1), 0),
      ("RIGHTPADDING", (0, 0), (-1, -1), 0),
      ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
      ("TOPPADDING", (0, 0), (-1, -1), 0),
      ("ALIGN", (1, 0), (-1, -1), "CENTER")

    ]

    for color in _COLORS + [_SPECIAL_COLOR]:
      colorData = []
      currentRow = len(data)
      tableStyle.append(("TEXTCOLOR", (0, currentRow), (-1, currentRow), color.rgbcolor))

      if color.GetSymbol():
        colorData.append(color.GetSymbol())
      else:
        colorData.append(None)

      for i in range(14):
        if cards[i].color == color:
          colorData.append(cards[i].shortName)
          if highlightFirstEight and cards[i].order in firstEight:
            colorCardCount = len(colorData)
            tableStyle.append((
              "BOX",
              (colorCardCount - 1, currentRow),
              (colorCardCount - 1, currentRow),
              0.25,
              color.rgbcolor))

      data.append(colorData)

    columnWidths = [12] + [11 for i in range(1, max([len(row) for row in data]))]
    if "Dr" in [c.shortName for c in cards]:
      columnWidths[1] = 13
    rowHeights = [12 for i in range(0, 5)]

    table = Table(data, rowHeights=rowHeights, colWidths=columnWidths, style=TableStyle(tableStyle))
    width, height = table.wrapOn(self.canvas, *LETTER)
    table.drawOn(self.canvas, *_Offsets(centerOffset, position.fullOffset,
                                        (width * position.fullWidthMultiplier, _FULL_HEIGHT)))

  def _RenderCenter(self, topLeftOffset):
    """
    Renders the board's "center" rectangle, including the board number and position labels.

    Args:
      topLeftOffset: tuple for the X/Y offset in pixels of the center rectangle's top-left corner,
          relative to the page's top-left corner.
    """
    self.canvas.setStrokeColorRGB(0, 0, 0)
    self.canvas.setFillColorRGB(1, 1, 1)
    self.canvas.setLineWidth(.5)
    offset = _Offsets(topLeftOffset)
    self.canvas.rect(offset[0], offset[1], _CENTER_WIDTH, -_CENTER_HEIGHT)

    self.canvas.setFillColorRGB(0, 0, 0)

    # TODO: Calculate line height instead of eyeballing half of it for offset.
    offset = _Offsets(topLeftOffset, (_CENTER_WIDTH / 2, _CENTER_HEIGHT / 2), (0, 14))
    self.canvas.setFont('Helvetica-Bold', 40)
    self.canvas.drawCentredString(offset[0], offset[1], str(self.board.id))

    self.canvas.setFont('Helvetica-Bold', 10)
    i = 180
    for position in _POSITIONS:
      self.canvas.saveState()
      offset = _Offsets(topLeftOffset, position.labelOffset)
      self.canvas.translate(offset[0], offset[1])
      self.canvas.rotate(i)
      i -= 90
      self.canvas.drawCentredString(0, 0, position.name)
      self.canvas.restoreState()


def _RenderResultsOverview(c, tourney_name, summaries, player_futures):
  # TODO: Render title as paragraph to enable automatic wrapping
  titleLocation = _Offsets((_PAGE_WIDTH / 2, 250))
  c.setFont('Helvetica-Bold', 32)
  c.drawCentredString(titleLocation[0], titleLocation[1], tourney_name + " Results")

  OrderBy(summaries, "MP")
  rows = [["Place", "Team", "Match Points"]]
  place = 1
  for summary in summaries:
    rows.append([
      place,
      ExtractTeamNames(summary.team_no, player_futures, "Team "),
      "{0:.2f}".format(summary.mps)
    ])
    place += 1

  table = Table(rows, style=_OVERVIEW_TABLE_STYLE)

  tableWidth, tableHeight = table.wrapOn(c, *LETTER)
  tableLocation = _Offsets((_PAGE_WIDTH / 2 - tableWidth / 2, 350 + tableHeight))
  table.drawOn(c, *tableLocation)

  c.showPage()


def _RenderHandResults(c, hand_result, player_futures):
  rows = [
    [
      "NS Team",
      "EW Team",
      "Calls",
      "NS Score",
      "EW Score",
      "NS MPs",
      "EW MPs",
    ]
  ]
  rowStyles = []
  for score in hand_result._board_score:
    rows.append([
      ExtractTeamNames(score._hr.ns_pair_no(), player_futures),
      ExtractTeamNames(score._hr.ew_pair_no(), player_futures),
      str(score._hr.calls()),
      score._hr.ns_score(),
      score._hr.ew_score(),
      "{0:.1f}".format(score.ns_mps),
      "{0:.1f}".format(score.ew_mps),
    ])

    rowCount = len(rows)
    if rowCount % 2 is 1:
      rowStyles.append(("BACKGROUND", (0, rowCount - 1), (-1, rowCount - 1), "#eeeeee"))

  style = TableStyle(rowStyles, parent=_RESULTS_TABLE_STYLE)

  table = Table(rows, style=style)

  tableWidth, tableHeight = table.wrapOn(c, *LETTER)
  tableLocation = _Offsets((_PAGE_WIDTH / 2 - tableWidth / 2, _RESULTS_TABLE_Y + tableHeight))
  table.drawOn(c, *tableLocation)


def _TeamCalls(calls, *positions):
  for position in positions:
    if calls.call_for_short_position(position):
      yield "{}({})".format(position, calls.call_for_short_position(position))


def RenderBoardsToIo(boards, write_target):
  """Renders the given boards to the passed output stream."""
  c = canvas.Canvas(write_target, pagesize=LETTER)
  for board in boards:
    renderer = _BoardRenderer(board, c)
    renderer.RenderFull((_CENTER_X, _SETUP_CENTER_Y), highlightFirstEight=False)
    renderer.RenderFirstEight()
    c.showPage()
  c.save()


def RenderResultsToIo(tourney_name, boards, hand_results, summaries, player_futures, write_target):
  """Renders tournament results to the passed output stream.

  Args:
    tourney_name: String. Name of the tournament.
    boards: List of board.Board objects. Tournament board descriptions sorted
        by board order.
    hand_results: List of calculator.Board objects. Board results sorted by
        board order.
    summaries: List of calculator.TeamSummary objects. Team summaries for the
        tournament.
    player_futures: <fill in>
    write_target: Output stream or file name. Location to write the results to.
  """
  c = canvas.Canvas(write_target, pagesize=LETTER)

  _RenderResultsOverview(c, tourney_name, summaries, player_futures)

  for board, hand in zip(boards, hand_results):
    _BoardRenderer(board, c).RenderFull((_CENTER_X, _RESULTS_CENTER_Y), highlightFirstEight=True)
    _RenderHandResults(c, hand, player_futures)
    c.showPage()

  c.save()
