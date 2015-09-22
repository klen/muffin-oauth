Muffin-OAuth
############

.. _description:

Muffin-OAuth -- Support OAUTH authentication in Muffin Framework.

.. _badges:

.. image:: http://img.shields.io/travis/klen/muffin-oauth.svg?style=flat-square
    :target: http://travis-ci.org/klen/muffin-oauth
    :alt: Build Status

.. image:: http://img.shields.io/pypi/v/muffin-oauth.svg?style=flat-square
    :target: https://pypi.python.org/pypi/muffin-oauth

.. image:: http://img.shields.io/pypi/dm/muffin-oauth.svg?style=flat-square
    :target: https://pypi.python.org/pypi/muffin-oauth

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 3.3

.. _installation:

Installation
=============

**Muffin-OAuth** should be installed using pip: ::

    pip install muffin-oauth

.. _usage:

Usage
=====

See example application.
Run with command: ::

    $ make run

And open http://fuf.me:5000 in your browser.

.. code:: python

    # OAuth2
    client = app.ps.oauth.client('github', access_token='...')
    resource = yield from client.request('GET', 'user')

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
=======

Licensed under a `MIT license`_.

If you wish to express your appreciation for the project, you are welcome to send
a postcard to: ::

    Kirill Klenov
    pos. Severny 8-3
    MO, Istra, 143500
    Russia

.. _links:

.. _klen: https://github.com/klen
.. _MIT license: http://opensource.org/licenses/MIT
