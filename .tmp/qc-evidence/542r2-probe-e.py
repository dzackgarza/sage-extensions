"""#542 round 2: the Picard class's representative and the group law."""
from sage_extensions.all import *  # noqa


def show(label, f):
    try:
        print(f"{label}: {f()!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")


ring = QQ["x"]
x = ring("x")
scheme = ring.affine_spectrum()
pic = scheme.picard_group()
classes = pic.underlying_set()
unit = classes(scheme.structure_sheaf())
show("unit", lambda: unit)
show("hash unit", lambda: hash(unit))
show("pic.zero()", lambda: pic.zero())
show("pic.zero() is unit?", lambda: pic.zero() == unit)
show("hash pic.zero()", lambda: hash(pic.zero()))
doubled = pic.add(unit, unit)
show("doubled", lambda: doubled)
show("doubled representative", lambda: doubled.representative())
show("hash doubled", lambda: hash(doubled))
show("doubled == unit", lambda: doubled == unit)
show("ask(doubled == unit)", lambda: ask(pic.equal(doubled, unit)))
show("repr is unit's?", lambda: doubled.representative() is unit.representative())
negated = pic.negate(unit)
show("negated", lambda: negated)
show("hash negated", lambda: hash(negated))
show("negated==unit", lambda: negated == unit)
show("ask negated == unit", lambda: ask(pic.equal(negated, unit)))
show("tensor_power on structure sheaf", lambda: scheme.structure_sheaf().tensor_power(2))
show("hash group", lambda: hash(pic))
show("hash underlying set", lambda: hash(classes))
show("FiniteOrderedSets (unit, doubled)", lambda: FiniteOrderedSets()((unit, doubled)).cardinality())
