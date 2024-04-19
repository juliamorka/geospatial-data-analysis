RAW_DATA_URL = (
    "https://danepubliczne.imgw.pl/"
    "data/dane_pomiarowo_obserwacyjne/"
    "dane_meteorologiczne/dobowe/opad/"
)
DEFAULT_START_YEAR = 1990
DEFAULT_END_YEAR = 2020
INPUT_DATA_PATH = "data/input/"
INTERIM_DATA_PATH = "data/interim/"
OUTPUTS_PATH = "outputs/"
HTTP_REQUEST_TIMEOUT = 10
VOIVODESHIPS_URL = (
    "https://raw.githubusercontent.com/"
    "ppatrzyk/polska-geojson/master/"
    "wojewodztwa/wojewodztwa-min.geojson"
)
COLS_TO_USE = list(range(6)) + [7]
COLUMNS_LABELS = [
    "station_code",
    "station_name",
    "year",
    "month",
    "day",
    "total_precip",
    "precip_type",
]
STATIONS_INFO_PATH = (
    "https://danepubliczne.imgw.pl/pl/datastore/"
    "getfiledown/Arch/Telemetria/Meteo/kody_stacji.csv"
)
STATIONS_INFO_COLUMNS_LABELS = ["station_code", "name", "lat", "lon"]
IMGW_PRECIP_DATA_READ_OPTIONS = {
    "sep": ",",
    "header": None,
    "usecols": COLS_TO_USE,
    "encoding": "cp1250",
}
STATIONS_INFO_PK = "station_code"
IMGW_STATIONS_INFO_READ_OPTIONS = {
    "sep": ";",
    "usecols": [1, 2, 4, 5],
    "encoding": "cp1250",
}
PERCENT_OF_DATES_THRESHOLD = int(30 * 365 * 40 / 100)
CHOSEN_VOIVODESHIP = "podlaskie"
DEFAULT_STATIONS_PLOT_PATH = "outputs/stations_map.png"
WINDOWS_TO_CALCULATE = [1, 3, 12]
DEFAULT_SPI_PRECIP_TS_PLOT_PATH = "outputs/spi_rolling_total_precip_ts.png"
NUMBER_OF_TASKS = 14
