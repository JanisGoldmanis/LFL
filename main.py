import json
from neo4j import GraphDatabase

import Game
import Team
import Player
import Referee
import Goals
import Substitution
import Warnings

keywords_substitution = ["Laiks", "Nr1", "Nr2"]
keywords_warnings = ["Laiks", "Nr"]
keywords_referees = ["Uzvards", "Vards"]
keywords_teams = ["Nosaukums"]
keywords_player = ["Vards", "Uzvards", "Loma", "Nr"]


def load_substitutions(dictionary, keyword="Mainas", sub_keyword="Maina", sub_dict_keywords=["Laiks", "Nr1", "Nr2"],
                       team=Team.Team(), debug=False):
    substitutions = []
    local_dict = dictionary[keyword]
    number_of_substitutions = len(local_dict)
    if debug:
        print("Number of substitutions in protocol:", number_of_substitutions)
    if number_of_substitutions == 0:
        print("No Substitutions")
    elif number_of_substitutions == 1:
        if debug:
            print(local_dict[sub_keyword])
        local_dict = local_dict[sub_keyword]
        sub = Substitution.Substitution(local_dict[sub_dict_keywords[0]], local_dict[sub_dict_keywords[1]],
                                        local_dict[sub_dict_keywords[2]])
        if debug:
            print(sub)
        substitutions.append(sub)
    else:
        print("Parse multiple substitutions!")
    team.substitutions = substitutions
    dictionary.pop(keyword)


def load_warnings(dictionary, keyword="Sodi", sub_keyword="Sods", sub_dict_keywords=["Laiks", "Nr"], team=Team.Team(),
                  debug=False):
    warnings = []
    local_dict = dictionary[keyword][sub_keyword]
    if debug:
        print("Warnings:", local_dict, "Type:", type(local_dict))
    if isinstance(local_dict, dict):
        warning = Warnings.Warning(local_dict[sub_dict_keywords[0]], local_dict[sub_dict_keywords[1]])
        warnings.append(warning)
    if isinstance(local_dict, list):
        for warning_dict in local_dict:
            warning = Warnings.Warning(warning_dict[sub_dict_keywords[0]], warning_dict[sub_dict_keywords[1]])
            warnings.append(warning)
    team.warnings = warnings
    dictionary.pop(keyword)


def generate_referees(dictionary, keyword="Spele", sub_keyword="T", sub_dict_keywords=["Uzvards", "Vards"]):
    referees = []
    for referee_dict in dictionary[keyword][sub_keyword]:
        referees.append(Referee.Referee(referee_dict[sub_dict_keywords[0]], referee_dict[sub_dict_keywords[1]]))
    return referees


def generate_teams(dictionary, keyword="Spele", sub_keyword="Komanda", sub_dict_keywords=["Nosaukums"], debug=False):
    teams = []
    for team_dict in dictionary[keyword][sub_keyword]:
        if debug:
            print("Team name:", team_dict[sub_dict_keywords[0]])
        team = Team.Team(team_dict[sub_dict_keywords[0]])
        team_dict.pop(sub_dict_keywords[0])
        players = generate_players(team_dict)
        team.players = players
        starters = generate_starters(team_dict)
        team.starting = starters
        goals = generate_goals(team_dict)
        team.goals = goals

        load_substitutions(team_dict, sub_dict_keywords=keywords_substitution, team=team, debug=False)
        load_warnings(team_dict, sub_dict_keywords=keywords_warnings, team=team, debug=False)
        teams.append(team)
    if debug:
        print("Team quantity from parsing:", len(teams))
    return teams


def generate_players(dictionary, keyword="Speletaji", sub_keyword="Speletajs",
                     sub_dict_keywords=None, debug=False):
    if sub_dict_keywords is None:
        sub_dict_keywords = ["Vards", "Uzvards", "Loma", "Nr"]
    players = []
    name = sub_dict_keywords[0]
    surname = sub_dict_keywords[1]
    role = sub_dict_keywords[2]
    nr = sub_dict_keywords[3]
    if debug:
        print(dictionary[keyword][sub_keyword])
    for player_dict in dictionary[keyword][sub_keyword]:
        player = Player.Player(player_dict[name], player_dict[surname], player_dict[role], player_dict[nr])
        players.append(player)
    dictionary.pop(keyword)
    return players


def generate_starters(dictionary, keyword="Pamatsastavs", subkeyword="Speletajs", sub_dict_keywords=["Nr"]):
    nr = sub_dict_keywords[0]
    starters = []
    for starter_dict in dictionary[keyword][subkeyword]:
        starters.append(starter_dict[nr])
    dictionary.pop(keyword)
    return starters


def generate_goals(dictionary, keyword="Varti", subkeyword="VG", sub_dict_keywords=["Laiks", "P", "Nr", "Sitiens"]):
    time = sub_dict_keywords[0]
    assists = sub_dict_keywords[1]
    nr = sub_dict_keywords[2]
    type = sub_dict_keywords[3]
    goals = []
    for goal_dict in dictionary[keyword][subkeyword]:
        goal = Goals.Goals(goal_dict[time], goal_dict[assists], goal_dict[nr], goal_dict[type])
        goals.append(goal)
    dictionary.pop(keyword)
    return goals


def generate_game(dictionary, referees, teams, keyword="Spele", sub_dict_keywords=["Laiks", "Skatitaji", "Vieta"]):
    date = sub_dict_keywords[0]
    spectators = sub_dict_keywords[1]
    place = sub_dict_keywords[2]
    game_dict = dictionary[keyword]
    game = Game.Game(game_dict[date], game_dict[spectators], game_dict[place], referees, teams)
    game_dict.pop(date)
    game_dict.pop(spectators)
    game_dict.pop(place)
    game_dict.pop("T")
    game_dict.pop("Komanda")
    return game


with open('futbols0.json', 'r') as file:
    game_data = json.load(file)
    referees = generate_referees(game_data, sub_dict_keywords=keywords_referees)
    teams = generate_teams(game_data)
    game = generate_game(game_data, referees, teams)




# transaction_execution_commands = []

# neo4j_create_statement = "create (t:Transaction {transaction_id:1001})"
# transaction_execution_commands.append(neo4j_create_statement)
# neo4j_create_statement = "create (t:Transaction {transaction_id:1005})"
# transaction_execution_commands.append(neo4j_create_statement)

def execute_transactions(transaction_exection_commands):
    data_base_connection = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "password"))
    session = data_base_connection.session()
    for i in transaction_exection_commands:
        session.run(i)

def delete_all():
    return "MATCH (n) DETACH DELETE n"

# neo4j_create_statement = delete_all()
# transaction_execution_commands.append(neo4j_create_statement)

# execute_transactions(transaction_execution_commands)
