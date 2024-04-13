import pandas as pd
from scipy import stats


def calculate_gamma_parameters(data: list) -> tuple:
    """
    Calculates the parameters of a gamma distribution fit for the given data.

    Parameters:
        data (list): The data to fit the gamma distribution to.

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


def calculate_SPI(precipitation: pd.Series) -> pd.DataFrame:
    """
    Calculates the Standardized Precipitation Index (SPI) for given precipitation data.

    Parameters:
        precipitation (pd.Series): A pandas Series containing precipitation data.

    Returns:
        pd.DataFrame: A DataFrame containing SPI values for the input precipitation data.
    """

    gamma_params = calculate_gamma_parameters(precipitation)
    SPI_values = [
        stats.norm.ppf(calculate_gamma_cumulative_probability(val, gamma_params))
        for val in precipitation
    ]

    return pd.DataFrame(SPI_values, index=precipitation.index)
