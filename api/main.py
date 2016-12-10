import webapp2
from hand_handler import HandHandler
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
], debug=True)
