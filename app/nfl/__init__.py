from datetime import date

from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749.wrappers import OAuth2Token
from django.http import HttpResponse


class NflApiClient(object):
    instance = None

    class __NflApiClient:
        api_base_url = 'https://api.nfl.com/v1'

        @staticmethod
        def update_token(token, refresh_token=None, access_token=None):
            print("update_token called:", token, refresh_token, access_token)
            if refresh_token:
                item = OAuth2Token.find(
                    name='nfl', refresh_token=refresh_token
                )
            elif access_token:
                item = OAuth2Token.find(
                    name='nfl', access_token=access_token
                )
            else:
                return

            # update old token
            item.access_token = token['access_token']
            item.refresh_token = token.get('refresh_token', None)
            item.expires_at = token['expires_at']
            item.save()

        def __init__(self):
            self.oauth_client = OAuth2Session(
                client_id='dyZHpNCWN5iuPx1gdbE3Dx9JAJIzZSCQ',
                client_secret='abD8E45RS31lZIHZhqoev5Zr78JO8j4W',
                grant_type='client_credentials',
                name='nfl',
                api_base_url='https://api.nfl.com/v1',
                token_endpoint='https://api.nfl.com/v1/oauth/token',
                token_endpoint_auth_method='client_secret_post',
                token_placement='header',
                update_token=NflApiClient.__NflApiClient.update_token
            )
            self.oauth_client.fetch_access_token()

        def get(self, url_suffix: str = None) -> HttpResponse:
            if url_suffix:
                if url_suffix[0] != '/':
                    url_suffix = f'/{url_suffix[0:]}'
                return self.oauth_client.get(
                    f'{self.api_base_url}{url_suffix}'
                )
            return HttpResponse()

        def get_games(
            self, season: int = None, week: int = None,
            season_type: str = 'REG', with_game_stats: bool = False
        ) -> dict:
            if season is None and week is None:
                return {}
            # TODO: Check week and season_type combination

            field_selector = '{gameTime,homeTeam{abbr},visitorTeam{abbr},stadiumInfo{name}}'
            if with_game_stats:
                field_selector = (
                    f'{field_selector[0:-2]},'
                    'homeTeamScore{pointsTotal},'
                    'visitorTeamScore{pointsTotal},'
                    f'gameStatus{{phase}}{field_selector[-2:]}'
                )
            query = f'{{"$query":{{"week.season":{season},"week.seasonType":"{season_type}","week.week":{week}}}}}'

            r = self.get(f'/games?fs={field_selector}&s={query}')
            if r and r.status_code == 200:
                return r.json()
            print(f"[{r.status_code}] Could not get games for season={season}, week={week} and season_type={season_type}: {r.text}")
            return {}

        def get_team(self, season: int = None, team_abbr: str = None) -> dict:
            if season is None:
                now = date.today()
                season = now.year if now.month > 8 else now.year - 1
            field_selector = '{abbr,fullName,teamType,branding{logos},standings{overallWins,overallLosses,overallTies}}'
            if team_abbr:
                query = f'{{"$query":{{"season":{season},"abbr":"{team_abbr}"}},"$take":40}}'
            else:
                query = f'{{"$query":{{"season":{season}}},"$take":40}}'
            r = self.get(f'/teams?fs={field_selector}&s={query}')
            if r and r.status_code == 200:
                return r.json()
            print(f"[{r.status_code}] Could not get team info for {team_abbr}: {r.text}")
            return {}

    def __new__(cls):
        if NflApiClient.instance is None:
            NflApiClient.instance = NflApiClient.__NflApiClient()
        return NflApiClient.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)
