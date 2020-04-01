from datetime import date

from django.core.management.base import BaseCommand

from nfl import NflApiClient
from nfl.defines import GamePhase, SeasonType
from nfl.models import Game, Team, Week, Year

WeekMapping = {
    1: (SeasonType.HALL_OF_FAME.value, 1),
    2: (SeasonType.PRE_SEASON.value, 1),
    3: (SeasonType.PRE_SEASON.value, 2),
    4: (SeasonType.PRE_SEASON.value, 3),
    5: (SeasonType.PRE_SEASON.value, 4),
    6: (SeasonType.REGULAR_SEASON.value, 1),
    7: (SeasonType.REGULAR_SEASON.value, 2),
    8: (SeasonType.REGULAR_SEASON.value, 3),
    9: (SeasonType.REGULAR_SEASON.value, 4),
    10: (SeasonType.REGULAR_SEASON.value, 5),
    11: (SeasonType.REGULAR_SEASON.value, 6),
    12: (SeasonType.REGULAR_SEASON.value, 7),
    13: (SeasonType.REGULAR_SEASON.value, 8),
    14: (SeasonType.REGULAR_SEASON.value, 9),
    15: (SeasonType.REGULAR_SEASON.value, 10),
    16: (SeasonType.REGULAR_SEASON.value, 11),
    17: (SeasonType.REGULAR_SEASON.value, 12),
    18: (SeasonType.REGULAR_SEASON.value, 13),
    19: (SeasonType.REGULAR_SEASON.value, 14),
    20: (SeasonType.REGULAR_SEASON.value, 15),
    21: (SeasonType.REGULAR_SEASON.value, 16),
    22: (SeasonType.REGULAR_SEASON.value, 17),
    23: (SeasonType.POST_SEASON.value, 1),  # Wild Card Weekend
    24: (SeasonType.POST_SEASON.value, 2),  # Divisional Playoffs
    25: (SeasonType.POST_SEASON.value, 3),  # Conference Championships
    26: (SeasonType.PRO_BOWL.value, 1),  # Pro Bowl
    27: (SeasonType.SUPER_BOWL.value, 1),  # Super Bowl
}


class Command(BaseCommand):
    help = 'Update nfl games in the database'

    def add_arguments(self, parser):
        parser.add_argument('-s', '--season', type=int, help='Season for which to import game data')
        parser.add_argument('-w', '--week', type=int, help='Week within a season for which to import game data [1-27]')

    def handle(self, *args, **kwargs):
        now = date.today()
        season = kwargs['season'] or now.year if now.month > 8 else now.year - 1
        week = kwargs['week']

        year_object = Year.objects.get_or_create(year=season)[0]

        client = NflApiClient()
        existing_games = 0
        updated_games = 0
        create_games = []
        if week:
            week_mappings = [(week, WeekMapping.get(week))]
        else:
            week_mappings = WeekMapping.items()
        for week, week_mapping in week_mappings:
            api_games = client.get_games(
                season=season,
                week=week_mapping[1],
                season_type=week_mapping[0]
            )
            if not len(api_games.get('data', [])):
                break
            week_object = Week.objects.get_or_create(year=year_object, week=week)[0]
            for game in api_games.get('data', []):
                try:
                    home_team = Team.objects.get(abbr=game['homeTeam']['abbr'])
                    visitor_team = Team.objects.get(abbr=game['visitorTeam']['abbr'])
                except Team.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"Team {game['homeTeam']['abbr']} or {game['visitorTeam']['abbr']} does not exist in game={game}"
                    ))
                    continue
                try:
                    cur_game = Game.objects.get(
                        week=week_object,
                        home_team=home_team,
                        visitor_team=visitor_team
                    )
                    if hasattr(game, 'gameStatus'):
                        if game['gameStatus'].get('phase', 1) > GamePhase.SUSPENDED:
                            cur_game.final = True
                            if hasattr(game, 'homeTeamScore'):
                                cur_game.home_team_score = game['homeTeamScore'].get('pointsTotal', None)
                            if hasattr(game, 'visitorTeamScore'):
                                cur_game.home_team_score = game['visitorTeamScore'].get('pointsTotal', None)
                            cur_game.save()
                            updated_games += 1
                except Game.DoesNotExist:
                    create_games.append(Game(
                        week=week_object,
                        home_team=home_team,
                        visitor_team=visitor_team,
                        timestamp=game['gameTime']
                    ))
                existing_games += 1
        if len(create_games):
            Game.objects.bulk_create(create_games)
        self.stdout.write((
            f"Inserted {len(create_games)} and updated {updated_games} of {existing_games} games"
            f" for {season}{'-' + week if len(week_mappings) == 1 else ''} in db"
        ))
