Example
=======

This sections show the result of the harness generation for a simple
SCADE Test SSS scenario: This scenario address the operator
``Common::MinMaxU8``, defined in the ``Common.etp`` SCADE project.

* Input scenario

  .. code:: tcl

     SSM::alias x Common::MinMaxU8/x
     SSM::alias y Common::MinMaxU8/y
     SSM::alias min Common::MinMaxU8/min
     SSM::alias max Common::MinMaxU8/max
     # input sequence for MinMaxU8
     # step 1
     SSM::set x 0
     SSM::set y 0
     SSM::check min 0
     SSM::check max 0
     SSM::cycle

* Python script

  Reminder: ``common.py`` and its class ``MinMax8`` are produced by
  Ansys SCADE Python Wrapper.

  .. code::

     from common import MinMaxU8
     from ansys.scade.pyhg.lib.thgrt import Thgrt as Thgrt

     # instance of root operator
     root = MinMaxU8()

     # instance of Thgrt
     thgrt = Thgrt(root, 'Common::MinMaxU8', 'MinMaxU8')

     # input sequence for MinMaxU8
     # step 1
     root.x = 0
     root.y = 0
     thgrt.check("min", 0)
     thgrt.check("max", 0)
     thgrt.cycle(1)
