"""CASM — Consequence Analysis Surrogate Model.

End-to-end pipeline around a consequence-modelling package (Phast/Safeti):

1. :mod:`casm.sampling` builds a space-filling design of vessel/leak scenarios.
2. :mod:`casm.phast.input_writer` writes them into a Phast-importable workbook.
3. :mod:`casm.phast.output_reader` turns Phast's result workbook into a dataset.
4. :mod:`casm.training` fits a multi-output surrogate model.
5. :mod:`casm.predict` / :mod:`casm.gui` serve predictions.

Only the Phast import/export clicks stay manual.
"""

__version__ = "0.2.0"

from .config import CasmConfig, Project  # noqa: F401

__all__ = ["CasmConfig", "Project", "__version__"]
