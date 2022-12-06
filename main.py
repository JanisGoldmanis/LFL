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

print(game)

# Generating NEO4J data
transaction_execution_commands = []


def delete_all():
    return "MATCH (n) DETACH DELETE n"


neo4j_create_statement = delete_all()
transaction_execution_commands.append(neo4j_create_statement)

place = game.place
spectators = game.spectators
date = game.date
referees = game.referees
teams = game.teams
team1 = teams[0].name
team2 = teams[1].name

neo4j_create_statement = "MERGE (g:GAME {place:'%s', date:'%s', spectators:%d}) \
                          WITH g MERGE (t1:TEAM {name:'%s'}) \
                          WITH g,t1 MERGE (t2:TEAM {name:'%s'})\
                          WITH g,t1,t2 \
                          MERGE (t1)-[:PLAYED_IN]->(g)\
                          WITH g,t2\
                          MERGE (t2)-[:PLAYED_IN]->(g)" \
                         % (place, date, spectators, team1, team2)
transaction_execution_commands.append(neo4j_create_statement)

# for referee in referees:
#     neo4j_create_statement =
#
#     transaction_execution_commands.append(neo4j_create_statement)
for referee in referees:
    name = referee.Name
    surname = referee.Surname
    neo4j_create_statement = "MERGE (r:REFEREE {name:'%s', surname:'%s'}) " \
                             "WITH r MATCH (game:GAME) WHERE game.date = '%s' AND game.place = '%s' " \
                             "MERGE (r)-[:REFEREEING]->(game) " \
                             % (name, surname, date, place)

    transaction_execution_commands.append(neo4j_create_statement)



for team in teams:
    team_name = team.name
    for player in team.players:
        nr = player.number
        name = player.name
        surname = player.surname
        role = player.role
        neo4j_create_statement = "MERGE (p:PLAYER {nr:%d, name:'%s', surname:'%s', role:'%s',team:'%s'}) " \
                                 "WITH p MATCH (team:TEAM) WHERE team.name = '%s' " \
                                 "WITH p,team " \
                                 "MERGE (p)-[:PLAYS_FOR]->(team)" \
                                 % (nr, name, surname, role, team_name, team_name)
        transaction_execution_commands.append(neo4j_create_statement)
    for goal in team.goals:
        time = goal.time
        # passers = ""S
        # for passer in goal.passers:
        #     passers += "," + passer
        scorer = goal.scorer
        type = goal.type
        neo4j_create_statement = "MERGE (g:GOAL {time:'%s',scorer:%d,type:'%s',team:'%s'}) " \
                                 "WITH g MATCH (p:PLAYER) WHERE g.scorer = p.nr AND g.team = p.team " \
                                 "WITH g,p " \
                                 "MERGE (p)-[:SCORED]->(g) " \
                                 "WITH g MATCH (game:GAME) WHERE game.date = '%s' AND game.place = '%s' " \
                                 "MERGE (g)-[:GOAL]-(game)" \
                                 % (time, scorer, type, team_name, date, place)
        transaction_execution_commands.append(neo4j_create_statement)

    for penalty in team.warnings:
        time = penalty.Time
        nr = penalty.Nr
        neo4j_create_statement = "MERGE (w:PENALTY {time:'%s',nr:%d,team:'%s'}) " \
                                 "WITH w MATCH (p:PLAYER) WHERE w.nr = p.nr AND w.team = p.team " \
                                 "WITH w,p " \
                                 "MERGE (p)-[:PENALTY]->(w) " \
                                 "WITH w MATCH (game:GAME) WHERE game.date = '%s' AND game.place = '%s' " \
                                 "MERGE (w)-[:PENALTY]-(game)" \
                                 % (time, nr, team_name, date, place)
        transaction_execution_commands.append(neo4j_create_statement)


# neo4j_create_statement = "MATCH "

# neo4j_create_statement = "create (t:Transaction {transaction_id:1005})"
# transaction_execution_commands.append(neo4j_create_statement)

def execute_transactions(transaction_exection_commands):
    data_base_connection = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "password"))
    session = data_base_connection.session()
    for i in transaction_exection_commands:
        session.run(i)


execute_transactions(transaction_execution_commands)
