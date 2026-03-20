.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`2.3.0 <https://github.com/ansys/scade-pyhg/releases/tag/v2.3.0>`_ - March 20, 2026
===================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Maintenance missing or outdated check-vulnerabilities and check-actions-security ansys actions
          - `#39 <https://github.com/ansys/scade-pyhg/pull/39>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - build: bump pytest from 8.0.2 to 8.4.1
          - `#22 <https://github.com/ansys/scade-pyhg/pull/22>`_

        * - build: bump twine from 5.1.1 to 6.1.0
          - `#23 <https://github.com/ansys/scade-pyhg/pull/23>`_

        * - Bump the dependencies group across 1 directory with 8 updates
          - `#41 <https://github.com/ansys/scade-pyhg/pull/41>`_

        * - Bump sphinxcontrib-httpdomain from 1.8.1 to 2.0.0 in the dependencies group
          - `#43 <https://github.com/ansys/scade-pyhg/pull/43>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix: enhance robustness
          - `#18 <https://github.com/ansys/scade-pyhg/pull/18>`_

        * - Ci: bump the actions group with 2 updates
          - `#19 <https://github.com/ansys/scade-pyhg/pull/19>`_, `#29 <https://github.com/ansys/scade-pyhg/pull/29>`_

        * - Build: bump the docs-deps group with 5 updates
          - `#20 <https://github.com/ansys/scade-pyhg/pull/20>`_

        * - Build: bump pytest-cov from 5.0.0 to 6.2.1
          - `#21 <https://github.com/ansys/scade-pyhg/pull/21>`_

        * - Ci: group the dependencies to minimize the number of prs
          - `#24 <https://github.com/ansys/scade-pyhg/pull/24>`_

        * - Docs: update ``contributors.md`` with the latest contributors
          - `#25 <https://github.com/ansys/scade-pyhg/pull/25>`_

        * - Build(deps): bump the dependencies group with 2 updates
          - `#28 <https://github.com/ansys/scade-pyhg/pull/28>`_

        * - Chore: Update missing or outdated files
          - `#35 <https://github.com/ansys/scade-pyhg/pull/35>`_

        * - Ci: bump the actions group across 1 directory with 5 updates
          - `#36 <https://github.com/ansys/scade-pyhg/pull/36>`_

        * - Chore: Update license headers
          - `#38 <https://github.com/ansys/scade-pyhg/pull/38>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - chore: update CHANGELOG for v2.2.0
          - `#16 <https://github.com/ansys/scade-pyhg/pull/16>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - ci: Fix release steps
          - `#17 <https://github.com/ansys/scade-pyhg/pull/17>`_

        * - Bump actions/download-artifact from 6.0.0 to 7.0.0 in the actions group
          - `#40 <https://github.com/ansys/scade-pyhg/pull/40>`_

        * - Bump Python and SCADE versions
          - `#44 <https://github.com/ansys/scade-pyhg/pull/44>`_


`2.2.0 <https://github.com/ansys/scade-pyhg/releases/tag/v2.2.0>`_ - 2025-02-11
===============================================================================

Added
^^^^^

- feat: Support NaN and Inf values `#13 <https://github.com/ansys/scade-pyhg/pull/13>`_
- feat: Support relative tolerances `#15 <https://github.com/ansys/scade-pyhg/pull/15>`_


Documentation
^^^^^^^^^^^^^

- chore: update CHANGELOG for v2.1.0 `#11 <https://github.com/ansys/scade-pyhg/pull/11>`_

`2.1.0 <https://github.com/ansys/scade-pyhg/releases/tag/v2.1.0>`_ - 2025-01-22
===============================================================================

Fixed
^^^^^

- fix: `tox` env variable for test coverage `#7 <https://github.com/ansys/scade-pyhg/pull/7>`_
- fix: trusted publisher permissions `#10 <https://github.com/ansys/scade-pyhg/pull/10>`_


Documentation
^^^^^^^^^^^^^

- chore: update CHANGELOG for v2.0.0 `#5 <https://github.com/ansys/scade-pyhg/pull/5>`_
- feat: Technical review `#6 <https://github.com/ansys/scade-pyhg/pull/6>`_
- docs: review of user documentation `#8 <https://github.com/ansys/scade-pyhg/pull/8>`_


Maintenance
^^^^^^^^^^^

- ci: Remove the dependencies to pr-name `#9 <https://github.com/ansys/scade-pyhg/pull/9>`_

`2.0.0 <https://github.com/ansys/scade-pyhg/releases/tag/v2.0.0>`_ - 2024-10-10
===============================================================================

Added
^^^^^

- feat: Migrate the original repository to GitHub `#1 <https://github.com/ansys/scade-pyhg/pull/1>`_
- feat: Add sensors and projections `#3 <https://github.com/ansys/scade-pyhg/pull/3>`_


Fixed
^^^^^

- fix: Add support for SCADE 2024 R2 `#4 <https://github.com/ansys/scade-pyhg/pull/4>`_


Test
^^^^

- refactor: Simplify the tests and add a new one for main `#2 <https://github.com/ansys/scade-pyhg/pull/2>`_

.. vale on
