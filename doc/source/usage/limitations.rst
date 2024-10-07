Limitations
===========

* The name of the structuring folders are not considered to define the name of
  the Python scripts: Two different records of a procedure with the same name
  lead to the same target file.
* The sensors are not considered.
* The probes are not considered.
* The parameter ``filter`` of the ``on_check`` callback is ignored.
