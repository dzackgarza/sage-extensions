"""#542 round 2: cross-type real equality, and what AA hashes."""
from sage_extensions.all import *  # noqa
from sage.rings.qqbar import AA, QQbar
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ
from sage.symbolic.ring import SR


def show(label, f):
    try:
        print(f"{label}: {f()!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")

r2 = RR(2)
sqrt2 = RR(2).sqrt()
print("=== cross-type equality")
show("RR(2) == QQ(2)", lambda: r2 == QQ(2))
show("RR(2) == SR(2)", lambda: r2 == SR(2))
show("RR(sqrt2) == AA(2).sqrt()", lambda: sqrt2 == AA(2).sqrt())
show("RR(sqrt2) == sqrt(2) (SR)", lambda: sqrt2 == SR(2).sqrt())
show("RR(pi) == SR(pi)", lambda: RR.pi() == SR.pi() if hasattr(RR, 'pi') else None)
show("RR(2) == 2.0 (float)", lambda: r2 == 2.0)
show("RR(2) == RR(2) again", lambda: r2 == RR(2))

print("=== AA hash is a function of the value")
show("hash(AA(2))", lambda: hash(AA(2)))
show("hash(AA(4)/2)", lambda: hash(AA(4)/2))
show("hash(AA(sqrt2))", lambda: hash(AA(2).sqrt()))
show("hash(AA(8).sqrt()/2)", lambda: hash(AA(8).sqrt()/2))
show("hash(QQbar(AA(2).sqrt()))", lambda: hash(QQbar(AA(2).sqrt())))
show("hash(SR(2))", lambda: hash(SR(2)))
show("hash(SR(sqrt2))", lambda: hash(SR(2).sqrt()))

print("=== what a value hash could read")
show("AA(RR(2).expression())", lambda: AA(RR(2).expression()))
show("AA(RR(1/2).expression())", lambda: AA(RR(QQ(1)/2).expression()))
show("AA(sqrt2.expression())", lambda: AA(sqrt2.expression()))
show("QQ(RR(2).expression())", lambda: QQ(RR(2).expression()))
show("is_integral", lambda: [ (x, AA(x.expression()).is_rational() if x.expression().is_rational() else None) for x in (r2, sqrt2)])

print("=== RR(pi)?")
show("RR has pi", lambda: hasattr(RR, 'pi'))
show("RR.pi()", lambda: RR.pi())
show("AA(RR.pi().expression())", lambda: AA(RR.pi().expression()))
show("RR.pi() == RR.pi()", lambda: RR.pi() == RR.pi())
show("RR.pi() == 2*RR.pi()/2", lambda: RR.pi() == 2*RR.pi()/2)
show("expr of 2*pi/2", lambda: (2*RR.pi()/2).expression())
