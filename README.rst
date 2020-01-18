pinku
=====

``pinku`` is a `Pinboard <https://pinboard.in>`_-to-`buku <https://github.com/jarun/buku>`_ importation utility.

``pinku`` is **not** (at least at this time) a syncing utility and works in only one direction: to import bookmarks *from* Pinboard *into* buku. If the URL already exists in buku, the entry is skipped over.

Installation
------------
``pip install pinku``

Usage
-----
Ensure that you have set the ``PINBOARD_API_KEY`` environment variable to your Pinboard API token. You can find your API token `here <https://pinboard.in/settings/password>`_.

``pinku`` takes command-line arguments that serve as filters for searching through Pinboard bookmarks. ``pinku`` will then add the results to your buku database.

Pinku supports all of the filter arguments for the Pinboard API ``/all`` endpoint. Please visit `Pinboard's API documentation <https://pinboard.in/api>`_ to read the details.

**Please note that Pinboard limits API calls to the /all endpoint to once every five minutes**

Examples
--------

Add *all* Pinboard bookmarks to buku:

.. code-block::

    pinku

Add your 10 most recent Pinboard bookmarks to buku:

.. code-block::

    pinku -r 10

Add all Pinboard bookmarks tagged ``web-dev`` and ``programming`` (max 3 tags per Pinboard API) to buku:

.. code-block::

    pinku -t web-dev, programming

Add the first 3 Pinboard bookmarks tagged ``web-dev`` to buku:

.. code-block::

    pinku -t web-dev -r 3

Add the first 3 Pinboard bookmarks tagged ``history`` that also have a Pinboard "to read" status:

.. code-block::

    pinku -t history -r 3 --toread

Add all Pinboard bookmarks since September 1, 2017 to buku:

.. code-block::

    pinku --fromdt 2017-09-01

Add all bookmarks that were added to Pinboard between 7/1/2017 and 9/1/2017 to buku:

.. code-block::

    pinku --fromdt 2017-09-01 --todt 2017-09-01

