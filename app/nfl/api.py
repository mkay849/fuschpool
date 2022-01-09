import asyncio
import httpx
import logging
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from asgiref.sync import sync_to_async
from django.db.models.base import Model

from nfl.defines import SeasonType
from nfl.models import Game, Week, Year

logger = logging.getLogger("EspnApiClient")


class EspnApiClient(object):
    api_base_url = "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
    httpx_limits = httpx.Limits(max_keepalive_connections=2, max_connections=5)
    dt_format_str = "%Y-%m-%dT%H:%M%z"

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    @sync_to_async
    def _get_or_create(self, object_class: Model, **kwargs):
        defaults_dict: dict = kwargs.pop("defaults")
        cur_object, created = object_class.objects.get_or_create(
            **kwargs, defaults=defaults_dict,
        )
        if created:
            updated_fields = []
            for k, v in defaults_dict.items():
                if getattr(cur_object, k) != v:
                    setattr(cur_object, k, v)
                    updated_fields.append(k)
            if len(updated_fields):
                cur_object.save(update_fields=updated_fields)
        return cur_object

    def check_games(self, event_ids: List[int] = None) -> List[Game]:
        """Check all started but not final games or a given list of event ids and update the database"""
        try:
            if event_ids is None:
                not_ts = datetime.now(timezone.utc)
                missing_games = Game.objects.filter(timestamp__lt=not_ts, final=False)
            else:
                missing_games = Game.objects.filter(event_id__in=event_ids)
        except Game.DoesNotExist:
            missing_games = Game.objects.none()
        if missing_games.exists():
            missing_games = list(missing_games)
            logger.info(f"Trying to update {len(missing_games)}")
            return self.loop.run_until_complete(self.check_games_async(missing_games))
        logger.info("There were no games to update")
        return []

    async def check_games_async(self, missing_games: List[Game]) -> List[Game]:
        """Check all started but not final games or a given list of event ids asynchronously and update the database"""
        updated_games = []
        async with httpx.AsyncClient(limits=self.httpx_limits) as client:
            for game in missing_games:
                event_url = f"{self.api_base_url}/events/{game.event_id}/competitions/{game.event_id}/competitors"
                event = await client.get(event_url)
                if event.status_code != 200:
                    continue
                event_json = event.json()
                if competitors := event_json.get("items"):
                    comp_res = await self._process_competitors(competitors, client)
                    if comp_res is None:
                        logger.info(
                            f"Teams unknown for game on {event_json['date']}. Skipping..."
                        )
                        continue
                    updated = False
                    if game.final != comp_res["final"]:
                        game.final = comp_res["final"]
                        updated = True
                    cur_score = comp_res["home"]["score"]
                    if cur_score and game.home_team_score != cur_score:
                        game.home_team_score = cur_score
                        updated = True
                    cur_score = comp_res["visitor"]["score"]
                    if cur_score and game.visitor_team_score != cur_score:
                        game.visitor_team_score = cur_score
                        updated = True
                    if updated:
                        updated_games.append(game)
        if len(updated_games):
            await sync_to_async(Game.objects.bulk_update)(
                updated_games, ["final", "home_team_score", "visitor_team_score"]
            )
        return updated_games

    def import_games(self) -> List[Game]:
        try:
            missing_weeks = Week.objects.filter(games__isnull=True).select_related(
                "year"
            )
        except Week.DoesNotExist:
            missing_weeks = Week.objects.none()
        res = []
        if missing_weeks.exists():
            missing_weeks = list(missing_weeks)
            gather_res = self.loop.run_until_complete(
                asyncio.gather(
                    *[self.import_games_async(week) for week in missing_weeks]
                )
            )
            for gr in gather_res:
                res.extend(gr)
        return res

    async def import_games_async(self, week_object: Week) -> List[Game]:
        games = []

        season = week_object.year.value
        season_type = week_object.season_type
        week = week_object.nfl_week

        events_url = f"{self.api_base_url}/seasons/{season}/types/{season_type}/weeks/{week}/events"
        async with httpx.AsyncClient(limits=self.httpx_limits) as client:
            events_res = await client.get(events_url)
            if events_res.status_code != 200:
                logger.warning(
                    f"Could not query list of events for season={season} season_type={season_type} week={week}: {events_res.reason}"
                )
                return []
            events_json = events_res.json()
            for event in events_json["items"]:
                event_res = await client.get(event["$ref"])
                if event_res.status_code != 200:
                    logger.warning(f"Could not query event: {event_res.reason}")
                    continue
                event_json = event_res.json()
                competitors = event_json["competitions"][0]["competitors"]
                comp_res = await self._process_competitors(competitors, client)
                if comp_res is None:
                    logger.info(
                        f"Teams unknown for game on {event_json['date']}. Skipping..."
                    )
                    continue
                event_timestamp = datetime.strptime(
                    event_json["date"], self.dt_format_str
                )
                cur_game = await self._get_or_create(
                    Game,
                    event_id=event_json["id"],
                    defaults={
                        "week_id": week_object.id,
                        "timestamp": event_timestamp,
                        "home_team_id": comp_res["home"]["team_id"],
                        "home_team_score": comp_res["home"]["score"]
                        if comp_res["home"]["score"]
                        else None,
                        "visitor_team_id": comp_res["visitor"]["team_id"],
                        "visitor_team_score": comp_res["visitor"]["score"]
                        if comp_res["visitor"]["score"]
                        else None,
                        "final": comp_res["final"],
                    },
                )
                games.append(cur_game)
        return games

    def import_season(self, season: int = None) -> List[Week]:
        return self.loop.run_until_complete(self.import_season_async(season))

    async def import_season_async(self, season: int = None) -> List[Week]:
        """
        Import games of a specific season and or week into the database
        """
        season_weeks = []

        if season is None:
            cur_year = date.today().year
        else:
            cur_year = season
        year_url = f"{self.api_base_url}/seasons/{cur_year}"
        async with httpx.AsyncClient(limits=self.httpx_limits) as client:
            year_res = await client.get(year_url)
            if year_res.status_code != 200:
                logger.warning(f"Could not get season {cur_year}: {year_res.reason}")
                return []
            yjson = year_res.json()
            year_dt_start = datetime.strptime(yjson["startDate"], self.dt_format_str)
            year_dt_end = datetime.strptime(yjson["endDate"], self.dt_format_str)
            cur_year = await self._get_or_create(
                Year,
                value=yjson["year"],
                defaults={
                    "start_timestamp": year_dt_start,
                    "end_timestamp": year_dt_end,
                },
            )
            pre_season_weeks = regular_season_weeks = post_season_weeks = 0
            for season in yjson["types"]["items"]:
                weeks_url = f"{year_url}/types/{season['type']}/weeks"
                weeks_res = await client.get(weeks_url)
                if weeks_res.status_code != 200:
                    logger.warning(
                        f"Could not query season type {SeasonType(season['type']).label}: {weeks_res.reason}"
                    )
                    continue
                weeks_json = weeks_res.json()
                if season["type"] == 1:
                    pre_season_weeks = len(weeks_json["items"])
                elif season["type"] == 2:
                    regular_season_weeks = len(weeks_json["items"])
                elif season["type"] == 3:
                    post_season_weeks = len(weeks_json["items"])
                for week in weeks_json["items"]:
                    week_res = await client.get(week["$ref"])
                    if week_res.status_code != 200:
                        logger.warning(f"Could not query week: {week_res.reason}")
                        continue
                    week_json = week_res.json()
                    week_dt_start = datetime.strptime(
                        week_json["startDate"], self.dt_format_str
                    )
                    week_dt_end = datetime.strptime(
                        week_json["endDate"], self.dt_format_str
                    )
                    real_week = week_json["number"]
                    if season["type"] == 2:
                        real_week += pre_season_weeks
                    elif season["type"] == 3:
                        real_week += pre_season_weeks + regular_season_weeks
                    elif season["type"] == 4:
                        real_week += (
                            pre_season_weeks + regular_season_weeks + post_season_weeks
                        )
                    cur_week = await self._get_or_create(
                        Week,
                        value=real_week,
                        year=cur_year,
                        defaults={
                            "start_timestamp": week_dt_start,
                            "end_timestamp": week_dt_end,
                        },
                    )
                    season_weeks.append(cur_week)
        return season_weeks

    async def _process_competitors(
        self, competitors: List[Dict[str, Any]], client: httpx.AsyncClient
    ) -> Optional[Dict[str, Any]]:
        res = {
            "home": {"score": None, "team_id": None},
            "visitor": {"score": None, "team_id": None},
            "final": False,
        }
        if competitors[0]["homeAway"] == "home":
            home_team = competitors[0]
            visitor_team = competitors[1]
        else:
            home_team = competitors[1]
            visitor_team = competitors[0]
        if int(home_team["id"]) < 1 or int(visitor_team["id"]) < 1:
            return None
        home_score = None
        visitor_score = None
        if "score" in home_team:
            home_score_res = await client.get(home_team["score"]["$ref"])
            home_score = home_score_res.json()
        if "score" in visitor_team:
            visitor_score_res = await client.get(visitor_team["score"]["$ref"])
            visitor_score = visitor_score_res.json()
        final = home_score and "winner" in home_score
        res["home"].update(
            {"team_id": home_team["id"], "score": home_score.get("value")}
        )
        res["visitor"].update(
            {"team_id": visitor_team["id"], "score": visitor_score.get("value")}
        )
        res.update({"final": final})
        return res
