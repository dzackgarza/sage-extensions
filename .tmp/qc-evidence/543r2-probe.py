from sage_extensions.all import *
from sage.rings.rational_field import QQ as SageQQ
from sage_extensions.categories.rings.ring_foundation import _parent_of_an_element

def show(label, thunk):
    try:
        print(f"{label:44s} => {thunk()!r}")
    except Exception as error:
        print(f"{label:44s} !! {type(error).__name__}: {error}")

print("== helper ==")
for label, value in [("cardinal(7)", cardinal(7)), ("QQ", QQ), ("SageQQ", SageQQ), ("QQ(3)", QQ(3)),
                     ("SageQQ(3)", SageQQ(3)), ("7", 7), ("(1,2)", (1, 2)), ("a lambda", lambda _i: 1)]:
    show(f"helper({label})", lambda value=value: _parent_of_an_element(value))

print("== predicate subrings ==")
sub = PredicateSubrings().an_object()
show("sub(cardinal(7))", lambda: sub(cardinal(7)))
show("sub(QQ(7))", lambda: sub(QQ(7)))
show("sub(7)", lambda: sub(7))
show("sub(QQ(1)/2)", lambda: sub(QQ(1)/2))

print("== the localization of ZZ at 2 ==")
L = ZZ.localization(2)
show("L", lambda: L)
show("L(cardinal(7))", lambda: L(cardinal(7)))
show("L(7)", lambda: L(7))
show("L(ZZ(7))", lambda: L(ZZ(7)))
show("L(QQ(1)/2)", lambda: L(QQ(1)/2))
show("L(SageQQ(1)/2)", lambda: L(SageQQ(1)/2))
show("cardinal(7) in L", lambda: cardinal(7) in L)
show("ZZ(7) in L", lambda: ZZ(7) in L)
show("QQ(1)/2 in L", lambda: QQ(1)/2 in L)
show("QQ(3) in L", lambda: QQ(3) in L)
show("SageQQ(3) in L", lambda: SageQQ(3) in L)
show("L(3) == L(6)/L(2)", lambda: L(3) == L(6)/L(2))

print("== indexed sums ==")
show("indexed_sum(NN, cardinal(3))", lambda: Cardinalities().indexed_sum(NN, cardinal(3)))
show("indexed_sum(NN, 3)", lambda: Cardinalities().indexed_sum(NN, 3))
show("indexed_sum(NN, cardinal(1)) == aleph0", lambda: Cardinalities().indexed_sum(NN, cardinal(1)) == aleph0)
show("indexed_sum(Sets.Delta[2], cardinal(3))", lambda: Cardinalities().indexed_sum(Sets.Δ[2], cardinal(3)))
show("indexed_sum(Sets.Delta[2], 4)", lambda: Cardinalities().indexed_sum(Sets.Δ[2], 4))
show("indexed_sum(NN, lambda) == aleph0", lambda: Cardinalities().indexed_sum(NN, lambda _i: cardinal(1)) == aleph0)
show("indexed_sum(NN, 'x')", lambda: Cardinalities().indexed_sum(NN, "x"))

print("== order hooks ==")
show("Mor(2,3).is_empty()", lambda: Cardinalities().Mor(2,3).is_empty())
show("Mor(2,3)._emptiness_decision()", lambda: Cardinalities().Mor(2,3)._emptiness_decision())
show("undecided hook", lambda: Cardinalities().Mor(2 ** aleph0, aleph(1))._emptiness_decision())
show("undecided is_empty", lambda: Cardinalities().Mor(2 ** aleph0, aleph(1)).is_empty())
show("Ordinals().Mor(1,2) hook", lambda: Ordinals().Mor(1,2)._emptiness_decision())
