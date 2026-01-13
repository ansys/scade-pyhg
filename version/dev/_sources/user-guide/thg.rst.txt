Test harness generation
=======================

Settings
--------
Select the extension ``Python Target Test Environment`` in SCADE Test Settings,
``Harness Generation`` tab.

.. image:: /_static/harness.png

The settings page ``Python Target Test Environment`` is visible when the target
is selected:

.. image:: /_static/settings.png

* Module name (default name of the SCADE Suite model): Name of the Python proxy
  for the tested root operators.
* Runtime class (default ``ansys.scade.pyhg.lib.thgrt.Thgrt``): Class used by
  the generated scripts to assess the checks. The default class is delivered as
  an example, you can provide your own runtime, for example by deriving a new
  class from the default one.

Generation
----------
The tool generates one Python script per test record, named
``<procedure>_<record>.py``.
