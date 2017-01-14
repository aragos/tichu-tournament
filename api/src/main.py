import webapp2

from api.src.board_handler import PdfBoardHandler
from auth_handler import AuthHandler
from auth_handler import LoginHandler
from auth_handler import LogoutHandler
from change_log_handler import ChangeLogHandler
from hand_handler import HandHandler
from hand_preparation_handler import HandPreparationHandler
from movement_handler import MovementHandler
from pair_id_handler import PairIdHandler
from pair_id_handler import TourneyPairIdHandler
from pair_id_handler import TourneyPairIdsHandler
from result_handler import ResultHandler
from result_handler import XlxsResultHandler
from tournament_handler import TourneyHandler
from tournament_list_handler import TourneyListHandler

app = webapp2.WSGIApplication([
    ('/api/checkAuth', AuthHandler),
    ('/api/login', LoginHandler),
    ('/api/logout', LogoutHandler),
    ('/api/tournaments/?', TourneyListHandler),
    ('/api/tournaments/pairno/([^/]+)/?', PairIdHandler),
    ('/api/tournaments/([^/]+)/?', TourneyHandler),
    ('/api/tournaments/([^/]+)/handprep/?', HandPreparationHandler),
    ('/api/tournaments/([^/]+)/hands/([^/]+)/([^/]+)/([^/]+)/?', HandHandler),
    ('/api/tournaments/([^/]+)/hands/changelog/([^/]+)/([^/]+)/([^/]+)/?', ChangeLogHandler),
    ('/api/tournaments/([^/]+)/pairids/([^/]+)/?', TourneyPairIdHandler),
    ('/api/tournaments/([^/]+)/pairids/?', TourneyPairIdsHandler),
    ('/api/tournaments/([^/]+)/movement/([^/]+)/?', MovementHandler),
    ('/api/tournaments/([^/]+)/results/?', ResultHandler),
    ('/api/tournaments/([^/]+)/xlsresults/?', XlxsResultHandler),
    ('/api/tournaments/([^/]+)/pdfboards/?', PdfBoardHandler),
], debug=True)
