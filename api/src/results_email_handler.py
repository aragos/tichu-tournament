import StringIO
import json
from collections import defaultdict

from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.api.app_identity import get_application_id
from google.appengine.ext import ndb

from generic_handler import GenericHandler
from handler_utils import BuildMovementAndMaybeSetStatus
from handler_utils import CheckUserOwnsTournamentAndMaybeReturnStatus
from handler_utils import GetTourneyWithIdAndMaybeReturnStatus
from handler_utils import SetErrorStatus
from model_utils import ListOfModelBoardsToListOfBoards
from model_utils import ListOfScoredHandsToListOfDicts
from python import pdfrenderer
from python.calculator import Calculate
from python.calculator import GetMaxRounds
from python.calculator import OrderBy
from python.jsonio import ReadJSONInput
from python.teams import ExtractTeamNames
from python.xlsxio import OutputWorkbookAsBytesIO
from python.xlsxio import WriteResultsToXlsx


class ResultsEmailHandler(GenericHandler):
  """ Handles reuqests to /api/tournament/:id/resultsemail. Responsible for
  emailing players with the tournament results.
  """

  @ndb.toplevel
  def post(self, id):
    """ Sends an email with results to all email addresses in the request.
    Also cc's the director if the director is not in the list.
    Checks that emails belong to players in the tournament and sends the email
    only to valid addresses.

    Args: 
      id: tournament ID to look up. Tournament must already have been
          created.
    """
    user = users.get_current_user()
    tourney = GetTourneyWithIdAndMaybeReturnStatus(self.response, id)
    if not tourney:
      return
    if not CheckUserOwnsTournamentAndMaybeReturnStatus(self.response, user, tourney):
      return

    request_dict = self._ParseRequestAndMaybeSetStatus()
    if not request_dict:
      return

    scored_hands_future = tourney.GetScoredHandListAsync()
    player_futures = tourney.GetAllPlayerPairsAsync()
    boards_future = tourney.GetBoardsAsync()

    if not self._CheckIfAllHandsScoredAndMaybeSetStatus(tourney, scored_hands_future):
      return

    hand_list = ListOfScoredHandsToListOfDicts(scored_hands_future.get_result())
    hand_results = ReadJSONInput(hand_list)
    max_rounds = GetMaxRounds(hand_results)
    summaries = Calculate(hand_results, max_rounds)

    # TODO: Generate results asynchronously in parallel.
    xls_results = self._GenerateXlsxResults(hand_results, max_rounds, player_futures, summaries,
                                            tourney)

    boards = ListOfModelBoardsToListOfBoards(boards_future.get_result())
    pdf_results = self._GeneratePdfResults(boards, hand_results, player_futures, summaries, tourney)

    payloads = [xls_results, pdf_results]

    self._SendEmails(request_dict, user, tourney, player_futures, summaries, payloads)
    self.response.headers['Content-Type'] = 'application/json'
    self.response.set_status(201)

  def _GeneratePdfResults(self, boards, hand_results, player_futures, summaries, tourney):
    outputStream = StringIO.StringIO()
    pdfrenderer.RenderResultsToIo(tourney.name, boards, hand_results, summaries, player_futures,
                                  outputStream)
    pdf_results = outputStream.getvalue()
    return pdf_results

  def _GenerateXlsxResults(self, boards, max_rounds, player_futures, summaries, tourney):
    pair_list = _GetNamePairList(tourney, player_futures)
    return OutputWorkbookAsBytesIO(
      WriteResultsToXlsx(max_rounds, summaries, summaries, boards, name_list=pair_list)).getvalue()

  def _CheckIfAllHandsScoredAndMaybeSetStatus(self, tourney, scored_hands_future):
    """ Checks if all the hands in the tournament have been scored. If not, sets
    the appropriate status.
    
    Args:
      tourney: Tournament object.
      scored_hands_future: Future of a list of ScoredHand obects.

    Returns: True iff all hands are scored for this tournament.
    """
    movement = BuildMovementAndMaybeSetStatus(
      self.response, tourney.no_pairs, tourney.no_boards,
      tourney.legacy_version_id)
    if not movement:
      SetErrorStatus(self.response, 400, "Invalid Tournament",
                     "Cannot build movement for this tournament.")
      return False
    scored_hands = ListOfScoredHandsToListOfDicts(scored_hands_future.get_result())
    north_team_to_scored_hands = defaultdict(list)
    for hand in scored_hands:
      north_team_to_scored_hands[hand["ns_pair"]].append(hand["board_no"])
    for round_no in xrange(1, movement.GetNumRounds() + 1):
      for team_no in xrange(1, tourney.no_pairs + 1):
        round = movement.GetMovement(team_no)[round_no - 1]
        hands = round.hands
        if not hands or not round.is_north:
          continue
        for hand in hands:
          if hand not in north_team_to_scored_hands.get(team_no, []):
            SetErrorStatus(self.response, 400, "Cannot Compute Results",
                           "Not all hands are scored yet.")
            return False
    return True

  def _SendEmails(self, request_dict, user, tourney, tourney_player_pair_futures,
      summaries, payloads):
    """Sends a welcome email for all email addresses in the request_dict. Also
    cc's the tournament director if the director is not also a player.

    Args: 
      request_dict: Parsed JSON dict.
      user: The ndb.User owning this tournament.
      tourney: The tournament model object. 
    """
    assert len(summaries) > 3
    requested_emails = request_dict["emails"]
    OrderBy(summaries, "MP")

    found_tournament_director = False
    winner = ExtractTeamNames(summaries[0].team_no, tourney_player_pair_futures, "Team ")
    second_place = ExtractTeamNames(summaries[1].team_no, tourney_player_pair_futures, "Team ")
    third_place = ExtractTeamNames(summaries[2].team_no, tourney_player_pair_futures, "Team ")
    project_name = get_application_id()
    unnamed_email_text = """
\nThe great tournament by the name of \"{}\" is over. Our top three teams are 
1. {}
2. {}
3. {}
Congratulations! For the analytical sort among us, check out the hand record and detailed breakdowns attached.
\nHope you had fun and see you next time!
Your friendly neighborhood tournament director""".format(tourney.name, winner,
                                                         second_place, third_place)
    unnamed_email_html = """The great tournament by the name of \"{}\" is over. Congratuations to our top 3 teams!
<ol>
  <li>{}</li>
  <li>{}</li>
  <li>{}</li>
</ol>
For the analytical sort among us, check out the hand record and detailed breakdowns attached.
<br/>
<br/>Hope you had fun and see you next time!
<br/>Your friendly neighborhood tournament director
""".format(tourney.name, winner, second_place, third_place)

    attachment_files = [mail.Attachment('results.xlsx', payloads[0]),
                        mail.Attachment('boards.pdf', payloads[1])]
    for player_pair_future in tourney_player_pair_futures:
      player_pair = player_pair_future.get_result()
      for player in player_pair.player_list():
        player_email = player.get("email")
        if player_email == user.email():
          found_tournament_director = True
        if player_email not in requested_emails:
          continue
        player_name = player.get("name")
        player_greeting = "Hi there {},".format(player_name) if player_name else "Greetings!"
        self._SendEmailToAddress(user, "{} <results@{}.appspotmail.com>".format(tourney.name,
                                                                                project_name),
                                 player_email, unnamed_email_text, unnamed_email_html,
                                 player_greeting, attachment_files)
    if not found_tournament_director:
      self._SendEmailToAddress(user,
                               "{} <results@{}.appspotmail.com>".format(tourney.name, project_name),
                               user.email(), unnamed_email_text, unnamed_email_html,
                               "Hey Awesome Tournament Director, you did great!",
                               attachment_files)

  def _SendEmailToAddress(self, user, sender_address, player_email, unnamed_email_text,
      unnamed_email_html, player_greeting, attachment_files):
    """ Sends an email to the specifie address.

    Args:
      user: Tournament director, currently logged in user.
      sender_address: String. Address to send email from.
      player_email: String. Addressee's email.
      unnamed_email_text: String. Body of the email without the player's greeting.
      unnamed_email_html: String. HTML version of the email without the player's
        greeting.
      player_greeting: String. How to address the player.
      attachment_files: List of Attachment payloads to include.
    """
    email_text = "{}{}".format(player_greeting, unnamed_email_text)
    email_html = "{}<br/><br/>{}".format(player_greeting, unnamed_email_html)
    mail.send_mail(
      sender=sender_address,
      to=player_email,
      subject="Tichu Tournament Results",
      body=email_text,
      html=email_html,
      attachments=attachment_files,
      reply_to=user.email())

  def _ParseRequestAndMaybeSetStatus(self):
    """ Parses the client request for email sents an error status if the
        request is unreadable or the email list is empty. 

    Returns: dict corresponding to the parsed request.s
    """
    try:
      request_dict = json.loads(self.request.body)
    except ValueError:
      SetErrorStatus(self.response, 500, "Invalid Input",
                     "Unable to parse request body as JSON object")
      return None
    request_dict["emails"] = [e for e in request_dict["emails"] if e and e != ""]
    if len(request_dict["emails"]) == 0:
      SetErrorStatus(self.response, 400, "Invalid Input",
                     "No emails specified.")
      return None
    return request_dict


def _GetNamePairList(tourney, player_futures):
  """ Returns a list of tuples of names for every pair. If a name is not
  available, returns None for that player.
  """
  name_list = range(1, tourney.no_pairs + 1)
  for player_pair_future in player_futures:
    player_pair = player_pair_future.get_result()
    player_list = player_pair.player_list()
    if not player_list or len(player_list) == 0:
      name_list[player_pair.pair_no - 1] = (None, None)
    elif len(player_list) == 1:
      name_list[player_pair.pair_no - 1] = (player_list[0].get("name"),
                                            None)
    else:
      name_list[player_pair.pair_no - 1] = (player_list[0].get("name"),
                                            player_list[1].get("name"))
  return name_list
