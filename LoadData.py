import json


import Game
import Referee
import HeadReferee
import Team
import Player
import Goals
import Substitution
import Warnings

def load_data(fileName):
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

    def generate_head_referees(dictionary, extended=False):
        if extended:
            print('Adding head referee')
        referee_dict = dictionary["Spele"]["VT"]
        referee = HeadReferee.HeadReferee(referee_dict["Uzvards"], referee_dict["Vards"])
        return referee

    def generate_teams(dictionary, extended=False):
        teams = []
        for team_dict in dictionary["Spele"]["Komanda"]:
            team = Team.Team(team_dict["Nosaukums"])
            team_dict.pop("Nosaukums")
            if extended:
                print()
                print('Team', team.name)

            # Players
            players = generate_players(team_dict, extended)
            team.players = players

            # Starters
            starters = generate_starters(team_dict, extended)
            team.starting = starters

            # Goals
            goals = generate_goals(team_dict, extended)
            team.goals = goals

            load_substitutions(team_dict, team, extended=extended)
            load_warnings(team_dict, team, extended=extended)

            teams.append(team)

        if extended:
            print(len(teams), "teams loaded")

        return teams

    def generate_players(dictionary, extended=False):
        players = []
        local_dict = dictionary["Speletaji"]["Speletajs"]
        for player_dict in local_dict:
            player = Player.Player(player_dict["Vards"], player_dict["Uzvards"], player_dict["Loma"], player_dict["Nr"])
            players.append(player)
        dictionary.pop("Speletaji")
        if extended:
            print(len(players), "players added")
        return players

    def generate_starters(dictionary, extended=False):
        starters = []
        for starter_dict in dictionary["Pamatsastavs"]["Speletajs"]:
            starters.append(starter_dict["Nr"])
        dictionary.pop("Pamatsastavs")
        if extended:
            print(len(starters), "starters added")
        return starters

    def generate_goals(dictionary, extended=False, debug=False):
        # No goals in json
        if len(dictionary["Varti"]) == 0:
            if extended:
                print('No goals')
            dictionary.pop("Varti")
            return []

        goals = []
        # Multiple goals
        if isinstance(dictionary["Varti"]["VG"], list):
            for g in dictionary["Varti"]["VG"]:
                try:
                    goal = Goals.Goals(g["Laiks"], g["P"], g["Nr"], g["Sitiens"])
                except KeyError:
                    goal = Goals.Goals(g["Laiks"], [], g["Nr"], g["Sitiens"])
                goals.append(goal)
        # Single goal
        else:
            g = dictionary["Varti"]["VG"]
            try:
                goal = Goals.Goals(g["Laiks"], g["P"], g["Nr"], g["Sitiens"])
            except KeyError:
                goal = Goals.Goals(g["Laiks"], [], g["Nr"], g["Sitiens"])
            goals.append(goal)

        if extended:
            print(len(goals), 'total goals')
        dictionary.pop("Varti")
        return goals

    def generate_game(dictionary, referees, teams, head_referee, extended=False):
        game_dict = dictionary["Spele"]
        game = Game.Game(game_dict["Laiks"], game_dict["Skatitaji"], game_dict["Vieta"], referees, teams, head_referee)
        game_dict.pop("Laiks")
        game_dict.pop("Skatitaji")
        game_dict.pop("Vieta")
        game_dict.pop("T")
        game_dict.pop("VT")
        game_dict.pop("Komanda")
        if extended:
            print('Generating game', game.date, game.place)
        return game

    extended = False

    filename = fileName
    with open(filename, 'r') as file:
        if extended:
            print()
            print('Loading', filename)
        game_data = json.load(file)
        head_referee = generate_head_referees(game_data, extended)
        referees = generate_referees(game_data, extended)
        teams = generate_teams(game_data, extended=extended)
        game = generate_game(game_data, referees, teams, head_referee, extended)
        # print('Leftover:', game_data)

    # Generating NEO4J data
    transaction_execution_commands = []

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

    return transaction_execution_commands