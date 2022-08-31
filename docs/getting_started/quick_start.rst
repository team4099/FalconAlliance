Quick Start
===========
Welcome to FalconAlliance! This section goes over everything you need to know to start using this library!

Prerequisites
-------------

**Python:** FalconAlliance supports Python 3.7+ and you should know a little bit of Python before diving into FalconAlliance! However, if you're confused about something, the documentation should explain it clearly.

**TBA API Key:** If you're planning to access TBA (The Blue Alliance) data from FalconAlliance, you'll need a TBA API key before proceeding to use this library. Visit https://thebluealliance.com/account to attain an API key from TBA.


Building Block of FalconAlliance Code
-------------------------------------

When accessing data from TBA (The Blue Alliance)'s API, all code regardless of whether or not you request to one of the base endpoints must include the following code to start off with:

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       # Your code goes here


The following code sets ``api_client`` to the instance you made of :ref:`falcon_alliance.ApiClient`, so now you can call the corresponding methods from TBA's API implemented into falcon_alliance.ApiClient.

.. warning::
   If you don't need to use the :ref:`falcon_alliance.ApiClient` instance and aren't sending requests to base endpoints (eg finding a team's matches, events, etc.), you can remove the ``as api_client`` portion of the code as it is redundant if you aren't calling methods upon the instance itself.

The purpose of the ``with`` block here is to close the client session used for sending requests to the TBA API. Without the ``with`` block, the session will be unclosed and errors might be propagated based on that, therefore it is required to use the ``with`` block.

.. note::
   If you haven't seen this syntax before, ``with`` blocks are known as context managers and are used to manage resources in some way. You may have seen these blocks in the context of opening and closing files, and they're generally used to ensure that resources are closed or managed with once the block of code is finished running.

   For more information about context managers, check out `this article <https://realpython.com › python-wit...Context Managers and Python's with Statement>`_.

.. _installation:

Common Tasks
------------

Accessing Specific Data
^^^^^^^^^^^^^^^^^^^^^^^

In the event that you want to access specific data, such as data pertaining to a team, event or district, you can use the corresponding classes' methods to do so.

For example, if you wanted to print a team's matches during a year, you could do:

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY):
       team_4099 = falcon_alliance.Team(4099)
       print(team_4099.matches(year=2022))

Or, if you wanted to print all matches that occurred during an event you could do:

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY):
       einsteins = falcon_alliance.Event("2022cmptx")
       print(einsteins.matches())

Or, if you wanted to print all teams in a district you could do:

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY):
       chesapeake_district = falcon_alliance.District("2022chs")
       print(chesapeake_district.teams())

These are just a few examples to show the hierarchy of FalconAlliance code and display how in order to access specific data, there are classes and corresponding methods within those classes to retrieve said data.

To find out more about the methods you could use to retrieve specific data, check out the following:
   - :ref:`falcon_alliance.District` (for retrieving district specific data)
   - :ref:`falcon_alliance.Event` (for retrieving event specific data)
   - :ref:`falcon_alliance.Team` (for retrieving team specific data)

Accessing General Data
^^^^^^^^^^^^^^^^^^^^^^

For accessing general data (i.e. all teams in FRC or all events in a certain year rather than a specific team or event), you can use :ref:`falcon_alliance.ApiClient`.

For example, if you want to print all the teams competing in the 2022 FRC season, you could do:

.. code-block:: python

   import falcon_alliance

   with falcon_alliance.ApiClient(api_key=YOUR_API_KEY) as api_client:
       print(api_client.teams(year=2022))

.. warning::
   The ``as api_client`` part is required for retrieving general data, since otherwise the :ref:`falcon_alliance.ApiClient` instance won't be set to a variable. However, you can change the name after ``as`` to whatever you want, for example ``as tba_api_client``.

Storing your API Key as an Environment Variable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Passing in your TBA API key to :ref:`falcon_alliance.ApiClient` every time gets redundant and you risk exposing your API key.
However, :ref:`falcon_alliance.ApiClient` allows you to define your API key as an environment variable so you don't need to pass it in.

To be able to do this, create a file called ``.env``, and write the following in it:

.. code-block:: none

   TBA_API_KEY=your_api_key_goes_here

You could also write:

.. code-block:: none

   API_KEY=your_api_key_goes_here

and it would be valid.

If you're worried that your API key will be leaked to Github when you push your code with this new file, don't worry! .env is not pushed to Github among with other files starting with . as they're considered "hidden".

.. attention::
   Make sure that the API key you put in as an environment variable is your TBA API key.

Accessing Attributes from Schemas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you call FalconAlliance methods, you'll probably have to deal with various classes in the return types of the methods you call.
These classes represent the schemas from the TBA API, which essentially is just a grouping of data that falls under a certain 'category'.

You can find the various schemas you'll be dealing within the return types and by itself in the ``API Reference`` section.

However, we can access attributes via either **dot syntax** which is accessing an attribute like ``class_instance.attribute_name``. For example, if we want to access a team's state with dot syntax we can do:

.. code-block:: python

   import falcon_alliance

   with ApiClient(api_key=YOUR_API_KEY) as api_client:
       team4099 = api_client.team("frc4099")
       print(team4099.state_prov)

Or you can access attributes via **dictionary syntax** which is accessing an attribute like ``class_instance["attribute_name"]``. For example, if we want to access a team's state with dictionary syntax we can do:

.. code-block:: python

   import falcon_alliance

   with ApiClient(api_key=YOUR_API_KEY) as api_client:
       team4099 = api_client.team("frc4099")
       print(team4099["state_prov"])

This is useful for when you have code that you are migrating to FalconAlliance from sending requests raw and want to use existing syntax.
