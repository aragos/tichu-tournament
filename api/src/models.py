from google.appengine.ext import ndb

class Tournament(ndb.Model):
  ''' Model for all the information needed to describe a Tournament
     
      Fields:
        hands: json object describing a list of raw hand records including
               scores and calls. Required.
        owner_id: owner of the tournament. Required.
        metadata: unique id of the tournament, number of pairs and hands are
                  required. May also contain information about players in each
                  team.
  '''
  hands = ndb.StringProperty()
  owner_id = ndb.StringProperty()
  metadata = ndb.StringProperty()
