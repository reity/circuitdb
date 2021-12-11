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

Examples
^^^^^^^^
This library provides a database that contains an (arbitrary but fixed) example of the smallest possible logical circuit (in terms of the number of unary and/or binary gates) for each possible logical function (from a finite set of functions). Logical functions are represented using tuples, as in the `logical <https://pypi.org/project/logical/>`_ library. In the example below, a circuit is retrieved for the function *f* (*x*, *y*, *z*) = *x* **and** *y* **and** *z* corresponding to the truth table ``(0, 0, 0, 0, 0, 0, 0, 1)``::

    >>> from circuitdb import circuitdb
    >>> circuitdb((0, 0, 0, 0, 0, 0, 0, 1))
    [((0, 1),), ((0, 1),), ((0, 1),), ((0, 0, 0, 1), 0, 1), ((0, 0, 0, 1), 2, 3), ((0, 1), 4)]

The representation of the circuit above consists of a list of unary and binary gates. Each gate is represented as a tuple. The first entry in each gate tuple is the logical function corresponding to that gate (represented using the `logical <https://pypi.org/project/logical/>`_ library). The remaining entries in the gate tuple are the indices of the input gates to that gate. For example, the entry ``((0, 0, 0, 1), 2, 3)`` represents a gate that is a conjunction of the gates at positions ``2`` and ``3`` in the overall list.

For any given logical function, it is possible to construct a corresponding circuit using a variety of gate sets. For each function, the database contains an example of a smallest circuit for each of a small collection of sets of unary and binary gates. In the remaining examples below, circuits for the function ``(0, 0, 1, 0, 0, 0, 0, 1)`` are retrieved. All gates in the circuit below are found in the set ``{logical.id_, logical.not_, logical.and_, logical.or_}``::

    >>> from logical import logical
    >>> circuitdb((0, 0, 1, 0, 0, 0, 0, 1), frozenset([logical.id_, logical.not_, logical.and_, logical.or_]))
    [((0, 1),), ((0, 1),), ((0, 1),), ((0, 0, 0, 1), 0, 2), ((0, 1, 1, 1), 0, 2), ((1, 0), 4), ((0, 1, 1, 1), 3, 5), ((0, 0, 0, 1), 1, 6), ((0, 1), 7)]

All gates in the circuit below are found in the set ``{logical.id_, logical.not_, logical.and_, logical.xor_}``::

    >>> circuitdb((0, 0, 1, 0, 0, 0, 0, 1), frozenset([logical.id_, logical.not_, logical.and_, logical.xor_]))
    [((0, 1),), ((0, 1),), ((0, 1),), ((1, 0), 0), ((0, 1, 1, 0), 2, 3), ((0, 0, 0, 1), 1, 4), ((0, 1), 5)]

By default (or if the set of all gates ``logical.every`` is specified), a smallest circuit that can be built using *any* combination of unary or binary gates is returned::

    >>> circuitdb((0, 0, 1, 0, 0, 0, 0, 1))
    [((0, 1),), ((0, 1),), ((0, 1),), ((0, 1, 1, 0), 0, 2), ((0, 0, 1, 0), 1, 3), ((0, 1), 4)]

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
