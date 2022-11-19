# Understanding Plotting
### FalconAlliance has a plotting feature that makes on-the-go visualizing data easier.

<hr>

## Plotting Syntax
Syntax for plotting with FalconAlliance is fairly simple, with six different plot types coming readily available with FalconAlliance:
- Line plots (`Plotter.plot`)
- Scatter plots (`Plotter.scatter_plot`)
- Violin plots (`Plotter.violin_plot`)
- Bar plots (`Plotter.bar_plot`)
- Histograms (`Plotter.histogram`)
- Pie charts (`Plotter.pie_chart`)

Below is the syntax of a basic line plot with FalconAlliance and its output, with FalconAlliance styling the plot for you:

### Code
```py
from falcon_alliance import Plotter

# Creates a plotter instance, used for plotting data
plotter = Plotter()

# Plots a line chart and displays it
plotter.plot([1, 2, 3, 4], [5, 6, 7, 8], title="Basic Line Plot")
```

### Output
![Basic line plot](https://user-images.githubusercontent.com/82843611/202835156-43739924-347c-4e76-aba8-cacf7e6020f3.jpg)

## The `apply` Function

The `apply` function is a function introduced with plotting, which is useful for making your code more concise with common tasks you'd usually do during plotting. 

For example, say you'd want to get the score of a team's alliance for all the matches a team played during a year. With normal syntax, you'd have to do:
```py
import falcon_alliance

with falcon_alliance.ApiClient():
  team_matches = falcon_alliance.Team(4099).matches(2022)
  team_scores = []
  
  for match in team_matches:
    team_scores.append(match.alliance_of(team4099).score)
```

However, with the `apply` function, all you have to do is:
```py
import falcon_alliance

with falcon_alliance.ApiClient():
  team4099 = falcon_alliance.Team(4099)

  team_scores = list(falcon_alliance.apply(team4099.matches, year=[2022]).alliance_of(team4099).score)
```

What the apply function does is it takes the keyword arguments you pass in and calls the function you passed in (in this case `team4099.matches`) with every value for the corresponding keyword argument.

In this case, `team4099.matches` is only called once with the argument `2022`, since the keyword arugment `year` only has one value meaning that it will only be applied to the function passed in once.

This gives us a list containing every match the team played this year. This looks clunky at first, but the benefit comes in when we can call any method, retrieve any attribute, etc. from the result of the `apply` function as if it's an individual value.

Here, we're treating what `apply` returns as a `Match` object, resulting in concise syntax to apply a set of instructions to values, being uesful for plotting.

<sup> With AppliedFunction, what apply returns, there is also a `for_each` function whose documentation can be found [here](https://falcon-alliance.readthedocs.io/en/latest/reference/plotting.html#falcon_alliance.plotting.plotter.AppliedFunction.for_each). </sup>

## Documentation & Examples
**You can find our documentation for our plotting feature [here](https://falcon-alliance.readthedocs.io/en/latest/reference/plotting.html#falcon-alliance-plotting) and you can find an example [here](https://falcon-alliance.readthedocs.io/en/latest/reference/plotting.html#falcon-alliance-plotting).**
