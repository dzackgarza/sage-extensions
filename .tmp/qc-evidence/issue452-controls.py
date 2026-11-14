r"""Which small marked-line controls already disagree with the lift itself? (#405)

For each candidate lattice, compare :meth:`integral_parameter_classes` with the classes
of ``P/mP`` whose own parameter lifts integrally, decided by the lift.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403

T0 = time.time()


def say(*a):
    print(f"[{time.time()-T0:7.1f}s]", *a, flush=True)


def control(name, lattice):
    labels = tuple(lattice.module_generating_set())
    marked = lattice.module_generator(labels[0])
    if lattice.q(marked) != lattice.base_ring().zero():
        say(name, "SKIP: the first basis vector is not isotropic")
        return
    reduction = lattice.primitive_isotropic_subobject(marked).isotropic_reduction()
    torsor = reduction.rational_lifts(reduction, reduction.Isom(reduction).identity())
    quotient = torsor.integral_parameter_quotient()
    inclusion = quotient.domain().inclusion()
    isometries = lattice.Isom(lattice)

    def lift_of(residue):
        parameter = inclusion(quotient.preimage(residue)).underlying_element()
        return torsor.parameterization()(parameter)

    integral_classes = {
        residue for residue in quotient.codomain()
        if lift_of(residue).integral_restriction(lattice, lattice) in isometries
    }
    reported = set(torsor.integral_parameter_classes())
    say(name, "div", lattice.div(marked), "rank", lattice.module_rank(),
        "|P/mP| =", len(tuple(quotient.codomain())),
        "|integral| =", len(integral_classes), "|reported| =", len(reported),
        "AGREE" if reported == integral_classes else "DISAGREE",
        "missing", len(integral_classes - reported), "extra", len(reported - integral_classes))


candidates = {
    "U + <2>": Lattices(ZZ)("U") + Lattices(ZZ)([[2]]),
    "U + U + <2>": Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[2]]),
    "U(2) + <2>": Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[2]]),
    "U(2) + U(2)": Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[0, 2], [2, 0]]),
    "U(4) + <2>": Lattices(ZZ)([[0, 4], [4, 0]]) + Lattices(ZZ)([[2]]),
    "U(2) + U(4)": Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[0, 4], [4, 0]]),
    "U(2) + U(2) + <2>": (Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[0, 2], [2, 0]])
                          + Lattices(ZZ)([[2]])),
    "U(2) + A2": Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)("A2"),
    "U(2) + <2> + <2>": (Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[2]])
                         + Lattices(ZZ)([[2]])),
    "U(2) + <4>": Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[4]]),
}
for name, lattice in candidates.items():
    try:
        control(name, lattice)
    except Exception as error:  # probe only
        say(name, "ERROR", type(error).__name__, str(error)[:200])
say("done")
