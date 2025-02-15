Getting started
===============
To use Ansys SCADE THG for Python, you must have a valid license for Ansys SCADE.

For information on getting a licensed copy, see the
`Ansys SCADE Suite <https://www.ansys.com/products/embedded-software/ansys-scade-suite>`_
page on the Ansys website.

Requirements
------------
The ``ansys-scade-pyhg`` package supports only the versions of Python delivered with
Ansys SCADE, starting from 2024 R2:

* 2024 R2 and later: Python 3.10

Install in user mode
--------------------
The following steps are for installing Ansys SCADE THG for Python in user mode. If you want to
contribute to Ansys SCADE THG for Python, see :ref:`contribute_scade_pyhg` for the steps
for installing in developer mode.

#. Before installing Ansys SCADE THG for Python in user mode, run this command to ensure that
   you have the latest version of `pip`_:

   .. code:: bash

      python -m pip install -U pip

#. Install Ansys SCADE THG for Python with this command:

   .. code:: bash

       python -m pip install --user ansys-scade-pyhg

#. For Ansys SCADE 2024 R2, complete the installation by copying
   ``ansys/scade/pyhg/lib/qtethgpyhg66.py`` to the ``SCADE/scripts/Thg`` directory
   of the SCADE 2024 R2 installation.

   For example: ``C:\Program Files\ANSYS Inc\v242\SCADE\SCADE\scripts\Thg``.

   .. Note::

      Create the directory ``Thg`` if it does not exist.

.. LINKS AND REFERENCES
.. _pip: https://pypi.org/project/pip/
