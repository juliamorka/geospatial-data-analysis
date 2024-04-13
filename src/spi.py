import pandas as pd
from scipy import stats


def calculate_gamma_parameters(data: pd.Series) -> tuple:
    """
    Calculates the parameters of a gamma distribution fit for the given data.

    Parameters:
        data (pd.Series): The data to fit the gamma distribution to.

    Returns:
        tuple: A tuple containing the shape, location, and scale parameters of the gamma distribution.
    """
    params = stats.gamma.fit(data, loc=0)
    return params


def calculate_gamma_cumulative_probability(value: float, params: tuple) -> float:
    """
    Calculates the cumulative probability of a gamma distribution at a given value.

    Parameters:
        value (float): The value at which to calculate the cumulative probability.
        params (tuple): A tuple containing the shape, location,
            and scale parameters of the gamma distribution.

    Returns:
        float: The cumulative probability at the given value.
    """
    return stats.gamma.cdf(value, *params)


def get_spi(precipitation: pd.Series) -> list:
    """
    Calculates the Standardized Precipitation Index (SPI) for given precipitation data.

    Parameters:
        precipitation (pd.Series): A pandas Series containing precipitation data.

    Returns:
        list: A list containing SPI values for the input precipitation data.
    """
    gamma_params = calculate_gamma_parameters(precipitation)
    spi_values = [stats.norm.ppf(calculate_gamma_cumulative_probability(val, gamma_params)) for val in precipitation]
    return spi_values


def calculate_stations_spi(stations_rolling_precip_sum: pd.DataFrame, save_to_csv: bool, output_csv_path: str = "outputs/spi.csv") -> pd.DataFrame:
    """
    Calculate Standardized Precipitation Index (SPI) for each station.

    Parameters:
        stations_rolling_precip_sum (pd.DataFrame): A DataFrame containing rolling precipitation sum
           data for stations.
        save_to_csv (bool): Flag indicating whether to save the result to a CSV file.
        output_csv_path (str, optional): Path to save the CSV file. Default is "outputs/spi.csv".

    Returns:
        pd.DataFrame: A copy of the input DataFrame with an additional column "SPI"
           containing the Standardized Precipitation Index values.
    """
    stations_rolling_precip_sum_copy = stations_rolling_precip_sum.copy()
    spi = stations_rolling_precip_sum.groupby("station_code")["total_precip"].apply(get_spi).explode()
    stations_rolling_precip_sum_copy["SPI"] = spi.values
    if save_to_csv:
        stations_rolling_precip_sum_copy.to_csv(output_csv_path, index=False)
    return stations_rolling_precip_sum_copy

