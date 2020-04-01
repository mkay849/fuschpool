from enum import Enum, IntEnum

from django.db import models


class CityChoices(models.TextChoices):
    ATLANTA = 'ATL', 'Atlanta'
    BALTIMORE = 'BAL', 'Baltimore'
    CHARLOTTE = 'CHA', 'Charlotte'
    CHICAGO = 'CHI', 'Chicago'
    CINCINNATI = 'CIN', 'Cincinnati'
    CLEVELAND = 'CLE', 'Cleveland'
    DENVER = 'DEN', 'Denver'
    DETROIT = 'DET', 'Detroit'
    EAST_RUTHERFORD = 'ER', 'East Rutherford'
    FOXBOROUGH = 'FOX', 'Foxborough'
    GLENDALE = 'GLE', 'Glendale'
    GREEN_BAY = 'GB', 'Green Bay'
    HOUSTON = 'HOU', 'Houston'
    INDIANAPOLIS = 'IND', 'Indianapolis'
    IRVING = 'IRV', 'Irving'
    JACKSONVILLE = 'JAX', 'Jacksonville'
    KANSAS_CITY = 'KC', 'Kansas City'
    LOS_ANGELES = 'LA', 'Los Angeles'
    LANDOVER = 'LAN', 'Landover'
    MIAMI = 'MIA', 'Miami'
    MINNEAPOLIS = 'MIN', 'Minneapolis'
    NASHVILLE = 'NAS', 'Nashville'
    NEW_ORLEANS = 'NO', 'New Orleans'
    OAKLAND = 'OAK', 'Oakland'
    ORCHARD_PARK = 'OP', 'Orchard Park'
    ORLANDO = 'ORL', 'Orlando'
    PHILADELPHIA = 'PHI', 'Philadelphia'
    PITTSBURGH = 'PIT', 'Pittsburgh'
    SAN_FRANCISCO = 'SF', 'San Francisco'
    SEATTLE = 'SEA', 'Seattle'
    TAMPA = 'TAM', 'Tampa'


class TeamChoices(models.TextChoices):
    AFC = 'AFC', 'American Football Conference'
    BEARS = 'CHI', 'Chicago Bears'
    BENGALS = 'CIN', 'Cincinnati Bengals'
    BILLS = 'BUF', 'Buffalo Bills'
    BRONCOS = 'DEN', 'Denver Broncos'
    BROWNS = 'CLE', 'Cleveland Browns'
    BUCCANEERS = 'TB', 'Tampa Bay Buccaneers'
    CARDINALS = 'ARI', 'Arizona Cardinals'
    CHARGERS = 'LAC', 'Los Angeles Chargers'
    CHIEFS = 'KC', 'Kansas City Chiefs'
    COLTS = 'IND', 'Indianapolis Colts'
    COWBOYS = 'DAL', 'Dallas Cowboys'
    DOLPHINS = 'MIA', 'Miami Dolphins'
    EAGLES = 'PHI', 'Philadelphia Eagles'
    FALCONS = 'ATL', 'Atlanta Falcons'
    FOURTYNINERS = 'SF', 'San Francisco 49ers'
    GIANTS = 'NYG', 'New York Giants'
    JAGUARS = 'JAX', 'Jacksonville Jaguars'
    JETS = 'NYJ', 'New York Jets'
    LIONS = 'DET', 'Detroit Lions'
    NFC = 'NFC', 'National Football Conference'
    PACKERS = 'GB', 'Green Bay Packers'
    PANTHERS = 'CAR', 'Carolina Panthers'
    PATRIOTS = 'NE', 'New England Patriots'
    RAIDERS = 'OAK', 'Oakland Raiders'
    RAMS = 'LA', 'Los Angeles Rams'
    RAVENS = 'BAL', 'Baltimore Ravens'
    REDSKINS = 'WAS', 'Washington Redskins'
    SAINTS = 'NO', 'New Orleans Saints'
    SEAHAWKS = 'SEA', 'Seattle Seahawks'
    STEELERS = 'PIT', 'Pittsburgh Steelers'
    TEXANS = 'HOU', 'Houston Texans'
    TITANS = 'TEN', 'Tennessee Titans'
    VIKINGS = 'MIN', 'Minnesota Vikings'


class StadiumChoices(models.TextChoices):
    AS = 'AS', 'Arrowhead Stadium'
    ATS = 'ATS', 'AT&T Stadium'
    BAS = 'BAS', 'Bank of America Stadium'
    CLF = 'CLF', 'CenturyLink Field'
    CWS = 'CWS', 'Camping World Stadium'
    DHSP = 'DHSP', 'Dignity Health Sports Park'
    EF = 'EF', 'Empower Field at Mile High'
    FEF = 'FEF', 'FedExField'
    FES = 'FES', 'FirstEnergy Stadium'
    FF = 'FF', 'Ford Field'
    GS = 'GS', 'Gillette Stadium'
    HF = 'HF', 'Heinz Field'
    HRS = 'HRS', 'Hard Rock Stadium'
    LAMC = 'LAMC', 'Los Angeles Memorial Coliseum'
    LF = 'LF', 'Lambeau Field'
    LFF = 'LFF', 'Lincoln Financial Field'
    LS = 'LS', 'Levi\'s Stadium'
    LOS = 'LOS', 'Lucas Oil Stadium'
    MBS = 'MBS', 'Mercedes-Benz Stadium'
    MBD = 'MBD', 'Mercedes-Benz Superdome'
    MLS = 'MLS', 'MetLife Stadium'
    MTBS = 'MTBS', 'M&T Bank Stadium'
    NEF = 'NEF', 'New Era Field'
    NRGS = 'NRGS', 'NRG Stadium'
    NS = 'NS', 'Nissan Stadium'
    PBS = 'PBS', 'Paul Brown Stadium'
    RCC = 'RCC', 'RingCentral Coliseum'
    RJS = 'RJS', 'Raymond James Stadium'
    SF = 'SF', 'Soldier Field'
    SFS = 'SFS', 'State Farm Stadium'
    TBF = 'TBF', 'TIAA Bank Field'
    USBS = 'USBS', 'U.S. Bank Stadium'


class PickChoices(models.IntegerChoices):
    TBP = 0
    HOME_TEAM = 1
    AWAY_TEAM = 2
    TIED_GAME = 3


class GamePhase(IntEnum):
    PREGAME = 1
    INGAME = 2
    HALFTIME = 3
    SUSPENDED = 4
    FINAL = 5
    FINAL_OVERTIME = 6


class SeasonType(Enum):
    """
    Season  Week_Order	Season_Type Week	Name
    2019	1	        HOF         1	    Hall Of Fame Week
    2019	2	        PRE         1	    Preseason Week 1
    2019	3	        PRE         2	    Preseason Week 2
    2019	4	        PRE         3	    Preseason Week 3
    2019	5	        PRE         4	    Preseason Week 4
    2019	6	        REG         1	    Week 1
    2019	7	        REG	        2	    Week 2
    2019	8	        REG	        3	    Week 3
    2019	9	        REG	        4   	Week 4
    2019	10	        REG	        5	    Week 5
    2019	11	        REG     	6	    Week 6
    2019	12	        REG	        7	    Week 7
    2019	13	        REG	        8   	Week 8
    2019	14	        REG	        9	    Week 9
    2019	15	        REG	        10  	Week 10
    2019	16	        REG	        11  	Week 11
    2019	17	        REG	        12	    Week 12
    2019	18	        REG	        13  	Week 13
    2019	19	        REG	        14	    Week 14
    2019	20	        REG	        15  	Week 15
    2019	21	        REG	        16  	Week 16
    2019	22	        REG     	17	    Week 17
    2019	23	        POST       	1	    Wild Card Weekend
    2019	24	        POST    	2   	Divisional Playoffs
    2019	25	        POST    	3	    Conference Championships
    2019	26	        PRO	        1	    Pro Bowl
    2019	27	        SB	        1	    Super Bowl
    """
    HALL_OF_FAME = 'HOF'
    PRE_SEASON = 'PRE'
    REGULAR_SEASON = 'REG'
    POST_SEASON = 'POST'
    PRO_BOWL = 'PRO'
    SUPER_BOWL = 'SB'
