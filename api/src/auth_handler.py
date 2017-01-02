import json
import webapp2
import urllib

from google.appengine.api import users
from handler_utils import SetErrorStatus


class LoginHandler(webapp2.RequestHandler):
  ''' Class to handle requests to /api/login?then=<url>
  '''
  def get(self):
    ''' Redirect to Google login page, followed by another redirect to the 
    URL specified by [then] argument.

    See api for request and response documentation.
    '''
    url = users.create_login_url(dest_url=self.request.get('then'))
    self.redirect(url)


class AuthHandler(webapp2.RequestHandler):
  ''' Class to handle requests to /api/checkAuth '''
  def get(self):
    ''' Test if the user is logged in. 

    See api for request and response documentation.
    '''
    user = users.get_current_user()
    if not user:
      SetErrorStatus(self.response, 401, "Invalid User", "User not logged in")
      return

    self.response.set_status(200)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps({"user": user.nickname()}, indent=2))

class LogoutHandler(webapp2.RequestHandler):
  ''' Class to handle requests to /api/logout?then=<url>
  '''
  def get(self):
    ''' Redirect to Google logout page, followed by another redirect to the 
    URL specified by [then] argument.

    See api for request and response documentation.
    '''
    url = users.create_logout_url(dest_url=self.request.get('then'))
    self.redirect(url)