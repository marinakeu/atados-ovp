==========
Open Volunteering Platform
==========

.. image:: https://img.shields.io/codeship/790495b0-551b-0135-2d95-0a077cc55315/master.svg?style=flat-square
  :target: https://app.codeship.com/projects/235535
.. image:: https://img.shields.io/codecov/c/github/OpenVolunteeringPlatform/django-open-volunteering-platform.svg?style=flat-square
  :target: https://codecov.io/gh/OpenVolunteeringPlatform/django-open-volunteering-platform
.. image:: https://img.shields.io/pypi/v/ovp-open-volunteering-platform.svg?style=flat-square
  :target: https://pypi.python.org/pypi/ovp-open-volunteering-platform/

django-open-volunteering-platform is a free and opensource django backend for developing volunteering platforms. It has users, organizations, projects and more baked in. 
We currently don't have a standard front-end for our API service, although it's something we're looking forward to building.


Getting Started
---------------
Prerequisites
""""""""""""""
We are always developing and testing against the latest python and django versions.

- Python 3.6
- Django 1.11
- Elasticsearch

Development
''''''''''''''
- SQLite

PostgreSQL
''''''''''''''
- PostgreSQL
- Haystack


Installing
""""""""""""""
1. Install django-ovp-core::

    pip install ovp-core

2. Add it to `INSTALLED_APPS` on `settings.py`

3. Add `vinaigrette` to `INSTALLED_APPS`


Forking
""""""""""""""
If you have your own OVP installation and want to fork this module
to implement custom features while still merging changes from upstream,
take a look at `django-git-submodules <https://github.com/leonardoarroyo/django-git-submodules>`_.

Testing
---------------
To test this module

::

  python ovp_core/tests/runtests.py

Contributing
---------------
Please read `CONTRIBUTING.md <https://github.com/OpenVolunteeringPlatform/django-ovp-users/blob/master/CONTRIBUTING.md>`_ for details on our code of conduct, and the process for submitting pull requests to us.

Versioning
---------------
We use `SemVer <http://semver.org/>`_ for versioning. For the versions available, see the `tags on this repository <https://github.com/OpenVolunteeringPlatform/django-ovp-users/tags>`_. 

License
---------------
This project is licensed under the GNU GPLv3 License see the `LICENSE.md <https://github.com/OpenVolunteeringPlatform/django-ovp-users/blob/master/LICENSE.md>`_ file for details

Thanks
---------------
A thanks for django-oscar for some great ideas for code structure.

