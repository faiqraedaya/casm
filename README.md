<p align="center"><img src="src/casm/gui/assets/casm.svg" alt="CASM logo" width="96"></p>

# CASM

## Overview
*CASM (Consequence Analysis Surrogate Model) samples release scenarios, prepares them for Phast/Safeti, and trains a neural network on the results. The trained model predicts release consequences in milliseconds anywhere inside the sampled range, for screening, sensitivity studies or filling gaps in a QRA dataset.*

## Features
CASM handles every step except the Phast run itself, through a desktop application or a command line.
- Space-filling scenario design (Latin hypercube, Sobol, Halton or random) within per-material temperature and pressure envelopes
- Pure components and mixtures, with a starting catalogue of thirteen materials
- Export of cases into a copy of the Safeti input template that Phast can import
- Import of Phast results workbooks, with failed scenarios reported and dropped
- One multi-output network across all materials and consequences, split by vessel for testing
- Single-point or batch CSV prediction with optional Monte Carlo dropout uncertainty
- Domain warnings for inputs outside the training envelope

## Install
```bash
git clone https://github.com/faiqraedaya/casm
cd casm
uv sync
```

## Usage
```bash
uv run casm gui
```
The window opens on a home page, then works through five stages in order: Project, Sample, Phast, Train and Predict. From the command line, the same steps are `uv run casm init`, `sample --vessels 500`, `export`, then `import path/to/results.xlsx` once Phast has run, and `train`. Then predict a point with `uv run casm predict --temperature 25 --pressure 60 --orifice 25 --material METHANE`. The Safeti input template is not in the repository: copy it to `templates/Safeti Template Input Sheet.xlsx` or set `phast.template` in `casm.json`.

## Technical details
A project directory (default `./workspace`) holds `casm.json` with all settings. Sampling covers temperature, pressure and orifice diameter, with log-spaced pressure and hole size, one design per material and stratified hole sizes per vessel. Every vessel name carries a design ID. Cases are written to `cases/cases.csv` and patched directly into the template's worksheet XML in `phast/input/*.xlsx`, so the rest of the workbook stays byte-identical. Columns are addressed by Safeti attribute code, and values are converted to the template's units.

The Phast results workbook's Discharge, Flammable Dispersion, Jet fire, Explosions and pool fire sheets are joined on path, scenario and weather. They are then merged back onto the cases into `datasets/training_data.csv`. Training uses a TensorFlow/Keras multi-output MLP with a shared trunk, per-target heads, LayerNorm and swish activation. Targets are log10(y + c), and missing targets are masked out of the loss. Physically grouped features include the choked-flow group P·A/√T and reduced temperature and pressure. Release rate, release velocity, distance to LFL and jet flame length are trained by default, from about twenty extracted quantities.

Each run writes `models/run_<stamp>/` with the model, scalers, metadata, metrics and history, and `models/registry.json` records the current run. Predictions print to the console or are written to a CSV with one column per consequence and a `domain_warnings` column. [TECHNICAL.md](TECHNICAL.md) explains the design choices in detail.

## License
MIT — see [LICENSE](LICENSE).
