Muffin-OAuth
############

.. _description:

**Muffin-OAuth** -- Support OAuth authentication for Muffin_ Framework.

.. _badges:

.. image:: https://github.com/klen/muffin-oauth/workflows/tests/badge.svg
    :target: https://github.com/klen/muffin-oauth/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/muffin-oauth
    :target: https://pypi.org/project/muffin-oauth/
    :alt: PYPI Version

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 3.7

.. _installation:

Installation
=============

**Muffin-OAuth** should be installed using pip: ::

    pip install muffin-oauth

.. _usage:

Usage
=====

Get OAuth Access/Refresh Tokens
-------------------------------

See an example application in `example.py`.
Run the example with command: ::

    $ make example

And open http://localhost:5000 in your browser.

Load resouces with access tokens
--------------------------------

.. code:: python

    # OAuth2
    client = oauth.client('github', access_token='...')
    resource = await client.request('GET', 'user')

.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/muffin-oauth/issues

.. _contributing:

Contributing
============

Development of Muffin-OAuth happens at: https://github.com/klen/muffin-oauth


Contributors
=============

* klen_ (Kirill Klenov)

.. _license:

License
========

Licensed under a `MIT license`_.
.. _links:

.. _Muffin: https://github.com/klen/muffin
.. _klen: https://github.com/klen
.. _MIT license: http://opensource.org/licenses/MIT
