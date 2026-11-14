r"""Where the walk's sixteen walls lie relative to card 029J's 4.3.8 polyhedron, in N itself (#402)

The polyhedron ``P`` of card 029J row 4.3.8 (H. Sterk, Math. Z. 207 (1991), (4.3.8)
with Fig. 10, p. 23) is a cone in ``N = v^perp/Zv``, not in ``T_En``.  This record
computes it there: each printed wall is read as its class in ``N`` (any lift gives the
same class), ``P = {x in N_R : b(x, w) >= 0 for the eleven}``, and its extreme rays.
Every ray has square ``>= 0``, so ``P`` lies in the closed positive cone and has finite
volume.  Then each of the sixteen walls of ``issue387-cusp4-facets.log`` (the walk at
``max_decompositions=12``) is paired with every ray: ``implied`` if all pairings are
``>= 0``, ``opposite`` if all are ``<= 0``, ``crosses`` otherwise.  A mirror meets the
interior of ``P`` exactly when its wall ``crosses``.

``issue387-cusp4-mirrors.py`` decided the same question in ``Z^12``: its witnesses ``x``
pair ``-10`` or ``-14`` with ``v`` (``issue387-cusp4-lifts.log``), so they are not
points of ``v^perp``, and the pairing of a ``T_En`` lift of a class with such an ``x``
depends on the lift.
"""
import time
from sage_extensions.all import *  # noqa: F401,F403
from sage.matrix.constructor import matrix
from sage.modules.free_module_element import vector
from sage.rings.rational_field import QQ
from sage.geometry.polyhedron.constructor import Polyhedron
from sage_extensions.sterk import Sterk

START = time.time()


def say(*parts):
    print(f"[{time.time() - START:7.1f}s]", *parts, flush=True)


def gamma_en_2():
    invariant = Involutions.I_En.invariant_lattice()
    labels = tuple(invariant.module_generating_set())
    marks = [(l, r) for l in labels for r in labels if l <= r
             and invariant.q(invariant.module_generator(l)) == ZZ.zero()
             and invariant.q(invariant.module_generator(r)) == ZZ.zero()
             and invariant.b(invariant.module_generator(l), invariant.module_generator(r)) == ZZ(2)]
    l, r = marks[0]
    polarization = invariant.module_generator(l) + invariant.module_generator(r)
    return Involutions.I_En.polarized(invariant.inclusion()(polarization)).coinvariant_extension_subgroup()


image = gamma_en_2().isotropic_vector_reduction_image(Sterk.sterk4_cusp_vector())
lattice, reduction = image.lattice(), image.reduction()
perpendicular = reduction.orthogonal_complement()
labels = tuple(reduction.module_generating_set())
generators = [reduction.module_generator(label) for label in labels]
gram = matrix(QQ, [[int(reduction.b(x, y)) for y in generators] for x in generators])
say("Gram of N in its frame, determinant", gram.det())


def class_of(wall):
    return reduction.projection()(perpendicular.inclusion().lift(lattice([int(t) for t in wall.to_vector()])))


def coordinates(element):
    return vector(QQ, [int(element.to_vector()(label)) for label in labels])


names = [f"alpha_{index}" for index in range(2, 13)]
walls = [coordinates(class_of(wall)) for wall in Sterk.cusp_roots_in_TEn("Sterk_4")]
for name, wall in zip(names, walls):
    say(name, tuple(wall), "square", wall * gram * wall)
cone = Polyhedron(ieqs=[[0] + list(wall * gram) for wall in walls])
rays = [vector(QQ, ray) for ray in cone.rays()]
say("P: rays", len(rays), "lines", len(cone.lines()), "ray squares", sorted({ray * gram * ray for ray in rays}))
facets = [
    (2, -5, -10, -15, -20, -25, -18, 6, 0, 2), (0, 1, 0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 1, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 1, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 1, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 1, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0, 1, -1),
    (-5, 12, 25, 38, 51, 64, 45, -16, -3, -3), (-6, 13, 27, 41, 55, 69, 49, -17, -3, -3),
    (-13, 31, 62, 93, 125, 157, 111, -39, -7, -7), (-30, 72, 145, 218, 291, 364, 257, -90, -16, -16),
    (-20, 49, 98, 147, 196, 245, 173, -61, -11, -11), (-21, 50, 100, 150, 200, 250, 177, -62, -11, -11),
    (-27, 67, 134, 201, 268, 335, 236, -83, -15, -15), (-29, 69, 138, 207, 276, 345, 244, -85, -15, -15),
]
for index, facet in enumerate(facets):
    wall = vector(QQ, facet)
    pairings = [wall * gram * ray for ray in rays]
    side = ("implied" if all(p >= 0 for p in pairings)
            else "opposite" if all(p <= 0 for p in pairings) else "crosses")
    say("walk wall", index, facet, "square", wall * gram * wall, side,
        "printed" if wall in walls else "")
say("done")
