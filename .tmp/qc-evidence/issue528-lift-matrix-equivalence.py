r"""#528: the locus' matrix test against the composition's integral restriction, class by class.

The repair replaces the per-class test `_lift_at(coordinates).integral_restriction(...)`
by the lift's own matrix -- the transvection's column matrix times the base point's
coordinate matrix, with the base point's images built once -- so the contract to
check is that the two readings answer the same thing on **every** class the locus
tests, not on a sample.

The probe wraps `_parameter_at`, which every tested class passes through, so the
tested coordinates are recorded without reconstructing the Smith reading, runs the
locus, and then asks each recorded class for the composition's own integral
restriction.  A disagreement is printed with its coordinates and index.

    sage -python <this file>            # the control U(2) + U(2) + <2>
    sage -python <this file> line       # also the T_Co line of Sterk's cusp 4
"""

import time

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories import isotropic_lifts as il

START = time.monotonic()
RECORDED = []


def say(*parts):
    print(f"[{time.monotonic() - START:7.1f}s]", *parts, flush=True)


def record_parameter_at():
    owner = None
    for klass in il.IsotropicReductionLiftTorsors.ParentMethods.__mro__:
        if "_parameter_at" in vars(klass):
            owner = klass
            break
    assert owner is not None, "IsotropicReductionLiftTorsors defines no _parameter_at"
    original = vars(owner)["_parameter_at"]

    def recording(self, coordinates):
        RECORDED.append(tuple(coordinates))
        return original(self, coordinates)

    setattr(owner, "_parameter_at", recording)


def torsor_at(line):
    reduction = line.isotropic_reduction()
    return reduction.rational_lifts(reduction, reduction.Aut().one())


def compare(name, torsor):
    RECORDED.clear()
    begin = time.monotonic()
    passing, kernel, _parameters = torsor._integral_parameter_cosets()
    tested = tuple(RECORDED)
    spent = time.monotonic() - begin
    passing_coordinates = set(RECORDED) if False else None
    say(f"{name}: the locus tested {len(tested)} classes in {spent:.3f} s")
    source = torsor.source_reduction().isotropic_embedding().codomain()
    target = torsor.target_reduction().isotropic_embedding().codomain()
    quotient = torsor.integral_parameter_quotient()
    classes_module = quotient.codomain()
    images = tuple(
        classes_module(quotient(quotient.domain().module_generator(label)))
        for label in quotient.domain().module_generating_set()
    )
    period = int(torsor.integral_parameter_period())

    def class_of(coefficients):
        return sum(
            (
                classes_module.scalar_multiple(
                    classes_module.base_ring()(coefficient), image
                )
                for coefficient, image in zip(coefficients, images, strict=True)
                if coefficient % period != 0
            ),
            classes_module.zero(),
        )

    agree = 0
    disagree = []
    reference_begin = time.monotonic()
    for coordinates in tested:
        by_matrix = class_of(coordinates) in passing
        by_composition = (
            torsor._lift_at(coordinates).integral_restriction(source, target) is not None
        )
        if by_matrix == by_composition:
            agree += 1
        else:
            disagree.append(
                (coordinates, by_matrix, by_composition, len(disagree))
            )
    reference = time.monotonic() - reference_begin
    say(f"{name}: {agree} of {len(tested)} classes agree; {len(disagree)} disagree")
    for coordinates, by_matrix, by_composition, _index in disagree[:10]:
        say(f"    {coordinates}: matrix says {by_matrix}, composition says {by_composition}")
    say(
        f"RESULT {name} tested={len(tested)} agree={agree} disagree={len(disagree)} "
        f"matrix_seconds={spent:.3f} composition_seconds={reference:.3f}"
    )
    return not disagree


def main(argv):
    record_parameter_at()
    hyperbolic = Lattices(ZZ)([[0, 2], [2, 0]])
    control = hyperbolic + hyperbolic + Lattices(ZZ)([[2]])
    line = control.primitive_isotropic_subobject(tuple(control.module_generators())[0])
    ok = compare("control U2+U2+<2>", torsor_at(line))
    if "line" in argv:
        from sage_extensions.sterk import Sterk

        lattice = NamedLattices.TEn
        vector = Sterk.sterk4_cusp_vector()
        ok = compare(
            "T_En cusp 4 line", torsor_at(lattice.primitive_isotropic_subobject(vector))
        ) and ok
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
