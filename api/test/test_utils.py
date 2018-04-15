import os, sys

sys.path.append(os.path.join(os.getcwd(), 'api/src'))
from models import Tournament

def loginUser(self, email='user@example.com', id='123', is_admin=False):
  self.testbed.setup_env(
    user_email=email,
    user_id=id,
    user_is_admin='1' if is_admin else '0',
    overwrite=True)

def setLegacyId(self, id='123', version=1):
  tourney = Tournament.get_by_id(int(id));
  tourney.legacy_version_id = version
  tourney.put()