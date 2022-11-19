# FalconAlliance
### A Pythonic wrapper around TBA and other FRC data sources at your convenience.

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
(.venv) $ python3.(your version) -m pip install falcon-alliance
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
The structure of FalconAlliance code follows a hierarchy with each schema being its own class with its own methods.

For example, all TBA endpoints stemming off from a team key (eg `team/{team_key}/events`) is under the `Team` class (in this case the corresponding method is `Team.events`).

Using this structure, you can find the method you need by looking at the base endpoint (in this case `team`, meaning you want to use the `Team` class method, then you can look at the rest of the method to figure out what method you want specifically. 

If it is a more generic base endpoint (eg `teams`), you'll likely find it in the `ApiClient` class. You can also look at the [documentation](https://falcon-alliance.readthedocs.io/en/latest) to find the method you want.

## Documentation
**To read more of our documentation, check out [this link](https://falcon-alliance.readthedocs.io/en/latest).**
