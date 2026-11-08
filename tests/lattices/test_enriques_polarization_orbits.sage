r"""DSH polarization orbit rows of the Enriques family, through the public group (#294).

The 87 numerical polarizations of Dutour Sikirić–Hulek (arXiv:2302.01679, Table 1,
p. 13 and Table 2) are indexed by admissible subsets of the Coxeter diagram of
$O(U + E_8(-1))$.  The source convention, stated with the tables and verified row by
row against the rendered pages 13 and 14: a group $\Gamma^+_h$ is determined by the
facets of the fundamental domain containing $h$; when that set is large the table lists
its *complement* with an overline (barred rows include five-element sets, so the printed
"greater than five" wording is typographic -- the bars were read individually and agree
with every lattice-database card).

The extreme-ray generators $g_1, \ldots, g_{10}$ form a $\mathbb Z$-basis of
$U + E_8(-1)$ with Gram matrix $W$ (source equation (7), unimodular of signature
$(1,9)$).  The wall normals are the exact dual basis, so through the lattice's own
correlation inverse the owner materializes $\alpha_i$ with
$b(\alpha_i, g_j) = \delta_{ij}$ -- no test-local matrix inversion.

The invariant lattice of the Enriques involution on $L_{K3}$ is the *scaled* model
$M \cong U(2) + E_8(-2)$ of rank 10 and determinant $-1024$ (asserted here against the
application's lattice; never the unimodular unscaled $U + E_8(-1)$).  A polarization is
a vector of $M(1/2) = U + E_8(-1)$, so its square in $M$'s own form is twice the
source's degree.

The representative of each class is $h = \sum_{\text{support}} g_j$, where the
support is decoded from the source's node set: a barred set is the complement of the
generating wall set, an unbarred set is that set itself.  A non-minimal polarization
with the same exact facet set serves the same class -- the listed subset identifies the
class up to conjugacy, so its representative need not lie in the fundamental chamber,
and Table 3 pins exactly the fundamental-chamber cases (asserted below for the eleven
minimal ones).

The public group is ``coinvariant_extension_subgroup``: $O(M,h)$ through the invariant
lattice's own orthogonal group, its image under $\pi_M$, the transport across the
actual discriminant glue, and the exact preimage in $O(N)$.

An exact subgroup boundary is retained, not resolved: the table's counts are orbits of
$\Gamma^+_h = \Gamma_h \cap O^+(N)$, while the public method returns the full preimage
$\Gamma_h$ in $O(N)$.  Equality of the line, plane and flag counts between the two is a
separate statement being settled in research #748, whose flag part currently has a gap
(a totally isotropic plane contains infinitely many lines and the displayed
$\operatorname{diag}(1,-1)$ witness fixes only two).  The line and plane stabilizer
witnesses are distinct from that missing flag proof.  No equality is inferred from the
table.
"""

from sage_extensions.all import *  # noqa: F401,F403
import pytest

# The Gram matrix W = (g_i . g_j) of the ten extreme-ray generators, DSH equation (7).
_DSH_W_ROWS = (
    (0, 1, 2, 2, 3, 3, 4, 4, 5, 6),
    (1, 2, 4, 4, 6, 6, 8, 8, 10, 12),
    (2, 4, 4, 6, 7, 8, 9, 10, 12, 14),
    (2, 4, 6, 6, 9, 9, 12, 12, 15, 18),
    (3, 6, 7, 9, 10, 12, 14, 15, 18, 21),
    (3, 6, 8, 9, 12, 12, 16, 16, 20, 24),
    (4, 8, 9, 12, 14, 16, 18, 20, 24, 28),
    (4, 8, 10, 12, 15, 16, 20, 20, 25, 30),
    (5, 10, 12, 15, 18, 20, 24, 25, 30, 36),
    (6, 12, 14, 18, 21, 24, 28, 30, 36, 42),
)

_WALL_INDICES = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

# The source's node labels for the ten wall/g-basis indices, fixed against Table 3:
# case 1 {0} -> g_2, case 3 {7} -> g_3, case 4 {1} -> g_4, case 7 {8} -> g_5,
# case 8 {2} -> g_6, case 11 {6} -> g_7, case 14 {3} -> g_8, case 20 {4} -> g_9,
# and case 5 {-1,7} -> g_1 + g_3, leaving node 5 -> g_10.
_NODE_TO_WALL = {-1: 1, 0: 2, 1: 4, 2: 6, 3: 8, 4: 9, 5: 10, 6: 7, 7: 3, 8: 5}

# The eleven classes whose Table 3 representative is the fundamental-chamber one:
# (case, support, source degree) -- an independent check of the decode.
_TABLE_3_MINIMAL = (
    (1, (2,), 2),
    (2, (1, 2), 4),
    (3, (3,), 4),
    (4, (4,), 6),
    (5, (1, 3), 8),
    (7, (5,), 10),
    (8, (6,), 12),
    (9, (2, 3), 14),
    (11, (7,), 18),
    (14, (8,), 20),
    (20, (9,), 30),
)

# (case, source node set, barred, lines, planes, flags) -- the primary source datum.
_CASES = (
    (1, (0,), True, 5, 9, 18),
    (2, (-1,0,), True, 7, 13, 28),
    (3, (7,), True, 5, 10, 19),
    (4, (1,), True, 6, 14, 28),
    (5, (-1,7,), True, 9, 23, 49),
    (6, (0,1,), True, 9, 23, 51),
    (7, (8,), True, 6, 13, 28),
    (8, (2,), True, 8, 22, 47),
    (9, (0,7,), True, 11, 34, 77),
    (10, (7,8,), True, 11, 31, 74),
    (11, (6,), True, 8, 22, 49),
    (12, (1,2,), True, 12, 38, 89),
    (13, (-1,0,7,), True, 15, 48, 116),
    (14, (3,), True, 10, 34, 76),
    (15, (-1,0,1,), True, 12, 32, 76),
    (16, (1,7,), True, 13, 49, 113),
    (17, (0,8,), True, 14, 51, 125),
    (18, (0,2,), True, 13, 46, 108),
    (19, (2,7,), True, 16, 67, 162),
    (20, (4,), True, 11, 41, 96),
    (21, (0,1,7,), True, 19, 83, 204),
    (22, (-1,0,8,), True, 19, 74, 191),
    (23, (0,1,2,), True, 17, 64, 159),
    (24, (5,8,), True, 16, 68, 171),
    (25, (5,7,), True, 18, 85, 213),
    (26, (0,3,), True, 18, 87, 213),
    (27, (3,8,), True, 19, 91, 233),
    (28, (5,), True, 12, 49, 115),
    (29, (1,2,7,), True, 24, 124, 320),
    (30, (3,7,), True, 18, 85, 208),
    (31, (0,1,8,), True, 24, 122, 322),
    (32, (2,8,), True, 18, 85, 215),
    (33, (-1,5,), True, 21, 115, 294),
    (34, (-1,0,1,7,), True, 25, 118, 305),
    (35, (2,6,), True, 23, 136, 351),
    (36, (0,2,7,), True, 26, 151, 388),
    (37, (2,3,7,), True, 29, 179, 466),
    (38, (1,2,8,), True, 28, 167, 448),
    (39, (0,2,8,), True, 31, 207, 553),
    (40, (-1,0,1,8,), True, 32, 181, 495),
    (41, (2,7,8,), True, 31, 200, 540),
    (42, (1,4,), True, 24, 149, 389),
    (43, (0,1,2,7,), True, 34, 219, 585),
    (44, (0,5,), True, 27, 187, 487),
    (45, (-1,0,1,2,), True, 22, 92, 238),
    (46, (0,3,7,), True, 33, 239, 629),
    (47, (0,5,8,), True, 36, 274, 746),
    (48, (0,1,2,8,), True, 41, 307, 849),
    (49, (1,5,), True, 30, 231, 608),
    (50, (1,2,3,7,), True, 44, 354, 967),
    (51, (2,6,8,), True, 38, 306, 832),
    (52, (0,5,7,), True, 40, 342, 927),
    (53, (1,2,7,8,), True, 48, 413, 1159),
    (54, (0,1,5,), True, 45, 429, 1175),
    (55, (0,1,3,7,), True, 48, 435, 1184),
    (56, (2,3,7,8,), True, 51, 463, 1298),
    (57, (1,5,8,), True, 40, 341, 937),
    (58, (0,5,7,8,), True, 53, 512, 1433),
    (59, (-1,0,1,2,8,), True, 54, 465, 1315),
    (60, (-1,0,1,2,7,), True, 44, 325, 890),
    (61, (1,2,5,), True, 48, 484, 1339),
    (62, (0,1,5,8,), True, 60, 649, 1832),
    (63, (0,1,2,7,8,), True, 70, 782, 2235),
    (64, (0,1,2,3,7,), True, 63, 653, 1825),
    (65, (0,2,5,), True, 54, 611, 1685),
    (66, (0,1,5,7,), True, 67, 814, 2291),
    (67, (1,2,3,7,8,), True, 80, 1002, 2884),
    (68, (0,1,2,5,), True, 72, 929, 2637),
    (69, (0,1,5,7,8,), True, 89, 1252, 3599),
    (70, (1,2,5,8,), True, 64, 737, 2097),
    (71, (0,2,5,7,), True, 81, 1174, 3323),
    (72, (4,6,3,5,), False, 92, 1210, 3503),
    (73, (0,1,2,5,8,), True, 96, 1440, 4166),
    (74, (0,1,2,5,7,), True, 108, 1818, 5251),
    (75, (4,6,-1,5,), False, 118, 1953, 5690),
    (76, (4,6,8,5,), False, 82, 996, 2829),
    (77, (4,6,3,7,), False, 128, 2263, 6625),
    (78, (0,1,3,5,7,), True, 122, 2306, 6647),
    (79, (4,6,-1,3,), False, 144, 2856, 8357),
    (80, (4,6,-1,2,), False, 163, 3626, 10599),
    (81, (4,6,5,), False, 156, 3074, 9031),
    (82, (4,6,3,), False, 192, 4532, 13369),
    (83, (4,6,-1,), False, 218, 5766, 17003),
    (84, (4,3,), False, 256, 7242, 21471),
    (85, (4,6,), False, 292, 9246, 27411),
    (86, (4,), False, 392, 14926, 44387),
    (87, (), False, 528, 24242, 72199),
)



def _doubled_invariant_model():
    r"""$M$'s doubled $g$-basis model: the form $2W$, determinant $-1024$."""
    return Lattices(ZZ)([list(2 * entry for entry in row) for row in _DSH_W_ROWS])


def _decode_support(case):
    r"""Return the $g$-basis support decoded from the case's source node set."""
    _number, nodes, barred, *_rest = case
    walls = tuple(_NODE_TO_WALL[node] for node in nodes)
    if barred:
        return tuple(sorted(walls))
    return tuple(wall for wall in _WALL_INDICES if wall not in walls)


def _wall_normals():
    r"""Return the materialized wall normals through the owner's correlation inverse.

    The dual basis is the set of functionals $b(\alpha_i, \cdot) = g_i^*$, so the
    inverse correlation raises $g_i^*$ to the lattice element with
    $b(\alpha_i, g_j) = \delta_{ij}$; nothing here inverts a matrix by hand.
    """
    model = Lattices(ZZ)([list(row) for row in _DSH_W_ROWS])
    inverse = model.correlation().inverse()
    return model, tuple(inverse(dual) for dual in model.dual_lattice().module_generators())


def test_the_dsh_fundamental_domain_model_is_the_source_lattice() -> None:
    r"""$W$'s lattice is unimodular of signature $(1,9)$: $U + E_8(-1)$."""
    model = Lattices(ZZ)([list(row) for row in _DSH_W_ROWS])
    assert model.determinant() == ZZ(-1)
    signature = model.signature_pair()
    assert signature.first() == cardinal(1)
    assert signature.second() == cardinal(9)


def test_the_doubled_model_matches_the_invariant_lattice() -> None:
    r"""The doubled $g$-model has the scaled invariant lattice's invariants."""
    model = _doubled_invariant_model()
    assert model.determinant() == ZZ(-1024)
    signature = model.signature_pair()
    assert signature.first() == cardinal(1)
    assert signature.second() == cardinal(9)
    invariant = Involutions.I_En.invariant_lattice()
    assert invariant.module_rank() == cardinal(10)
    assert invariant.determinant() == ZZ(-1024)


def test_the_anti_invariant_lattice_is_the_029j_card_lattice() -> None:
    r"""$N = T_{\mathrm{En}}$: rank 12, determinant 1024, signature $(2,10)$."""
    anti_invariant = Involutions.I_En.formed_coinvariants()
    assert anti_invariant.module_rank() == cardinal(12)
    assert anti_invariant.determinant() == ZZ(1024)
    signature = anti_invariant.signature_pair()
    assert signature.first() == cardinal(2)
    assert signature.second() == cardinal(10)


def test_every_class_representative_vanishes_exactly_on_its_source_wall_set() -> None:
    r"""All 87 classes, paired through the lattice's own form against the dual basis.

    The vanishing of $b(\alpha_i, h)$ is computed on materialized wall normals, so the
    check does not recompute the decode's arithmetic: it compares the lattice pairing
    with the source's generating set (barred rows: the complement of the listed nodes;
    unbarred rows: the listed nodes), and requires the representative to be
    non-isotropic -- the source's two excluded degenerate subsets never occur.
    """
    model, normals = _wall_normals()
    labels = tuple(model.module_generating_set())
    for case in _CASES:
        number, nodes, barred, _lines, _planes, _flags = case
        support = _decode_support(case)
        h = sum(
            (model.module_generator(labels[index - 1]) for index in support),
            model.zero(),
        )
        assert h.q() > ZZ(0), f"case {number}: the decoded representative is isotropic"
        source_walls = tuple(_NODE_TO_WALL[node] for node in nodes)
        generating = (
            tuple(wall for wall in _WALL_INDICES if wall not in source_walls)
            if barred
            else source_walls
        )
        for index, normal in enumerate(normals, start=1):
            pairing = model.b(normal, h)
            if index in generating:
                assert pairing == ZZ(0), (
                    f"case {number}: wall {index} is a source generator but pairs to {pairing}"
                )
            else:
                assert pairing != ZZ(0), (
                    f"case {number}: wall {index} is not a source generator yet vanishes"
                )


def test_the_table_3_minimal_representatives_are_the_decoded_ones() -> None:
    r"""The eleven fundamental-chamber cases match Table 3's representative and degree.

    This is the independent anchor for the decode: Table 3 lists the minimal
    representative in the fundamental chamber, so for those cases the decoded support
    must be exactly that representative's support and $h^2$ must be the source's degree
    (in $M(1/2)$'s own normalization).
    """
    model = Lattices(ZZ)([list(row) for row in _DSH_W_ROWS])
    labels = tuple(model.module_generating_set())
    for number, expected_support, expected_degree in _TABLE_3_MINIMAL:
        case = next(entry for entry in _CASES if entry[0] == number)
        assert _decode_support(case) == expected_support, (
            f"case {number}: the decode gives {_decode_support(case)}, Table 3 gives "
            f"{expected_support}"
        )
        h = sum(
            (model.module_generator(labels[index - 1]) for index in expected_support),
            model.zero(),
        )
        assert h.q() == ZZ(expected_degree), (
            f"case {number}: squared norm {h.q()} is not Table 3's degree {expected_degree}"
        )


def _case_group(case):
    r"""Return the public Gamma_h preimage subgroup of the case's representative."""
    model = _doubled_invariant_model()
    invariant = Involutions.I_En.invariant_lattice()
    transport = model.isometry_to(invariant)
    labels = tuple(model.module_generating_set())
    h = sum(
        (model.module_generator(labels[index - 1]) for index in _decode_support(case)),
        model.zero(),
    )
    h_M = transport(h)
    assert h_M.q() == h.q(), f"case {case[0]}: the transport changed the square"
    return Involutions.I_En.polarized(invariant.inclusion()(h_M)).coinvariant_extension_subgroup()


@pytest.mark.parametrize("case", _CASES, ids=lambda case: f"case-{case[0]}")
def test_the_source_line_row_is_the_public_line_orbit_count(case) -> None:
    r"""The case's cited line-orbit row, compared with the public orbit count."""
    number, _nodes, _barred, lines, _planes, _flags = case
    group = _case_group(case)
    assert group.isotropic_orbit_representatives(1).cardinality() == cardinal(lines), (
        f"case {number}: the public line orbits differ from the cited row"
    )


@pytest.mark.parametrize("case", _CASES, ids=lambda case: f"case-{case[0]}")
def test_the_source_plane_row_is_the_public_plane_orbit_count(case) -> None:
    r"""The case's cited plane-orbit row, compared with the public orbit count."""
    number, _nodes, _barred, _lines, planes, _flags = case
    group = _case_group(case)
    assert group.isotropic_orbit_representatives(2).cardinality() == cardinal(planes), (
        f"case {number}: the public plane orbits differ from the cited row"
    )


@pytest.mark.parametrize("case", _CASES, ids=lambda case: f"case-{case[0]}")
def test_the_source_flag_row_is_the_public_flag_orbit_count(case) -> None:
    r"""The case's cited flag-orbit row, compared with the public flag orbit count.

    The full-preimage versus positive-half flag equality is not established
    (research #748's flag argument has a gap), so a difference here is a result about
    that boundary, not an assertion to relax.
    """
    number, _nodes, _barred, _lines, _planes, flags = case
    group = _case_group(case)
    assert group.isotropic_orbit_representatives(2, flag=True).cardinality() == cardinal(
        flags
    ), f"case {number}: the public flag orbits differ from the cited row"
