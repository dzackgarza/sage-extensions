r"""``cusp_chamber`` from a vertex of card 029J's 4.3.8 polyhedron, after the kernel repair (#402)

Vinberg's algorithm (E. B. Vinberg, *On the groups of unit elements of certain quadratic
forms*, Math. USSR Sb. 16 (1972), §3.2, Propositions 4 and 5, pp. 28--29) run from a
point ``p_0`` returns the chamber of the reflection group that contains ``p_0`` and stops
when that polyhedron has finite volume.  ``p_0`` here is the vertex of positive square of
the polyhedron ``P`` of card 029J row 4.3.8 (H. Sterk, Math. Z. 207 (1991), (4.3.8) with
Fig. 10, p. 23) with the least square, computed in ``N = v^perp/Zv`` from the printed walls'
classes and lifted to ``v^perp`` by ``class_lift``.  The record compares the returned walls
with the eleven printed walls as classes of ``N``.
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


def coordinates(element):
    return vector(QQ, [int(element.to_vector()(label)) for label in labels])


printed = [coordinates(reduction.projection()(perpendicular.inclusion().lift(
    lattice([int(t) for t in wall.to_vector()])))) for wall in Sterk.cusp_roots_in_TEn("Sterk_4")]
cone = Polyhedron(ieqs=[[0] + list(wall * gram) for wall in printed])
vertex = min((vector(QQ, ray) for ray in cone.rays() if vector(QQ, ray) * gram * vector(QQ, ray) > 0),
             key=lambda ray: ray * gram * ray)
say("p_0 in N", tuple(vertex), "square", vertex * gram * vertex,
    "printed walls through it", sum(1 for wall in printed if wall * gram * vertex == 0))
point = image.class_lift(reduction([int(t) for t in vertex]))
say("rho(K_v) coset representatives", len(image._kernel_coset_representatives()))
asked = []
admits = image.admits_root


def counted(root):
    answer = admits(root)
    asked.append(answer)
    if len(asked) % 100 == 0:
        say("admits_root asked", len(asked), "admitted", sum(asked))
    return answer


image.admits_root = counted
chamber = image.cusp_chamber(point)
say("admits_root asked", len(asked), "admitted", sum(asked))
walls = [coordinates(wall) for wall in chamber.wall_roots()]
say("complete", chamber.is_complete_wall_set(), "walls", len(walls))
for wall in walls:
    say("  wall", tuple(wall), "square", wall * gram * wall, "printed", wall in printed)
say("returned walls equal the printed walls as a set:", set(map(tuple, walls)) == set(map(tuple, printed)))
say("done")
