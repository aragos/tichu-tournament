"""Utilities for interacting with teams."""


def ExtractTeamNames(team_number, player_pair_future, team_prefix=""):
  """ Formats the team number and names from a TeamSummaries object. """
  player_pair = player_pair_future[team_number - 1].get_result()
  player_list = filter(lambda x: x.get("name"), player_pair.player_list())
  if len(player_list) == 0:
    team_names = "2 Awesome Players"
  elif len(player_list) == 1:
    team_names = "{} and an Awesome Partner".format(player_list[0].get("name"))
  else:
    team_names = "{} and {}".format(player_list[0].get("name"),
                                    player_list[1].get("name"))
  return "{}{} ({})".format(team_prefix, team_number, team_names)
