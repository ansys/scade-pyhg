Runtime
=======

The generated scenarios require a runtime for assessing the checks.
Indeed, this requires an internal state, at least for caching properties like
tolerances, aliases, or most important, the sustainability of the checks.
Otherwise, the python script would become too verbose.

It is possible to tune the messages, execution reports, etc. by specifying
your own runtime class.
