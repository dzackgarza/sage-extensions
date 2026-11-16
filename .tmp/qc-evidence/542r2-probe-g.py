"""#542 round 2: Picard group law through scalar_multiple."""
from sage_extensions.all import *  # noqa


def show(label, f):
    try:
        print(f"{label}: {f()!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")


ring = QQ["x"]
scheme = ring.affine_spectrum()
pic = scheme.picard_group()
classes = pic.underlying_set()
unit = classes(scheme.structure_sheaf())
show("hash unit", lambda: hash(unit))
doubled = pic.scalar_multiple(2, unit)
show("2*unit", lambda: doubled)
show("hash 2*unit", lambda: hash(doubled))
show("2*unit repr is unit repr", lambda: doubled.representative() is unit.representative())
show("2*unit == unit", lambda: doubled == unit)
show("ask equal(2*unit, unit)", lambda: ask(pic.equal(doubled, unit)))
nan = pic.scalar_multiple(-1, unit)
show("hash -1*unit", lambda: hash(nan))
show("-1*unit repr is unit repr", lambda: nan.representative() is unit.representative())
show("ask equal(-1*unit, unit)", lambda: ask(pic.equal(nan, unit)))
show("FiniteOrderedSets(unit, 2*unit)", lambda: FiniteOrderedSets()((unit, doubled)).cardinality())
show("FiniteOrderedSets(unit, -unit)", lambda: FiniteOrderedSets()((unit, nan)).cardinality())
