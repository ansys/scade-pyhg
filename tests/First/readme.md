# Basic integration test for Ansys SCADE Python THG
## Overview
The project `First` allows testing manually the Python custom target.

## Setup
* Register the package to SCADE as detailed in
  [Install in user mode](<https://pyhg.scade.docs.pyansys.com/version/dev/contributing.html#install-in-user-mode>).

## Test
* Open `Model/First.vsw` with SCADE.
* Activate the project `First.etp`.
* Select the configuration `KCG`.
* Launch the command `Project/Code Generator/Generate Node Main` and verify
  the code generation is successful.
* Select the configuration `Python`.
* Launch the command `Project/Code Generator/Build Node Root` and verify the
  build is successful.
* Activate the project `Test.etp`.
* Launch the command `Project/Test Tool/Generate Target Test Harness` and
  verify the generation is successful.
* Edit `Test\Run.bat` and update the path to an installation of Python 3.10
  according to your system.

  You can use the version of Python delivered with SCADE, available in:
  `<scade install dir>\contrib\Python310`
* Open a command line window and execute `Test\Run.bat`:

  ```cmd
  Test\Run.bat
  ```

  Verify it displays the following traces:

  ```
  ========================
  Operator: P::Main
  Procedure: P1

  test failed at step 2: v3=5.5 (expected 4.6)
  test failed at step 2: v=7 (expected 3)
  test failed at step 2: v1=3.0 (expected 7.02)
  test failed at step 2: v2=False (expected True)
  Test result: failed
  ========================
  ```

## Clean
You may uninstall the package once the manual tests are completed:

* Unregister the package from SCADE as detailed in
  [Uninstall](<https://python-wrapper.scade.docs.pyansys.com/version/dev/contributing.html#uninstall>).
