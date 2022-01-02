from django.db import models


class CityChoices(models.TextChoices):
    ATLANTA = "ATL", "Atlanta"
    BALTIMORE = "BAL", "Baltimore"
    CHARLOTTE = "CHA", "Charlotte"
    CHICAGO = "CHI", "Chicago"
    CINCINNATI = "CIN", "Cincinnati"
    CLEVELAND = "CLE", "Cleveland"
    DENVER = "DEN", "Denver"
    DETROIT = "DET", "Detroit"
    EAST_RUTHERFORD = "ER", "East Rutherford"
    FOXBOROUGH = "FOX", "Foxborough"
    GLENDALE = "GLE", "Glendale"
    GREEN_BAY = "GB", "Green Bay"
    HOUSTON = "HOU", "Houston"
    INDIANAPOLIS = "IND", "Indianapolis"
    IRVING = "IRV", "Irving"
    JACKSONVILLE = "JAX", "Jacksonville"
    KANSAS_CITY = "KC", "Kansas City"
    LOS_ANGELES = "LA", "Los Angeles"
    LANDOVER = "LAN", "Landover"
    MIAMI = "MIA", "Miami"
    MINNEAPOLIS = "MIN", "Minneapolis"
    NASHVILLE = "NAS", "Nashville"
    NEW_ORLEANS = "NO", "New Orleans"
    OAKLAND = "OAK", "Oakland"
    ORCHARD_PARK = "OP", "Orchard Park"
    ORLANDO = "ORL", "Orlando"
    PHILADELPHIA = "PHI", "Philadelphia"
    PITTSBURGH = "PIT", "Pittsburgh"
    SAN_FRANCISCO = "SF", "San Francisco"
    SEATTLE = "SEA", "Seattle"
    TAMPA = "TAM", "Tampa"


class GamePhase(models.IntegerChoices):
    PREGAME = 1
    INGAME = 2
    HALFTIME = 3
    SUSPENDED = 4
    FINAL = 5
    FINAL_OVERTIME = 6


class SeasonType(models.IntegerChoices):
    PRE = 1, "Preseason"
    REGULAR = 2, "Regular Season"
    POST = 3, "Postseason"
    OFF = 4, "Off Season"


class StadiumChoices(models.TextChoices):
    AS = "AS", "Arrowhead Stadium"
    ATS = "ATS", "AT&T Stadium"
    BAS = "BAS", "Bank of America Stadium"
    CLF = "CLF", "CenturyLink Field"
    CWS = "CWS", "Camping World Stadium"
    DHSP = "DHSP", "Dignity Health Sports Park"
    EF = "EF", "Empower Field at Mile High"
    FEF = "FEF", "FedExField"
    FES = "FES", "FirstEnergy Stadium"
    FF = "FF", "Ford Field"
    GS = "GS", "Gillette Stadium"
    HF = "HF", "Heinz Field"
    HRS = "HRS", "Hard Rock Stadium"
    LAMC = "LAMC", "Los Angeles Memorial Coliseum"
    LF = "LF", "Lambeau Field"
    LFF = "LFF", "Lincoln Financial Field"
    LS = "LS", "Levi's Stadium"
    LOS = "LOS", "Lucas Oil Stadium"
    MBS = "MBS", "Mercedes-Benz Stadium"
    MBD = "MBD", "Mercedes-Benz Superdome"
    MLS = "MLS", "MetLife Stadium"
    MTBS = "MTBS", "M&T Bank Stadium"
    NEF = "NEF", "New Era Field"
    NRGS = "NRGS", "NRG Stadium"
    NS = "NS", "Nissan Stadium"
    PBS = "PBS", "Paul Brown Stadium"
    RCC = "RCC", "RingCentral Coliseum"
    RJS = "RJS", "Raymond James Stadium"
    SF = "SF", "Soldier Field"
    SFS = "SFS", "State Farm Stadium"
    TBF = "TBF", "TIAA Bank Field"
    USBS = "USBS", "U.S. Bank Stadium"


class TeamChoices(models.IntegerChoices):
    ATL = 1, "Atlanta Falcons"
    BUF = 2, "Buffalo Bills"
    CHI = 3, "Chicago Bears"
    CIN = 4, "Cincinnati Bengals"
    CLE = 5, "Cleveland Browns"
    DAL = 6, "Dallas Cowboys"
    DEN = 7, "Denver Broncos"
    DET = 8, "Detroit Lions"
    GB = 9, "Green Bay Packers"
    TEN = 10, "Tennessee Titans"
    IND = 11, "Indianapolis Colts"
    KC = 12, "Kansas City Chiefs"
    LV = 13, "Las Vegas Raiders"
    LAR = 14, "Los Angeles Rams"
    MIA = 15, "Miami Dolphins"
    MIN = 16, "Minnesota Vikings"
    NE = 17, "New England Patriots"
    NO = 18, "New Orleans Saints"
    NYG = 19, "New York Giants"
    NYJ = 20, "New York Jets"
    PHI = 21, "Philadelphia Eagles"
    ARI = 22, "Arizona Cardinals"
    PIT = 23, "Pittsburgh Steelers"
    LAC = 24, "Los Angeles Chargers"
    SF = 25, "San Francisco 49ers"
    SEA = 26, "Seattle Seahawks"
    TB = 27, "Tampa Bay Buccaneers"
    WSH = 28, "Washington"
    CAR = 29, "Carolina Panthers"
    JAX = 30, "Jacksonville Jaguars"
    AFC = 31, "AFC"
    NFC = 32, "NFC"
    BAL = 33, "Baltimore Ravens"
    HOU = 34, "Houston Texans"


class PickChoices(models.IntegerChoices):
    TBP = 0
    HOME_TEAM = 1
    VISITOR_TEAM = 2
    TIED_GAME = 3
