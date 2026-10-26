r"""Abbreviations the expectation files use for subcategories of varieties.

Each name is the category expression it abbreviates; the preamble presents
only the expression.  ``install()`` binds the names as builtins, so a test
module that star-imports the session also resolves them.
"""

import builtins

from sage_extensions.all import Curves, ProjectiveCompleteIntersections, Surfaces


def ProjectiveCurves(base):
    r"""Integral projective curves over ``base``: ``Curves(base).Projective()``."""
    return Curves(base).Projective()


def ProperSurfaces(base):
    r"""Proper integral surfaces over ``base``: ``Surfaces(base).Proper()``."""
    return Surfaces(base).Proper()


def ProjectiveSurfaces(base):
    r"""Projective integral surfaces over ``base``: ``Surfaces(base).Projective()``."""
    return Surfaces(base).Projective()


def DelPezzoSurfaces(base):
    r"""Smooth del Pezzo surfaces over ``base``: ``Surfaces(base).DelPezzo()``."""
    return Surfaces(base).DelPezzo()


def SmoothQuarticK3CompleteIntersections(base):
    r"""Smooth complete intersections that are K3: ``ProjectiveCompleteIntersections(base).Smooth().K3()``."""
    return ProjectiveCompleteIntersections(base).Smooth().K3()


def install() -> None:
    r"""Bind each abbreviation as a builtin."""
    for abbreviation in (
        ProjectiveCurves,
        ProperSurfaces,
        ProjectiveSurfaces,
        DelPezzoSurfaces,
        SmoothQuarticK3CompleteIntersections,
    ):
        setattr(builtins, abbreviation.__name__, abbreviation)
