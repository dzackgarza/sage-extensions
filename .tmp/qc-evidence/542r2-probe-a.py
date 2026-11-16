"""#542 round 2: what the reviewer measured, and what a hash could read."""
import traceback
from sage_extensions.all import *  # noqa
from sage.rings.qqbar import AA, QQbar
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ


def show(label, f):
    try:
        print(f"{label}: {f()!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")

print("=== reals")
two = RR(2)
print("type(RR(2))", type(two).__mro__)
show("RR(2) == 2", lambda: two == 2)
show("hash(RR(2))", lambda: hash(two))
show("hash(2)", lambda: hash(2))
show("hash(AA(2))", lambda: hash(AA(2)))
show("type(AA(2))", lambda: type(AA(2)))
show("hash(AA(QQ(1)/2))", lambda: hash(AA(QQ(1)/2)))
show("hash(QQ(1)/2)", lambda: hash(QQ(1)/2))
show("RR(1/2)==QQ(1)/2", lambda: RR(QQ(1)/2) == QQ(1)/2)
show("hash(AA(sqrt2))", lambda: hash(AA(2).sqrt()))
show("RR(2).sqrt()**2 == RR(2)", lambda: (RR(2).sqrt()**2) == RR(2))
show("expression of RR(2)", lambda: RR(2).expression())
show("expression type", lambda: type(RR(2).expression()))
show("RR(pi) expr", lambda: RR.pi() if hasattr(RR, 'pi') else None)
show("AA(pi)", lambda: AA(RR.pi().expression()) if hasattr(RR, 'pi') else None)
show("hash(AA(2).sqrt())  vs QQbar", lambda: hash(QQbar(AA(2).sqrt())))
show("FiniteOrderedSets of (sqrt2^2, 2)", lambda: FiniteOrderedSets()((RR(2).sqrt()**2, ZZ(2))).cardinality())
show("len({RR(2), 2})", lambda: len({RR(2), 2}))
show("hash({RR(2): 'a'}[2])", lambda: {RR(2): 'a'}[2])
