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
