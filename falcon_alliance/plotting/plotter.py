import collections.abc
import typing
from itertools import zip_longest
from operator import attrgetter, itemgetter

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import make_interp_spline


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

    def for_each(self, to_apply: typing.Callable) -> "AppliedFunction":
        """
        Applies a function to each element in a 2D list.

        Args:
            to_apply: A callable which is called with each element in a 2D list.

        Returns:
            AppliedFunction: An AppliedFunction instance containing the new applied list.
        """
        return AppliedFunction([[to_apply(element) for element in lst] for lst in self._applied_result])


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


class Plotter:
    """
    Helper class to make visualizing data easier.
    Uses matplotlib and abstracts the details, however the user can extend what is given and FalconAlliance's plotting features are easily extendable overall.

    Attributes:
        default_color (str): Represents the default color to use for plots. #FBBB00 by default.
        auto_plot (bool): Represents whether or not the axes should be plotted in the function itself.
    """  # noqa

    def __init__(self, auto_plot: bool = True, default_color: str = "#FBBB00"):
        self.auto_plot = auto_plot
        self.default_color = default_color

    def plot(
        self,
        x: collections.abc.Iterable[typing.Any],
        y: collections.abc.Iterable[typing.Any],
        fill_between: typing.Tuple[collections.abc.Iterable[typing.Any], collections.abc.Iterable[typing.Any]] = (),
        auto_plot: bool = None,
        title: str = "",
        smoothen: bool = False,
        color: str = "",
    ) -> typing.Tuple[plt.Figure, plt.Axes]:
        """
        Plots FalconAlliance data into a readable and understandable format.

        Args:
            x (Iterable[Any]): Data to plot on the x axis.
            y (Iterable[Any]): Data to plot on the y axis.
            fill_between(Tuple[Iterable[Any], Iterable[Any]]): Fills betweeen the first and second elements in the tuple on the plot.
            auto_plot (bool): Determines whether or not to plot the axes automatically in the function itself.
            title (str): The title for the plot.
            smoothen (bool): Determines whether or not to smoothen a line when plotting.
            color (str): Color to use when plotting. #FBBB00 by default.

        Returns:
            typing.Tuple[plt.Figure, plt.Axes]: Returns a plt.Figure object representing the figure created for the plot and a plt.Axes object representing the axes the data was plotted on.
        """  # noqa
        if not color:
            color = self.default_color

        if auto_plot is None:
            auto_plot = self.auto_plot

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

        if not fill_between:
            ax.fill_between(x, y, alpha=0.25, color=color)
        else:
            ax.fill_between(x, fill_between[0], fill_between[1], alpha=0.5, color=color)

        ax.set_title(title, fontdict={"fontweight": "bold"}, loc="left")

        if auto_plot:
            plt.show()

        return fig, ax

    def scatter(
        self,
        x: collections.abc.Iterable[typing.Any],
        y: collections.abc.Iterable[typing.Any],
        auto_plot: bool = None,
        title: str = "",
        color: str = "",
        secondary_color: str = "#262626",
        use_cmap: bool = True,
        marker_size: typing.Union[int, float] = plt.rcParams["lines.markersize"] ** 2,
    ) -> typing.Tuple[plt.Figure, plt.Axes]:
        """
        Plots the FalconAlliance data given into a scatter plot.

        Args:
            x (Iterable[Any]): Data to plot on the x axis.
            y (Iterable[Any]): Data to plot on the y axis.
            auto_plot (bool): Determines whether or not to plot the axes automatically in the function itself.
            title (str): The title for the plot.
            color (str): Color to use when plotting. #FBBB00 by default.
            secondary_color (str): Color to use for the higher points on the scatter plot. #262626 by default.
            use_cmap (bool): Boolean representing whether or not to use a colormap when plotting the scatter plot. True by default.
            marker_size (int, float): Number representing what to set the marker size (increases/decreases size of individual points).

        Returns:
            typing.Tuple[plt.Figure, plt.Axes]: Returns a plt.Figure object representing the figure created for the scatter plot and a plt.Axes object representing the axes the scatter plot is on.
        """  # noqa
        if not color:
            color = self.default_color

        if auto_plot is None:
            auto_plot = self.auto_plot

        fig: plt.Figure = plt.figure(figsize=(12, 6))

        ax: plt.Axes = plt.subplot(1, 1, 1)
        ax.grid(True, zorder=0)

        # in case of the usage of AppliedFunction
        x, y = list(x), list(y)

        if use_cmap:
            cmap = LinearSegmentedColormap.from_list("falconalliance_cmap", [color, secondary_color])

            try:
                ax.scatter(x, y, c=y, cmap=cmap, zorder=100, s=marker_size)
            except ValueError:
                ax.scatter(x, y, c=range(len(y)), cmap=cmap, zorder=100, s=marker_size)

        else:
            ax.scatter(x, y)

        ax.set_title(title, fontdict={"fontweight": "bold"}, loc="left")

        if auto_plot:
            plt.show()

        return fig, ax

    def violin_plot(
        self,
        data: collections.abc.Iterable[typing.List[typing.Any]],
        positions: collections.abc.Iterable[typing.Any],
        auto_plot: bool = None,
        title: str = "",
        color: str = "",
        secondary_color: str = "#262626",
        style_plot: bool = True,
    ) -> typing.Tuple[plt.Figure, plt.Axes]:
        """
        Plots the FalconAlliance data given into a violin plot.

        Args:
            data (Iterable[List[Any]): Array-like data for the violin plot itself.
            positions (Iterable[Any]): Data containing the positions for each 'violin' (the x-axis for vertical violin plots, basically).
            auto_plot (bool): Determines whether or not to plot the axes automatically in the function itself.
            title (str): The title for the plot.
            color (str): Color to use when plotting. #FBBB00 by default.
            secondary_color (str): Color to use for the edge color of the violins. #262626 by default.
            style_plot (bool): Boolean representing whether or not to use a custom style for the violin plot. Will default to matplotlib's standard style for a violin plot if False.

        Returns:
            typing.Tuple[plt.Figure, plt.Axes]: Returns a plt.Figure object representing the figure created for the scatter plot and a plt.Axes object representing the axes the scatter plot is on.
        """  # noqa
        if not color:
            color = self.default_color

        if auto_plot is None:
            auto_plot = self.auto_plot

        fig: plt.Figure = plt.figure(figsize=(12, 6))

        ax: plt.Axes = plt.subplot(1, 1, 1)
        ax.grid(True, zorder=0)

        # in case of the usage of AppliedFunction
        data, positions = list(data), list(positions)

        if style_plot:
            vp = ax.violinplot(data, positions, showextrema=False)

            for pc in vp["bodies"]:
                pc.set_facecolor(color)
                pc.set_edgecolor(secondary_color)
                pc.set_alpha(0.75)

            ax.vlines(positions, [*map(min, data)], [*map(max, data)], secondary_color)
        else:
            ax.violinplot(data, positions)

        ax.set_title(title, fontdict={"fontweight": "bold"}, loc="left")
        ax.set_xticks(positions)

        if auto_plot:
            plt.show()

        return fig, ax

    def bar_plot(
        self,
        x: collections.abc.Iterable[typing.Any],
        height: collections.abc.Iterable[typing.Any],
        auto_plot: bool = None,
        title: str = "",
        color: str = "",
        secondary_color: str = "#262626",
    ) -> typing.Tuple[plt.Figure, plt.Axes]:
        """
        Plots the FalconAlliance data given into a bar plot.

        Args:
            x (Iterable[Any]): Data containing the data for the x-axis.
            height (Iterable[Any]): Data containing the height of each "bar" on the bar chart (y-axis data).
            auto_plot (bool): Determines whether or not to plot the axes automatically in the function itself.
            title (str): The title for the plot.
            color (str): Color to use when plotting. #FBBB00 by default.
            secondary_color (str): Color to use for the edge color of the bar chart. #262626 by default.
        Returns:
            typing.Tuple[plt.Figure, plt.Axes]: Returns a plt.Figure object representing the figure created for the scatter plot and a plt.Axes object representing the axes the scatter plot is on.
        """  # noqa
        if not color:
            color = self.default_color

        if auto_plot is None:
            auto_plot = self.auto_plot

        fig: plt.Figure = plt.figure(figsize=(12, 6))

        ax: plt.Axes = plt.subplot(1, 1, 1)
        ax.grid(True, zorder=0)

        ax.bar(x, height, alpha=0.75, facecolor=color, edgecolor=secondary_color, zorder=100)
        ax.set_title(title, fontdict={"fontweight": "bold"}, loc="left")

        if auto_plot:
            plt.show()

        return fig, ax
