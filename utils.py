import numpy as np
import pandas as pd
from typing import Union

def break_text(text: str, max_length: int) -> str:
    """
    Breaks the text into two lines if the length of the text is greater than
    the max_length.

    Parameters:
    -----------
    text: str
        Text to be broken into two lines.
    max_length: int

    Returns:
    --------
    str
        Text broken into two lines.
    """
    if len(text) <= max_length:
        return text
    else:
        break_index = text.rfind(' ', 0, max_length)
        if break_index == -1:
            break_index = max_length

        line1 = text[:break_index].strip()
        line2 = text[break_index:].strip()

        return f"{line1}\n{line2}"

def round_to_nearest(value: int) -> int:
    """
    Rounds the value to the nearest integer.

    Parameters:
    -----------
    value: int
        Value to be rounded.

    Returns:
    --------
    int
        Rounded value.
    """
    if len(str(value)) == 1:
        return value
    elif len(str(value)) in range(2, 4):
        return round(value, -int(np.log10(value)))
    elif len(str(value)) in range(4, 6):
        return round(value, -(int(np.log10(value))-1))

def scale(
        value: int,
        min_value: float,
        max_value: float,
        n: int
    ) -> Union[float, np.ndarray, pd.Series]:
    """
    Scales the value between min_value and max_value. This is used to get the
    right value of the radius for the donut chart.

    Parameters:
    -----------
    value: int
        Value to be scaled.
    min_value: float
        Minimum value of the scale.
    max_value: float
        Maximum value of the scale.
    n: int
        Value of n for the nth root.

    Returns:
    --------
    Union[float, np.ndarray, pd.Series]
        Scaled value or array.
    """
    new_value = (nth_root(value * 1E2, n)) + (max_value + min_value)

    # Handles the case when the value is -inf
    if not isinstance(new_value, np.float64):
        new_value[new_value == -np.inf] = min_value

    return new_value

def nth_root(value: int, n: int) -> float:
    """
    Returns the nth root of the value.

    Parameters:
    -----------
    value: int
        Value to be scaled.
    n: int
        Value of n for the nth root.

    Returns:
    --------
    float
        Nth root of the value.
    """
    return np.power(value, 1/n)

def custom_scale(n: int, count_limit: int, num_points: int) -> np.ndarray:
    """
    Generates a custom scale for the donut chart using the nth root.

    Parameters:
    -----------
    n: int
        Value of n for the nth root.
    count_limit: int
        Maximum value of the scale.
    num_points: int
        Number of points to be generated.

    Returns:
    --------
    np.ndarray
        Generated scaled values.
    """
    # Generates a list of values between 0 and 1
    scaled_values = np.linspace(0, 1, num=num_points, endpoint=True)

    # Raises the values to the nth power
    scaled_values = np.power(scaled_values, n)

    # Scales the values to the count_limit
    scaled_values = scaled_values / np.max(scaled_values) * count_limit

    return scaled_values.astype(int)