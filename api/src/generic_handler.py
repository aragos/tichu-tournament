import sys
import traceback
import webapp2

from handler_utils import SetErrorStatus


class GenericHandler(webapp2.RequestHandler):
  ''' Generic handler that all server side handler should extend. '''

  #def handle_exception(self, exception, debug_mode):
  #  ''' Save relevant error details in any unexpected exception. '''
  #  super(GenericHandler, self).handle_exception(exception, debug_mode)
  #  SetErrorStatus(self.response, 500, "Unexpected Error", str(exception))
