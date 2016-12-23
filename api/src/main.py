import webapp2
from hand_handler import HandHandler
from movement_handler import MovementHandler
from pair_id_handler import PairIdHandler
from pair_id_handler import TourneyPairIdHandler
from pair_id_handler import TourneyPairIdsHandler
from result_handler import ResultHandler
from result_handler import XlxsResultHandler
from tournament_handler import TourneyHandler
from tournament_list_handler import TourneyListHandler

app = webapp2.WSGIApplication([
    ('/api/tournaments/?', TourneyListHandler),
    ('/api/tournaments/([^/]+)/?', TourneyHandler),
    ('/api/tournaments/([^/]+)/results/?', ResultHandler),
    ('/api/tournaments/([^/]+)/xlsresults/?', XlxsResultHandler),
    ('/api/tournaments/([^/]+)/hands/([^/]+)/([^/]+)/([^/]+)/?', HandHandler),
    ('/api/tournaments/([^/]+)/pairids/([^/]+)/?', TourneyPairIdHandler),
    ('/api/tournaments/([^/]+)/pairids/?', TourneyPairIdsHandler),
    ('/api/tournaments/pairno/([^/]+)/?', PairIdHandler),
    ('/api/tournaments/([^/]+)/movement/([^/]+)/?', MovementHandler),
], debug=True)
