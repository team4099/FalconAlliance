Examples
========

The Basics
----------

.. note::
   To see all the methods that wrap around the base endpoints of TBA since they aren't all included here (e.g., retrieving information about a match/team/event), check out the documentation for :ref:`falcon_alliance.ApiClient`.

Retrieving Teams that Played in a Season
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       # equal to [Team(team_number=1, ...), ...] for every team that played in 2022
       all_teams = api_client.teams(year=2022)

Retrieving Any Team that Played Across Multiple Seasons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       # equal to [Team(team_number=1, ...), ...] and has any team that played in 2020, 2021, or 2022.
       all_teams = api_client.teams(year=range(2020, 2023))

.. warning::
   This code will be slower the larger your range object is, as it has to call numerous requests for each year alone as the result is paginated into teams of 500 each, therefore taking a while.

Retrieving Teams In Groups of 500
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       # equal to [Team(team_number=1, ...), ...] containing all teams with a team number between 1 and 500 that played in 2022.
       first_500_teams = api_client.teams(year=2022, page_num=1)
       # equal to [Team(team_number=500, ...), ...] and any other team that played in 2022 and has a team number between 500 and 1000.
       teams_from_500_to_1000 = api_client.teams(year=2022, page_num=2)
.. tip::
   To save time, if you're only looking for a certain group of teams, you can use the ``page_num`` parameter to retrieve the page number of the group of 500 teams that you want, as it only calls one request per season.

Retrieving the Keys of Teams that Played in a Season
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       # equal to ["frc1", ...] and the key of any other team that played in 2022.
       first_500_teams = api_client.teams(year=2022, keys=True)

Retrieving All Events in a Year
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       # equal to [Event(event_key="2022cmptx"), ...] containing Event objects for all events that occurred in 2022.
       all_events = api_client.events(year=2022)

Retrieving All Events Across Multiple Seasons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       # equal to [Event(event_key="2017chcmp"), Event(event_key="2018chcmp"), ...] containing Event objects
       # for all events in 2017 and 2018.
       all_events = api_client.events(year=range(2017, 2019))
Retrieving the Keys of the Events in a Season
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       # equal to ["2022cmptx", ...] and the key of any other event in 2022.
       first_500_teams = api_client.events(year=2022, keys=True)

Retrieve All Districts Present in a Season
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       # equal to [District(key="2022chs", ...), ...] containing all districts that were present in 2022.
       all_district = api_client.districts(year=2022)

Team-Specific Examples
----------------------
