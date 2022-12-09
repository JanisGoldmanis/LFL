import json
from neo4j import GraphDatabase

import Game
import Referee
import HeadReferee
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


def load_substitutions(dictionary, team, extended=False):
    """
    :param dictionary: Full JSON dictionary
    :param team: Team class object
    :param extended: Boolean for debug
    :return: None. Modifies team object substitutions within method
    At the end, "Mainas" is removed from dictionary
    """
    # No substitutions in json
    if len(dictionary["Mainas"]) == 0:
        if extended:
            print('No substitutions')
        dictionary.pop("Mainas")
        return

    substitutions = []
    # Multiple substitutions
    if isinstance(dictionary["Mainas"]["Maina"], list):
        for sub in dictionary["Mainas"]["Maina"]:
            substitution = Substitution.Substitution(sub["Laiks"], sub["Nr1"], sub["Nr2"])
            substitutions.append(substitution)
    # Single substitution
    else:
        sub = dictionary["Mainas"]["Maina"]
        substitution = Substitution.Substitution(sub["Laiks"], sub["Nr1"], sub["Nr2"])
        substitutions.append(substitution)

    team.substitutions = substitutions
    if extended:
        print(len(substitutions), 'total substitutions')
    dictionary.pop("Mainas")
    pass


def load_warnings(dictionary, team, extended=False):
    # No warnings in json
    if len(dictionary["Sodi"]) == 0:
        if extended:
            print('No warnings')
        dictionary.pop("Sodi")
        return

    warnings = []
    # Multiple warnings
    if isinstance(dictionary["Sodi"]["Sods"], list):
        for warning in dictionary["Sodi"]["Sods"]:
            w = Warnings.Warning(warning["Laiks"], warning["Nr"])
            warnings.append(w)
    # Single warning
    else:
        warning = dictionary["Sodi"]["Sods"]
        w = Warnings.Warning(warning["Laiks"], warning["Nr"])
        warnings.append(w)

    team.warnings = warnings
    if extended:
        print(len(warnings), 'total warnings')
    dictionary.pop("Sodi")
    pass


def generate_referees(dictionary, extended=False):
    referees = []
    for referee_dict in dictionary["Spele"]["T"]:
        referees.append(Referee.Referee(referee_dict["Uzvards"], referee_dict["Vards"]))
    if extended:
        print('Loaded', len(referees), 'referees')
    return referees


def generate_head_referees(dictionary, keyword="Spele", sub_keyword="VT", sub_dict_keywords=["Uzvards", "Vards"]):
    print('Adding head referee')
    referee_dict = dictionary[keyword][sub_keyword]
    referee = HeadReferee.HeadReferee(referee_dict[sub_dict_keywords[0]], referee_dict[sub_dict_keywords[1]])
    return referee


def generate_teams(dictionary, keyword="Spele", sub_keyword="Komanda", sub_dict_keywords=["Nosaukums"], debug=False,
                   extended=False):
    teams = []
    for team_dict in dictionary[keyword][sub_keyword]:
        if debug:
            print("Team name:", team_dict[sub_dict_keywords[0]])
        team = Team.Team(team_dict[sub_dict_keywords[0]])
        team_dict.pop(sub_dict_keywords[0])
        print('Team', team.name)
        players = generate_players(team_dict)
        print(len(players), 'players')
        team.players = players
        starters = generate_starters(team_dict)
        print(len(starters), 'starters')
        team.starting = starters
        goals = generate_goals(team_dict)
        print(len(goals), 'total goals')
        team.goals = goals
        load_substitutions(team_dict, team, extended=extended)
        load_warnings(team_dict, team, extended=extended)
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
    print(dictionary[keyword])
    print(len(dictionary[keyword]))
    if isinstance(dictionary[keyword][subkeyword], list):
        number_of_goals = len(dictionary[keyword][subkeyword])
    else:
        number_of_goals = len(dictionary[keyword])

    if number_of_goals > 1:
        for goal_dict in dictionary[keyword][subkeyword]:
            try:
                goal = Goals.Goals(goal_dict[time], goal_dict[assists], goal_dict[nr], goal_dict[type])
            except KeyError:
                goal = Goals.Goals(goal_dict[time], [], goal_dict[nr], goal_dict[type])
            goals.append(goal)
            print(goal)
    if number_of_goals == 1:
        goal_dict = dictionary[keyword][subkeyword]
        try:
            goal = Goals.Goals(goal_dict[time], goal_dict[assists], goal_dict[nr], goal_dict[type])
        except KeyError:
            goal = Goals.Goals(goal_dict[time], [], goal_dict[nr], goal_dict[type])
        goals.append(goal)
        print(goal)

    dictionary.pop(keyword)
    return goals


def generate_game(dictionary, referees, teams, head_referee, keyword="Spele",
                  sub_dict_keywords=["Laiks", "Skatitaji", "Vieta"]):
    date = sub_dict_keywords[0]
    spectators = sub_dict_keywords[1]
    place = sub_dict_keywords[2]
    game_dict = dictionary[keyword]
    game = Game.Game(game_dict[date], game_dict[spectators], game_dict[place], referees, teams, head_referee)
    game_dict.pop(date)
    game_dict.pop(spectators)
    game_dict.pop(place)
    game_dict.pop("T")
    game_dict.pop("VT")
    game_dict.pop("Komanda")
    return game


extended = False

with open('futbols1.json', 'r') as file:
    game_data = json.load(file)
    head_referee = generate_head_referees(game_data, sub_dict_keywords=keywords_referees)
    referees = generate_referees(game_data, sub_dict_keywords=keywords_referees)
    teams = generate_teams(game_data, extended=extended)
    game = generate_game(game_data, referees, teams, head_referee)
    print('Leftover:', game_data)

# Generating NEO4J data
transaction_execution_commands = []


def delete_all():
    return "MATCH (n) DETACH DELETE n"


# neo4j_create_statement = delete_all()
# transaction_execution_commands.append(neo4j_create_statement)

place = game.place
spectators = game.spectators
date = game.date
referees = game.referees
head_referee = game.head_referee
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

for referee in referees:
    name = referee.Name
    surname = referee.Surname
    neo4j_create_statement = "MERGE (r:REFEREE {name:'%s', surname:'%s'}) " \
                             "WITH r MATCH (game:GAME) WHERE game.date = '%s' AND game.place = '%s' " \
                             "MERGE (r)-[:REFEREEING]->(game) " \
                             % (name, surname, date, place)
    transaction_execution_commands.append(neo4j_create_statement)

name = head_referee.Name
surname = head_referee.Surname
neo4j_create_statement = "MERGE (r:HEAD_REFEREE {name:'%s', surname:'%s'}) " \
                         "WITH r MATCH (game:GAME) WHERE game.date = '%s' AND game.place = '%s' " \
                         "MERGE (r)-[:HEAD_REFEREEING]->(game) " \
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
