=========
circuitdb
=========

Data set of optimal circuits for Boolean functions that have low arity.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/circuitdb.svg
   :target: https://badge.fury.io/py/circuitdb
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/circuitdb/badge/?version=latest
   :target: https://circuitdb.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/reity/circuitdb/workflows/lint-test-cover-docs/badge.svg
   :target: https://github.com/reity/circuitdb/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/reity/circuitdb/badge.svg?branch=master
   :target: https://coveralls.io/github/reity/circuitdb?branch=master

Package Installation and Usage
------------------------------
The package is available on PyPI::

    python -m pip install circuitdb

The library can be imported in the usual ways::

    import circuitdb
    from circuitdb import circuitdb

Documentation
-------------
.. include:: toc.rst

The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org/>`_::

    cd docs
    python -m pip install -r requirements.txt
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. ../setup.py && make html

Testing and Conventions
-----------------------
All unit tests are executed and their coverage is measured when using `nose <https://nose.readthedocs.io/>`_ (see ``setup.cfg`` for configution details)::

    nosetests

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`_::

    python circuitdb/circuitdb.py -v

Style conventions are enforced using `Pylint <https://www.pylint.org/>`_::

    pylint circuitdb

Contributions
-------------
In order to contribute to the source code, open an issue or submit a pull request on the GitHub page for this library.

Versioning
----------
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`_.
