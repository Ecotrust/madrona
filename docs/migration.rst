.. _migration:

Migrations for Database Schema Changes
============================================

As you develop django models, it quickly becomes apparent that syncing changes between your models.py and your database schema is not sufficiently handled by ``manage.py syncdb``. 

Using ``south``, you can create migrations - python code which describes how to alter the database schema and contents to keep up with changes in your model definitions.

For full details, please check out the `MarineMap Migration Wiki Page <http://code.google.com/p/marinemap/wiki/Migration>`_ or the `south documentation <http://south.aeracode.org/docs/about.html>`_.
