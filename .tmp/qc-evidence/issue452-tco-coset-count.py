r"""How many coset representatives does a T_Co line force the locus to test? (#452)

Reads the same Smith data the locus reads and prints the count, without running the
per-coset lift tests.
"""
import time
from math import prod

from sage_extensions.all import *  # noqa: F401,F403

from sage.all import ZZ, gcd, lcm
from sage.matrix.constructor import matrix
from sage.rings.rational_field import QQ

T0 = time.time()


def say(*a):
    print(f"[{time.time()-T0:7.1f}s]", *a, flush=True)


def report(name, lattice, vector):
    line = lattice.primitive_isotropic_subobject(vector)
    reduction = line.isotropic_reduction()
    torsor = reduction.rational_lifts(reduction, reduction.Aut().one())
    target = torsor.target_reduction().isotropic_embedding().codomain()
    quotient = torsor.integral_parameter_quotient()
    P = quotient.domain()
    m = int(torsor.integral_parameter_period())
    labels = tuple(P.module_generating_set())
    rank = int(P.module_rank())
    rational_target = torsor._target_witt.rational_lattice()
    columns = [
        list(rational_target.rational_coordinates(
            torsor._target_section(P.inclusion()(P.module_generator(label)).underlying_element())
        ).list())
        for label in labels
    ]
    coordinates = matrix(QQ, int(target.module_rank()), rank, [
        columns[column][entry]
        for entry in range(int(target.module_rank()))
        for column in range(rank)
    ])
    denominator = ZZ(1)
    for entry in coordinates.list():
        denominator = lcm(denominator, ZZ(entry.denominator()))
    integral_coordinates = matrix(ZZ, int(target.module_rank()), rank, [
        ZZ((entry * denominator).numerator()) for entry in coordinates.list()
    ])
    smith, _left, right = integral_coordinates.smith_form()
    steps = tuple(int(denominator // gcd(abs(smith[i, i]), denominator)) for i in range(rank))
    coset_steps = tuple(int(gcd(step, m)) for step in steps)
    counts = tuple(m // step for step in coset_steps)
    say(name, "div", lattice.div(vector), "m", m, "rank", rank,
        "smith", [smith[i, i] for i in range(rank)])
    say(name, "steps", steps, "coset_steps", coset_steps)
    say(name, "|P/mP| =", m ** rank, "#lift tests =", prod(coset_steps),
        "|K| =", prod(counts))


T_Co = Lattices(ZZ)([[2]]) + (NamedLattices.U + NamedLattices.E8).twist(2)
labels = tuple(T_Co.module_generating_set())
say("T_Co rank", T_Co.module_rank(), "labels", labels[:6])
candidates = [T_Co.module_generator(label) for label in labels]
isotropic = [vector for vector in candidates if T_Co.q(vector) == ZZ.zero() and vector.is_primitive()]
say("isotropic primitive basis vectors:", len(isotropic))
for position, vector in enumerate(isotropic[:2]):
    report(f"T_Co line {position}", T_Co, vector)
say("done")
