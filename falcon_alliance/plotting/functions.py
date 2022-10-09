import collections.abc
import typing

import matplotlib.pyplot as plt


def to_plot(
    x: collections.abc.Iterable[typing.Any], y: collections.abc.Iterable[typing.Any]
) -> typing.Tuple[plt.Figure, plt.Axes]:
    """
    Plots FalconAlliance data into a readable and understandable format.

    Args:
        x (Iterable[Any]): Data to plot on the x axis.
        y (Iterable[Any]): Data to plot on the y axis.

    Returns:
        typing.Tuple[plt.Figure, plt.Axes]: Returns a plt.Figure object representing the figure created for the plot and a plt.Axes object representing the axes the data was plotted on.
    """  # noqa
    fig: plt.Figure = plt.figure(figsize=(12, 6))
    ax: plt.Axes = plt.subplot(1, 1, 1)

    ax.grid(True)

    ax.plot(x, y)
    plt.show()

    return fig, ax
