.. _openid:

OpenID Authentication
======================

Overview
********

MarineMap instances require local accounts for all users. By default, logging on requires nothing more than
supplying the username and password for the local account. 

To use a single logon for mutliple marinemap instances, you can optionally turn
on `OpenID <http://openid.net>`_ consumer support. This allows you to use a third-party openid provider to authenticate. Once your
identity is verified by the OpenID Identity Provider, you can associate that openid with a local account.

When you have multiple marinemap accounts, all associated with a single openid, you get the 
benefits of app-to-app communication (TBD).


Decision Chart
***************
Rough overview of the login workflow:

.. image:: newauth2.png

Underlying Implementation
*************************
The `lingcod.openid` app is a fork of the `django-authopenid <http://bitbucket.org/benoitc/django-authsopenid/wiki/Home>`_ project. `django-authopenid` provided a good starting point for an openid consumer integrated with django auth, registration and legacy auth. Unfortunately it was no longer being maintained and required updates and customization - hence the fork.

Configuration
**************

You can use the `OPENID_ENABLED` setting to turn on/off the OpenID Login. The default is `False` or local 
"legacy" authentication system only. Setting to `True` enables openid features on the signin and user profile screens.

