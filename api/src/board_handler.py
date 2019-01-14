"""Handler returning board information within a tournament."""

import urllib
import webapp2

from api.src.handler_utils import GetTourneyWithIdAndMaybeReturnStatus, \
  CheckUserOwnsTournamentAndMaybeReturnStatus
from google.appengine.api import users
from python import pdfrenderer

class PdfBoardHandler(webapp2.RequestHandler):
  def get(self, id):
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return

    if not CheckUserOwnsTournamentAndMaybeReturnStatus(
        self.response,
        users.get_current_user(),
        tourney):
      return

    boards = tourney.GetBoards()

    pdfrenderer.RenderBoardsToIo(boards, self.response.out)

    self.response.headers['Content-Type'] = 'application/pdf'
    self.response.headers['Content-Disposition'] = (
      'attachment; filename=%sBoards.pdf' % str(urllib.quote(tourney.name)))
    self.response.set_status(200)