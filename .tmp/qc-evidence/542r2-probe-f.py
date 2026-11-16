"""#542 round 2: two Picard classes with distinct representatives."""
from sage_extensions.all import *  # noqa


def show(label, f):
    try:
        print(f"{label}: {f()!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")


ring = QQ["x"]
scheme = ring.affine_spectrum()
sheaf = scheme.structure_sheaf()
pic = scheme.picard_group()
classes = pic.underlying_set()
unit = classes(sheaf)
show("type pic", lambda: type(pic).__name__)
show("dir pic (group law)", lambda: [n for n in dir(pic) if n in ("zero", "add", "negate", "scalar_multiple", "sum", "underlying_set")])
negated = -unit
show("hash(-unit)", lambda: hash(negated))
show("hash(unit)", lambda: hash(unit))
show("(-unit) == unit", lambda: negated == unit)
show("ask equal", lambda: ask(pic.equal(negated, unit)))
show("representative is unit's", lambda: negated.representative() is unit.representative())
show("dual of O is O?", lambda: sheaf.dual_sheaf() is sheaf)
show("FiniteOrderedSets(unit, -unit)", lambda: FiniteOrderedSets()((unit, negated)).cardinality())
show("underlying set zero", lambda: classes.zero())
