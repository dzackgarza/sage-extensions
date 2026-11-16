"""Probe: the six findings of the #556 review, in one table, on any tree.

Reads only public operations except the three readings a session cannot make:
the engine kind behind a group, the number of engine conjugations one pair
costs, and the declared construction contract of the conjugate kind.
"""

import traceback

from sage_extensions.all import *
import sage_extensions.categories.group.groups as groups_module
from sage_extensions.categories.group.groups import ConjugateSubgroups
from sage_extensions.owned_category import construction_parameters


def show(label, thunk):
    try:
        print("%-58s %s" % (label, thunk()))
    except Exception as error:
        print("%-58s raised %s: %s" % (label, type(error).__name__, str(error)[:120]))


print("=== 1. the action law with a normalizing element")
group = Groups.S(3)
transposition = group((1, 2))
subgroup = group.subgroup((transposition,))
flagging = group((1, 3))
inner = group.conjugate_subgroup(transposition, subgroup)
show("h.H retains the pair", lambda: (inner.conjugated_subgroup() is subgroup, inner.conjugator() == transposition))
show("h.H is H itself", lambda: inner is subgroup)
show("h.H order and (1 2) in it", lambda: (inner.order(), transposition in inner))
left = group.conjugate_subgroup(flagging, inner)
right = group.conjugate_subgroup(flagging * transposition, subgroup)
show("g.(h.H) is (gh).H", lambda: left is right)
show("(2 3) in g.(h.H)", lambda: group((2, 3)) in left)
show("(1 2) not in g.(h.H)", lambda: transposition not in left)

print("=== 2. a conjugate conjugates its own subgroups")
conjugate = group.conjugate_subgroup(group((1, 2, 3)), subgroup)
trivial = conjugate.subgroup(())
show("conjugate order", lambda: conjugate.order())
show("(2 3) carries its trivial subgroup to itself", lambda: conjugate.conjugate_subgroup(group((2, 3)), trivial).order())

print("=== 3. an engine with no GAP model of its elements")
abelian = Groups.Abelian([2, 4])
short, long = tuple(abelian.group_generators())
cyclic = abelian.subgroup((short,))
print("%-58s %s" % ("engine kind", type(groups_module._engine_group(abelian)).__name__))
show("conjugate order", lambda: abelian.conjugate_subgroup(long, cyclic).order())
show("generator in the conjugate", lambda: short in abelian.conjugate_subgroup(long, cyclic))

print("=== 4. a group with no engine")
plane = Lattices(ZZ)("U")
isometries = plane.O()
labels = plane.module_generating_set()
first, second = plane.module_generators()
swap = isometries({labels[0]: second, labels[1]: first})
reflection = isometries({labels[0]: -first, labels[1]: second})
cyclic_subgroup = isometries.subgroup((reflection,))
print("%-58s %s" % ("O(U) supplies an engine", isometries._supplies_engine()))
show("the conjugate is formed", lambda: isometries.conjugate_subgroup(swap, cyclic_subgroup).conjugator() == swap)
show("g^-1.(g.H) is H", lambda: isometries.conjugate_subgroup(~swap, isometries.conjugate_subgroup(swap, cyclic_subgroup)) is cyclic_subgroup)

print("=== 5. one pair's engine conjugations")
wrapped = groups_module.libgap


class Counter:
    calls = 0

    def __call__(self, *arguments, **keywords):
        return wrapped(*arguments, **keywords)

    def __getattr__(self, name):
        value = getattr(wrapped, name)
        if name != "ConjugateSubgroup":
            return value

        def counted(*arguments, **keywords):
            Counter.calls += 1
            return value(*arguments, **keywords)

        return counted


big = Groups.S(4)
one_two = big((1, 2))
source = big.subgroup((one_two,))
groups_module.libgap = Counter()
try:
    fresh = big.conjugate_subgroup(big((1, 3)), source)
    print("%-58s %d" % ("engine conjugations: forming a conjugate that is not H", Counter.calls))
    print("%-58s %d" % ("engine conjugations: reading its order", Counter.calls))
    show("its order", lambda: fresh.order())
    print("%-58s %d" % ("engine conjugations: after reading its order", Counter.calls))
    Counter.calls = 0
    normalizing = big.conjugate_subgroup(one_two, source)
    print("%-58s %d" % ("engine conjugations: forming a conjugate by an element of H", Counter.calls))
    show("its order", lambda: normalizing.order())
    print("%-58s %d" % ("engine conjugations: after reading its order", Counter.calls))
finally:
    groups_module.libgap = wrapped

print("=== 6. the declared construction contract")
for parameter in construction_parameters(ConjugateSubgroups.ParentMethods) or ():
    if parameter.name in ("conjugated_subgroup", "conjugator"):
        print("%-58s %s" % (parameter.name, "required" if parameter.required else "optional"))
