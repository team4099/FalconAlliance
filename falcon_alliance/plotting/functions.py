import collections.abc
import typing
from itertools import zip_longest
from operator import attrgetter, itemgetter

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import BSpline, make_interp_spline


class AppliedFunction:
    """Represents an applied function, utilized for plotting."""

    def __init__(self, applied_result: list):
        self._applied_result = applied_result

    def __call__(self, *args, **kwargs):
        return AppliedFunction([*map(lambda function: function(*args, **kwargs), self._applied_result)])

    def __getitem__(self, item):
        return AppliedFunction([*map(itemgetter(item), self._applied_result)])

    def __getattr__(self, item):
        return AppliedFunction([*map(attrgetter(item), self._applied_result)])

    def __iter__(self):
        return iter(self._applied_result)

    def __str__(self):
        return f"AppliedFunction({self._applied_result})"


def apply(function: typing.Callable, **kwargs) -> AppliedFunction:
    """
    Applies keyword arguments to the function passed in, utilized for plotting.

    Args:
        function (Callable): A function to apply the kwargs to.
        **kwargs: The keyword argument name is the corresponding keyword argument for the function and the value is either a certain value that tells the function to keep that value constant or an iterable representing the different values to call the function with.

    Returns:
        AppliedFunction: A custom class containing a list of all the return values of the function based on the values that were applied to the function.
    """  # noqa
    kwargs_constant = {name: value for name, value in kwargs.items() if not isinstance(value, collections.abc.Iterable)}
    kwargs_iterables = {name: value for name, value in kwargs.items() if name not in kwargs_constant.keys()}

    formatted_kwargs = []

    for zipped in zip_longest(*kwargs_iterables.values()):
        formatted_kwargs.append({name: value for name, value in zip(kwargs_iterables.keys(), zipped)})

    return AppliedFunction([function(**kwargs_constant, **fmt_kwargs) for fmt_kwargs in formatted_kwargs])


def to_plot(
    x: collections.abc.Iterable[typing.Any],
    y: collections.abc.Iterable[typing.Any],
    title: str = "",
    smoothen: bool = False,
    color: str = "#FBBB00",
) -> typing.Tuple[plt.Figure, plt.Axes]:
    """
    Plots FalconAlliance data into a readable and understandable format.

    Args:
        x (Iterable[Any]): Data to plot on the x axis.
        y (Iterable[Any]): Data to plot on the y axis.
        title (str): The title for the plot.
        smoothen (bool): Determines whether or not to smoothen a line when plotting.
        color (str): Color to use when plotting. #FBBB00 by default.

    Returns:
        typing.Tuple[plt.Figure, plt.Axes]: Returns a plt.Figure object representing the figure created for the plot and a plt.Axes object representing the axes the data was plotted on.
    """  # noqa
    fig: plt.Figure = plt.figure(figsize=(12, 6))

    ax: plt.Axes = plt.subplot(1, 1, 1)
    ax.grid(True)

    # in case of the usage of AppliedFunction
    x, y = list(x), list(y)

    if smoothen:
        x_smooth = np.linspace(min(x), max(x), 200)
        spl = make_interp_spline(x, y, k=3)
        y_smooth = spl(x_smooth)
        x, y = x_smooth, y_smooth

    ax.plot(x, y, c=color, linewidth=2.5)
    ax.fill_between(x, y, alpha=0.25, color=color)
    ax.set_title(title, fontdict={"fontweight": "bold"}, loc="left")

    plt.show()

    return fig, ax
