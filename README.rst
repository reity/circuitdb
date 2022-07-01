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

.. |coveralls| image:: https://coveralls.io/repos/github/reity/circuitdb/badge.svg?branch=main
   :target: https://coveralls.io/github/reity/circuitdb?branch=main
   :alt: Coveralls test coverage summary.

Installation and Usage
----------------------
This library is available as a `package on PyPI <https://pypi.org/project/circuitdb>`__::

    python -m pip install circuitdb

The library can be imported in the usual ways::

    import circuitdb
    from circuitdb import circuitdb

Examples
^^^^^^^^

.. |logical| replace:: ``logical``
.. _logical: https://logical.readthedocs.io/en/2.0.0/_source/logical.html#logical.logical.logical

.. |circuit| replace:: ``circuit``
.. _circuit: https://circuit.readthedocs.io/en/2.0.0/_source/circuit.html#circuit.circuit.circuit

.. |to_legible| replace:: ``to_legible``
.. _to_legible: https://circuit.readthedocs.io/en/2.0.0/_source/circuit.html#circuit.circuit.gates.to_legible

This library provides a database that contains an (arbitrary but fixed) example of the smallest possible logical circuit (in terms of the number of unary and/or binary gates) for each possible logical function (from a finite set of functions). This library represents logical functions using tuples, in accordance with the conventions of the |logical|_ class defined in the `logical <https://pypi.org/project/logical>`__ library. In the example below, a circuit is retrieved for the function *f* (*x*, *y*, *z*) = *x* **and** *y* **and** *z* corresponding to the truth table ``(0, 0, 0, 0, 0, 0, 0, 1)``. Retrieved circuits are represented as instances of the |circuit|_ class defined in the `circuit <https://pypi.org/project/circuit>`__ library; in the example below, the |to_legible|_ method of the circuit's gate list is used to retrieve a human-readable representation of the circuit::

    >>> from circuitdb import circuitdb
    >>> c = circuitdb((0, 0, 0, 0, 0, 0, 0, 1))
    >>> c.gate.to_legible() # Use method belonging to circuit object's gate list to inspect the circuit.
    (('id',), ('id',), ('id',), ('and', 0, 1), ('and', 2, 3), ('id', 4))

The human-readable representation of the circuit above consists of a list of unary and binary gates. Each gate is represented as a tuple. The first entry in each gate tuple is the name of the logical function corresponding to that gate. The remaining entries in the gate tuple are the indices of the input gates to that gate. For example, the entry ``('and', 2, 3)`` represents a gate that is a conjunction of the gates that have indices ``2`` and ``3`` in the overall list of gates. In accordance with the requirements of the |circuit|_ class, the three inputs are represented using identity gates that have no input indices.

For any given logical function, it is possible to construct a corresponding circuit using a variety of gate sets. For each function, the database contains an example of a smallest circuit for each of a small collection of sets of unary and binary gates. In the remaining examples below, circuits for the function ``(0, 0, 1, 0, 0, 0, 0, 1)`` are retrieved. All gates in the circuit retrieved below can be found in the set ``{logical.id_, logical.not_, logical.and_, logical.or_}``::

    >>> from logical import logical
    >>> c = circuitdb(
    ...     (0, 0, 1, 0, 0, 0, 0, 1),
    ...     frozenset([logical.id_, logical.not_, logical.and_, logical.or_])
    ... )
    >>> c.gate.to_legible()
    (('id',), ('id',), ('id',), ('and', 0, 2), ('or', 0, 2), ('not', 4), ('or', 3, 5), ('and', 1, 6), ('id', 7))

On the other hand, all gates in the circuit retrieved below can be found in the set ``{logical.id_, logical.not_, logical.and_, logical.xor_}``::

    >>> circuitdb(
    ...     (0, 0, 1, 0, 0, 0, 0, 1),
    ...     frozenset([logical.id_, logical.not_, logical.and_, logical.xor_])
    ... ).gate.to_legible()
    (('id',), ('id',), ('id',), ('not', 0), ('xor', 2, 3), ('and', 1, 4), ('id', 5))

.. |logical_every| replace:: ``logical.every``
.. _logical_every: https://logical.readthedocs.io/en/2.0.0/_source/logical.html#logical.logical.logical.every

By default (or if the set of all gates |logical_every|_ is specified), a smallest circuit that can be built using *any* combination of unary or binary gates is returned::

    >>> circuitdb((0, 0, 1, 0, 0, 0, 0, 1)).gate.to_legible()
    (('id',), ('id',), ('id',), ('xor', 0, 2), ('nimp', 1, 3), ('id', 4))

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__::

    python -m pip install .[docs,lint]

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__::

    python -m pip install .[docs]
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
All `doctest <https://docs.python.org/3/library/doctest.html>`__ unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details)::

    python -m pip install .[test]
    python -m pytest

Style conventions are enforced using `Pylint <https://pylint.pycqa.org>`__::

    python -m pip install .[lint]
    python -m pylint src/circuitdb

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/reity/circuitdb>`__ for this library.

Versioning
^^^^^^^^^^
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/circuitdb>`__ by a package maintainer. First, install the dependencies required for packaging and publishing::

    python -m pip install .[publish]

Ensure that the correct version number appears in ``pyproject.toml``, and that any links in this README document to the Read the Docs documentation of this package (or its dependencies) have appropriate version numbers. Also ensure that the Read the Docs project for this library has an `automation rule <https://docs.readthedocs.io/en/stable/automation-rules.html>`__ that activates and sets as the default all tagged versions. Create and push a tag for this version (replacing ``?.?.?`` with the version number)::

    git tag ?.?.?
    git push origin ?.?.?

Remove any old build/distribution files. Then, package the source into a distribution archive using the `wheel <https://pypi.org/project/wheel>`__ package::

    rm -rf build dist src/*.egg-info
    python -m build --sdist --wheel .

Finally, upload the package distribution archive to `PyPI <https://pypi.org>`__ using the `twine <https://pypi.org/project/twine>`__ package::

    python -m twine upload dist/*
