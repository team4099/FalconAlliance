Examples
========

Creating a Dictionary Containing how many Teams each State has
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   states_to_teams = {}

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
      all_teams = api_client.teams(year=2022)

      for team in all_teams:
          states_to_teams[team.state_prov] = states_to_teams.get(team.state_prov, 0) + 1

Getting the Average Rookie Year of Teams in a District
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   states_to_teams = {}

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY):
      chs_district = falcon_alliance.District(2022, "chs")
      chs_teams = chs_district.teams()

      chs_rookie_years = [team.rookie_year for team in chs_teams]
      rookie_year_average = sum(chs_rookie_years) / len(chs_rookie_years)

Finding the Maximum Score from all the Matches a Team Played During a Year
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       team4099 = falcon_alliance.Team(4099)

       # Suggested way
       match_with_max_score = team4099.max(2022, metric=falcon_alliance.Metrics.MATCH_SCORE)
       maximum_score = match_with_max_score.alliance_of(team4099).score

       # Alternative way
       match_scores = []

       for match in team4099.matches(year=2022):
           match_scores.append(match.alliance_of(team4099).score)

       maximum_match_score = max(match_scores)

Plot of Distribution of Match Scores by Year for Team 4099
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       team4099 = falcon_alliance.Team(4099)
       plotter = falcon_alliance.Plotter()

       # data for x-axis
       years = range(2012, 2023)

       # data for y-axis, first gets match data from every year in a 2D list of match objects
       # the for_each method applies the function passed in to every element in the 2D list
       matches_by_year = falcon_alliance.apply(team4099.matches, year=years).for_each(lambda match: match.alliance_of(team4099).score)  # y data

       # if you don't want to edit the years in the x-axis
       plotter.violin_plot(data=matches_by_year, positions=years, title="Team 4099 Match Scores by Year")

       # if you do want to change the x-axis so that all years read properly
       fig, ax = plotter.violin_plot(data=matches_by_year, positions=years, title="Team 4099 Match Scores by Year", auto_plot=False)
       ax.set_xticklabels(years, rotation=90)

       plt.show()  # must have matplotlib.pyplot imported for the plot to show if you're not using auto-plot
