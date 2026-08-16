"""pyflp_compat — heal pyflp 2.2.1 on Python >= 3.12 (the DEAD V16 rail).

pyflp.parse() resolves every event id via ``EventEnum(id)`` on the MEMBERLESS
base enum. Python 3.12's EnumMeta raises ``TypeError: <enum 'EventEnum'> has
no members`` BEFORE ``_missing_`` is consulted — so EVERY pyflp.parse dies on
3.12, whatever the file. Found 2026-07-24 while building flp_export's parse
court: the V16 FLP *import* bridge had been silently dead on this interpreter
the same way (no .flp in the repo ever probed it — the docs lie, the probes
don't).

ensure() rebinds the name ``EventEnum`` inside pyflp.__init__'s namespace to
a resolver that reproduces ``EventEnum._missing_`` verbatim: a populated
subclass member when one owns the id, else a pseudo-member minted on the base
class. parse()'s only use of that global is the id lookup, and everything it
does with the result (int compares vs WORD/DWORD/TEXT, ``in`` subclass,
``.value``, event construction) holds for both member kinds. No-op on
interpreters/releases where the plain call works.
"""
import pyflp
from pyflp._events import EventEnum


class _EventEnumProxy:
    """callable like ``EventEnum(id)``; every other attribute (parse also uses
    ``EventEnum.__subclasses__()``) forwards to the real enum class."""

    def __call__(self, value):
        for sc in EventEnum.__subclasses__():
            if value in sc:
                return sc(value)
        pm = EventEnum._value2member_map_.get(value)
        if pm is None:
            nm = int.__new__(EventEnum, value)
            nm._name_ = str(value)
            nm._value_ = value
            pm = EventEnum._value2member_map_.setdefault(value, nm)
        return pm

    def __getattr__(self, name):
        return getattr(EventEnum, name)


def ensure():
    try:
        EventEnum(199)                      # healthy interpreter: leave pyflp alone
    except TypeError:
        proxy = _EventEnumProxy()
        pyflp.EventEnum = proxy             # parse()'s id lookup
        pyflp._events.EventEnum = proxy     # EventBase.__init__'s id re-wrap
