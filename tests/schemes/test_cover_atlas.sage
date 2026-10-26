r"""Distinguished open covers of the affine line."""

from sage_extensions.all import *


def test_intersections_of_distinguished_opens_of_the_line_are_distinguished_by_the_product() -> None:
    r"""On \(\mathbf A^1_{\mathbf Q}\), \(D(f)\cap D(g) = D(fg)\), independently of the order of the factors; the opens
    \(D(x), D(1-x), D(2-x)\) cover the line since \(x + (1-x) = 1\).

    Source: Hartshorne, *Algebraic Geometry*, II.2 (distinguished opens); Stacks Project, Tag 01HR.
    """
    R = QQ["x"]
    x = R.gen()
    line = Schemes(QQ)(R)
    cover = line.distinguished_open_cover(x, 1 - x, 2 - x)

    assert cover.intersection(0, 1).distinguished_open_element() == x * (1 - x)
    assert cover.intersection(1, 0).distinguished_open_element() == x * (1 - x)
    assert cover.intersection(0, 1, 2).distinguished_open_element() == x * (1 - x) * (2 - x)
    assert R.ideal(x, 1 - x, 2 - x) == R.ideal(R.one())


def test_finite_atlas_sheaf_arrows_preserve_descent_identity_and_zero() -> None:
    r"""The chartwise comparison from sheaf morphisms to descent morphisms
    preserves the two distinct endomorphisms zero and identity and their
    compositions on the standard affine atlas of projective space.
    """
    atlas = ProjectiveSpaces(QQ)(1).standard_affine_atlas()
    datum = atlas.structure_module_datum()
    sheaf = datum.sheaf()
    hom = QuasiCoherentSheaves(sheaf.scheme()).Mor(sheaf, sheaf)
    zero = hom({
        index: datum.local_module(index).module_category().Mor(
            datum.local_module(index), datum.local_module(index)
        ).zero()
        for index in datum.chart_indices()
    })
    identity = hom.identity()
    assert zero != identity
    assert zero * identity == zero
    assert identity * zero == zero
    assert (identity * zero).descent_morphism() == (
        identity.descent_morphism() * zero.descent_morphism()
    )

    doubling = hom({
        index: datum.local_module(index).module_category().Mor(
            datum.local_module(index), datum.local_module(index)
        )({label: datum.local_module(index).scalar_multiple(
            QQ(2), datum.local_module(index).module_generator(label)
        ) for label in datum.local_module(index).module_generating_set()})
        for index in datum.chart_indices()
    })
    assert doubling != identity and doubling != zero
    assert doubling * identity == doubling
    assert identity * doubling == doubling
    assert (doubling * doubling).descent_morphism() == (
        doubling.descent_morphism() * doubling.descent_morphism()
    )

    tensor_datum = datum.tensor_product(datum)
    tensor_sheaf = tensor_datum.sheaf()
    sheaves = QuasiCoherentSheaves(sheaf.scheme())
    forward = sheaves.Mor(sheaf, tensor_sheaf)({
        index: datum.local_module(index).module_category().Mor(
            datum.local_module(index), tensor_datum.local_module(index)
        ).zero()
        for index in datum.chart_indices()
    })
    backward = sheaves.Mor(tensor_sheaf, sheaf)({
        index: datum.local_module(index).module_category().Mor(
            tensor_datum.local_module(index), datum.local_module(index)
        ).zero()
        for index in datum.chart_indices()
    })
    assert forward.domain() is sheaf and forward.codomain() is tensor_sheaf
    assert backward.domain() is tensor_sheaf and backward.codomain() is sheaf
    assert backward * forward == zero
    assert (backward * forward).descent_morphism() == (
        backward.descent_morphism() * forward.descent_morphism()
    )
