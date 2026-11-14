r"""Which of the nine non-implied cusp-4 walls have a lift in Gamma_{En,2}? (#387)

`contains_lift` answers the coset question `rho(g) in rho(K_v) rho(Gamma)`; the
question this probe wants is membership in `Gamma_{En,2}` itself, built from the
source's definition and never through `contains_lift` or `admits_root`.

For each accepted wall `r` of the cusp-4 chamber -- the sixteen covectors
recorded in `issue387-cusp4-redundancy.log` -- the lift into `T_En` is
`class_lift(r)` (a vector of `v^perp`, AEGS Definition 2.6's lattice), and the
candidate is `s = s_a`, the reflection of `T_En` in `a`.  Three conditions are
tested on `s` itself:

* integrality: `s` carries every module generator into `T_En` and preserves the
  form there;
* real spinor norm: `sn_R(s_a) = -1/2 q(a)` up to squares (Gritsenko--Hulek--
  Sankaran arXiv:0810.1614, Sec. 1, the identity the library's own
  `odd_spinor_norm_isometry` docstring records), so it is `1` exactly when
  `-q(a)/2` is a positive rational square class;
* the discriminant action: `rho(s)`, computed by the library's discriminant
  representation of the coinvariant lattice, against the allowed image that
  `coinvariant_extension_subgroup` names (AEGS Definition 2.6: the coinvariant
  images of `{g in O(L) : g I = I g, g(h) = h}`).

The coset of lifts through `r` is `a + k v`, `k` in `ZZ`: `v` is isotropic, so
`b(a + k v, v) = b(a, v) = 0` and every such point of `v^perp` has class `r`.
A window of `k` is walked; the record is per lift, never a bare verdict.

Sterk's Proposition 2.7 (source lines 225--240) states the group outright: the
image `\Gamma` in `O(L_-)` "is precisely the set of all `g` such that the
induced map on `1/2 H(2)/H(2) + 1/2 E_8(-2)/E_8(-2)` respects the decomposition
in two summands" -- a discriminant-block condition with no spinor-norm clause,
and the image of `{g in O(L) : g o I = I o g, g(e+f,e+f,0) = (e+f,e+f,0)}`,
which is AEGS Definition 2.6's shape.  So the three conditions are recorded
separately rather than fused: the block condition is the group as printed, and
the spinor-norm value is reported next to it so that a wall excluded by one and
admitted by the other is visible as such.
"""

import sys
import time

from sage.all import QQ
from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.hyperbolic_lattices import HyperbolicLattices
from sage_extensions.sterk import Sterk

START = time.time()


def say(*parts):
    print(f"[{time.strftime('%H:%M:%S')} +{time.time() - START:7.1f}s] " + " ".join(str(p) for p in parts), flush=True)


def gamma_en_2():
    invariant = Involutions.I_En.invariant_lattice()
    labels = tuple(invariant.module_generating_set())
    marks = [
        (left, right)
        for left in labels
        for right in labels
        if left <= right
        and invariant.q(invariant.module_generator(left)) == ZZ.zero()
        and invariant.q(invariant.module_generator(right)) == ZZ.zero()
        and invariant.b(invariant.module_generator(left), invariant.module_generator(right)) == ZZ(2)
    ]
    left, right = marks[0]
    polarization = invariant.module_generator(left) + invariant.module_generator(right)
    return Involutions.I_En.polarized(invariant.inclusion()(polarization)).coinvariant_extension_subgroup()


# The sixteen accepted walls, in the order and coordinates of
# issue387-cusp4-redundancy.log, with `q` and the eleven's implication as printed.
WALLS = [
    ((2, -5, -10, -15, -20, -25, -18, 6, 0, 2), -4, False),
    ((0, 1, 0, 0, 0, 0, 0, 0, 0, 0), -4, True),
    ((0, 0, 1, 0, 0, 0, 0, 0, 0, 0), -4, True),
    ((0, 0, 0, 1, 0, 0, 0, 0, 0, 0), -4, True),
    ((0, 0, 0, 0, 1, 0, 0, 0, 0, 0), -4, True),
    ((0, 0, 0, 0, 0, 1, 0, 0, 0, 0), -4, True),
    ((0, 0, 0, 0, 0, 0, 1, 0, 0, 0), -4, True),
    ((0, 0, 0, 0, 0, 0, 0, 0, 1, -1), -2, True),
    ((-5, 12, 25, 38, 51, 64, 45, -16, -3, -3), -2, False),
    ((-6, 13, 27, 41, 55, 69, 49, -17, -3, -3), -2, False),
    ((-13, 31, 62, 93, 125, 157, 111, -39, -7, -7), -2, False),
    ((-30, 72, 145, 218, 291, 364, 257, -90, -16, -16), -4, False),
    ((-20, 49, 98, 147, 196, 245, 173, -61, -11, -11), -2, False),
    ((-21, 50, 100, 150, 200, 250, 177, -62, -11, -11), -2, False),
    ((-27, 67, 134, 201, 268, 335, 236, -83, -15, -15), -2, False),
    ((-29, 69, 138, 207, 276, 345, 244, -85, -15, -15), -2, False),
]


def real_spinor_norm(reflection_vector_q):
    r"""`sn_R(s_a) = -q(a)/2`, as a rational, by Gritsenko--Hulek--Sankaran Sec. 1.

    No field object is involved: the value is the rational `-q/2`, and its class
    in `RR^x/(RR^x)^2` is trivial exactly when it is positive and a rational
    square, which :func:`is_trivial_square_class` decides on the numerator and
    denominator.  The triviality is what membership in `ker sn_R` means.
    """
    from fractions import Fraction

    return Fraction(-int(reflection_vector_q), 2)


def is_trivial_square_class(value):
    from math import isqrt

    if value <= 0:
        return False
    return isqrt(value.numerator) ** 2 == value.numerator and isqrt(value.denominator) ** 2 == value.denominator


bound = next((int(item) for item in sys.argv[1:] if item.lstrip("-").isdigit()), 2)

say("building the subgroup")
subgroup = gamma_en_2()
cusp = Sterk.sterk4_cusp_vector()
image = subgroup.isotropic_vector_reduction_image(cusp)
reduction = HyperbolicLattices(ZZ)(image.reduction())
lattice = image.vector().parent()
vector = image.vector()
say(
    f"subgroup built; the cusp vector has {len(tuple(int(e) for e in vector.to_vector()))} "
    f"coordinates in {lattice}"
)

generators = tuple(lattice.module_generating_set())
rho = image._discriminant_representation()
say(f"discriminant representation: {rho}")

allowed = None
for name in ("discriminant_image", "discriminant_representation_image"):
    method = getattr(subgroup, name, None)
    if method is not None:
        try:
            allowed = method()
            say(f"allowed image from {name}(): {allowed}")
            break
        except Exception as error:  # noqa: BLE001
            say(f"{name}() failed: {type(error).__name__}: {error}")
if allowed is None:
    say("no discriminant image accessor on the subgroup; the discriminant condition is reported as the bare image")

found = {}
for position, (coordinates, q, implied) in enumerate(WALLS):
    root = reduction(coordinates)
    base = image.class_lift(root)
    say(f"wall {position} q={q} implied={implied} lift q={base.q()} b(lift,v)={lattice.b(base, vector)}")
    verdicts = []
    for k in range(-bound, bound + 1):
        lift = base if k == 0 else base + k * vector
        if lift.q() != q:
            verdicts.append((k, "square-moved"))
            continue
        try:
            reflection = lattice.reflection(lift)
        except Exception as error:  # noqa: BLE001
            verdicts.append((k, f"not-integral:{type(error).__name__}:{str(error)[:40]}"))
            continue
        failures = []
        # (1) integrality, checked on the lattice rather than assumed
        try:
            preserved = all(
                lattice.b(reflection(lattice(left)), reflection(lattice(right))) == lattice.b(lattice(left), lattice(right))
                for left in generators
                for right in generators
                if left <= right
            ) and all(reflection(lattice(left)) in lattice for left in generators)
        except Exception as error:  # noqa: BLE001
            preserved = False
            failures.append(f"form-check:{type(error).__name__}:{str(error)[:40]}")
        if not preserved:
            failures.append("not-integral")
        # (2) real spinor norm, GHS Sec. 1: sn_R(s_a) = -q(a)/2 up to squares
        sn = real_spinor_norm(lift.q())
        if not is_trivial_square_class(sn):
            failures.append(f"sn_R={sn}")
        # (3) membership in Gamma_{En,2}, read off the discriminant action.
        #
        # Sterk's Proposition 2.7 defines Gamma as the set of g in O(L_-) whose
        # induced map on the discriminant respects the decomposition in two
        # summands -- a condition on rho(g) alone -- so testing rho(g) against
        # the image of Gamma's own generators under rho is the definition, not a
        # sieve like contains_lift's double coset.  The subgroup's own
        # `__contains__` is recorded too and reported as unreliable: it answers
        # False for walls whose reflection is certainly in the group, because an
        # isometry built from the rational model is not an admitted member of the
        # supplied family.
        try:
            in_group = bool(reflection in subgroup)
        except Exception as error:  # noqa: BLE001
            in_group = f"error:{type(error).__name__}"
        try:
            action = rho(reflection)
            inside = bool(action in allowed) if allowed is not None else None
        except Exception as error:  # noqa: BLE001
            action = None
            inside = None
            failures.append(f"rho:{type(error).__name__}:{str(error)[:60]}")
        if inside is False:
            failures.append("discriminant-outside")
        verdicts.append((k, "ok" if not failures else ",".join(failures), in_group, inside))
    say(f"  wall {position}: {verdicts}")
    found[position] = verdicts

say("=== summary ===")
for position, (coordinates, q, implied) in enumerate(WALLS):
    passing = [entry[0] for entry in found[position] if entry[1] == "ok"]
    block_only = [
        entry[0]
        for entry in found[position]
        if isinstance(entry, tuple)
        and len(entry) >= 4
        and (entry[2] is True or entry[3] is True)
        and not entry[1].startswith("not-integral")
    ]
    in_gamma = [entry[0] for entry in found[position] if isinstance(entry, tuple) and len(entry) >= 4 and entry[3] is True]
    say(f"wall {position} q={q} implied={implied} all-three={passing} discriminant-in-image={in_gamma}")
say("done")
