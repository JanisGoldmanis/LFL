from neo4j import GraphDatabase


class Team():
    def __init__(self, name=""):
        self.name = name
        self.games_played = 0
        self.goals_for = 0
        self.goals_against = 0
        self.wins_normal = 0
        self.wins_ot = 0
        self.loses_ot = 0
        self.loses = 0
        self.points = 0

    def __str__(self):
        return self.name


def get_data():
    driver = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "password"))
    with driver.session() as session:
        query = """
            MATCH (g:GAME)<-[:PLAYED_IN]-(t:TEAM)
            OPTIONAL MATCH (g)<-[r:GOAL]-(goal:GOAL)
            RETURN g, collect(DISTINCT t) as teams, collect(DISTINCT goal) as goals
        """
        results = session.run(query)

        games_teams_goals = []
        for record in results:
            game = dict(record["g"])
            teams = [dict(team) for team in record["teams"]]
            goals = [dict(goal) for goal in record["goals"]]
            game["teams"] = teams
            game["goals"] = goals
            games_teams_goals.append(game)

        set_of_teams = set()
        list_of_teams = []

        for entry in games_teams_goals:
            teams = entry['teams']
            for team in teams:
                if team['name'] not in set_of_teams:
                    set_of_teams.add(team['name'])
                    list_of_teams.append(Team(team['name']))
            team1 = teams[0]['name']
            score1 = 0
            team2 = teams[1]['name']
            score2 = 0
            latest_goal_time = 0
            goals = entry['goals']
            for goal in goals:
                time_str = goal['time']
                minutes, seconds = time_str.split(':')
                time = int(minutes) * 60 + int(seconds)
                if time > latest_goal_time:
                    latest_goal_time = time
                if goal['team'] == team1:
                    score1 += 1
                else:
                    score2 += 1

            Team1 = Team
            Team2 = Team

            for team in list_of_teams:
                if team1 == team.name:
                    Team1 = team
                if team2 == team.name:
                    Team2 = team

            # Regulation
            Team1.games_played += 1
            Team2.games_played += 1
            Team1.goals_for += score1
            Team1.goals_against += score2
            Team2.goals_for += score2
            Team2.goals_against += score1

            if latest_goal_time <= 60 * 60:
                points_winner = 5
                points_loser = 1
                win = 1
                loss = 1
                ot_win = 0
                ot_loss = 0
            else:
                points_winner = 3
                points_loser = 2
                win = 0
                loss = 0
                ot_win = 1
                ot_loss = 1

            if score1 > score2:
                Team1.points += points_winner
                Team2.points += points_loser
                Team1.wins_normal += win
                Team1.wins_ot += ot_win
                Team2.loses += loss
                Team2.loses_ot += ot_loss
            else:
                Team2.points += points_winner
                Team1.points += points_loser
                Team2.wins_normal += win
                Team2.wins_ot += ot_win
                Team1.loses += loss
                Team1.loses_ot += ot_loss

        print('|     Team      | Pts | GP| W |OTW|OTL| L | GF| GA|')

        for team in list_of_teams:
            print(team, team.points, team.games_played)
