Getting Started
===============

Quick Start
-----------
Welcome to FalconAlliance! This section goes over everything you need to know to start using this library!

Prerequisites
^^^^^^^^^^^^^

**Python:** FalconAlliance supports Python 3.7+ and you should know a little bit of Python before diving into FalconAlliance! However, if you're confused about something, the documentation should explain it clearly.

**TBA API Key:** If you're planning to access TBA (The Blue Alliance) data from FalconAlliance, you'll need a TBA API key before proceeding to use this library. Visit https://thebluealliance.com/account to attain an API key from TBA.


Building Block of FalconAlliance Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When accessing data from TBA (The Blue Alliance)'s API, all code regardless of whether or not you request to one of the base endpoints must include the following code to start off with:

.. code-block:: python

   with ApiClient(api_key=YOUR_API_KEY) as api_client:
       # Your code goes here


The following code sets ``api_client`` to the instance you made of falcon_alliance.ApiClient, so now you can call the corresponding methods from TBA's API implemented into falcon_alliance.ApiClient.

.. warning::
   If you don't need to use the falcon_alliance.ApiClient instance and aren't sending requests to base endpoints (eg finding a team's matches, events, etc.), you can remove the ``as api_client`` portion of the code as it is redundant if you aren't calling methods upon the instance itself.

The purpose of the ``with`` block here is to close the client session used for sending requests to the TBA API. Without the ``with`` block, the session will be unclosed and errors might be propagated based on that, therefore it is required to use the ``with`` block.

.. note::
   If you haven't seen this syntax before, ``with`` blocks are known as context managers and are used to manage resources in some way. You may have seen these blocks in the context of opening and closing files, and they're generally used to ensure that resources are closed or managed with once the block of code is finished running.

   For more information about context managers, check out `this article <https://realpython.com › python-wit...Context Managers and Python's with Statement>`_.

.. _installation:

Installation
------------

FalconAlliance supports Python 3.7+, to install FalconAlliance use ``pip``.

.. code-block:: console

   (.venv) $ pip install falcon-alliance
