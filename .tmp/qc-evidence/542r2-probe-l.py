"""#542 round 2: which scheme morphisms refuse a hash, and why."""
from sage_extensions.all import *  # noqa


def show(label, f):
    try:
        v = f()
        print(f"{label}: {v!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")


line = ProjectiveSpaces(QQ)(1)
show("structure_morphism", lambda: type(line.structure_morphism()).__name__)
sm = line.structure_morphism()
show("role", lambda: getattr(sm, "_gluing_role", None))
show("hash", lambda: hash(sm))
show("domain stable", lambda: sm.domain() is line.Mor(sm.codomain()).domain() if False else sm.domain() is sm.domain())
show("hash again", lambda: hash(line.structure_morphism()))
show("rebuilt equal", lambda: ask(sm == line.structure_morphism()))
show("FiniteOrderedSets", lambda: FiniteOrderedSets()((sm, line.structure_morphism())).cardinality())
show("chart embedding", lambda: getattr(line, "chart_embedding", None))
