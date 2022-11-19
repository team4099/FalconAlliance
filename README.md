# FalconAlliance
### A Pythonic wrapper around TBA and other FRC data sources at your convenience. You can find the documentation [here](https://falcon-alliance.readthedocs.io/en/latest)

<hr>

## Installation

To install `falcon-alliance`, run the following in your console:
```console
(.venv) $ pip install falcon-alliance
```

If the following doesn't work, and you get an error regarding pip not being a command, try one of the following below:
```console
(.venv) $ python -m pip install falcon-alliance
```
```console
(.venv) $ python3 -m pip install falcon-alliance
```
```console
(.venv) $ python3.<your_version> -m pip install falcon-alliance
```

## Setup

Once you have `falcon-alliance` installed, a basic skeleton of FalconAlliance code is 
```py
import falcon_alliance

with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
  # Code using the API client here
```
<sup> For more information about the building block of FalconAlliance code, check out [this section](https://falcon-alliance.readthedocs.io/en/latest/getting_started/quick_start.html#building-block-of-falconalliance-code) of our documentation. </sup>

Do note that passing in the API key is not required if the API key is already stored in your `.env` file under the name `TBA_API_KEY` or `API_KEY`. 

As for the code within the context manager (the with statement), below is an example of retrieving a list of all the teams that played in 2022 via FalconAlliance:
```py
import falcon_alliance

with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
  all_teams = api_client.teams(year=2022)
```
<sup> For more examples with the building block, check out the [Common Tasks](https://falcon-alliance.readthedocs.io/en/latest/getting_started/quick_start.html#common-tasks) section and the [Examples](https://falcon-alliance.readthedocs.io/en/latest/getting_started/examples.html) section.

## Structure
The structure of FalconAlliance code follows a hierarchy, with `ApiClient` being at the top, containing agnostic methods like getting a list of all teams from a certain year, a list of all events from a certain year, etc. 

In the middle of the hierarchy are schemas with methods in them, containing endpoints depending on a certain team/event/district. `Team`, `Event`, and `District`, which wrap around endpoints that depend on a certain key (team key/event key/district key). An example of a method for each of the following classes are:
  - `Team.events`, which wraps around the `/team/{team_key}/events` endpoint.
  - `Event.teams`, which wraps around the `/event/{event_key}/teams` endpoint.
  - `District.rankings`, which wraps around the `/district/{district_key}/rankings` endpoint.

At the bottom of the hierarchy are schemas which primarily act as data-classes, and are there as a means of communicating data in a readable format rather than having functionality. The classes at the bottom of the hierarchy are: `Award`, `EventTeamStatus`, `Match`, `Media`, and `Robot`.

## Examples
### [Creating a Dictionary Containing how many Teams each State has](https://falcon-alliance.readthedocs.io/en/latest/getting_started/examples.html#creating-a-dictionary-containing-how-many-teams-each-state-has)
```py
import falcon_alliance

states_to_teams = {}

with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
   all_teams = api_client.teams(year=2022)

   for team in all_teams:
       states_to_teams[team.state_prov] = states_to_teams.get(team.state_prov, 0) + 1
```
### [Getting the Average Rookie Year of Teams in a District](https://falcon-alliance.readthedocs.io/en/latest/getting_started/examples.html#getting-the-average-rookie-year-of-teams-in-a-district)
```py
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
```
### [Finding the Maximum Score from all the Matches a Team Played During a Year](https://falcon-alliance.readthedocs.io/en/latest/getting_started/examples.html#finding-the-maximum-score-from-all-the-matches-a-team-played-during-a-year)
```py
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
```

**More examples are listed on the documentation [here](https://falcon-alliance.readthedocs.io/en/latest/getting_started/examples.html#examples).**
