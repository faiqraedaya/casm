# CASM

Consequence Analysis Surrogate Model. CASM trains a neural network on Phast/Safeti results and
uses it to predict release consequences in milliseconds.

You run Phast once on a sampled set of scenarios. After that, any point inside the sampled range
can be answered without the solver: for screening, sensitivity studies or filling gaps in a QRA
dataset.

```
sample  ──▶  export  ──▶  [ Phast ]  ──▶  import  ──▶  train  ──▶  predict
 design      workbook      you run it      dataset     model      app / CLI / CSV
```

CASM handles every step except the Phast run: you import the input workbook into Phast, run the
study, and export the results workbook.

## Contents

- [Requirements](#requirements)
- [Install](#install)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Predicting](#predicting)
- [Project directory](#project-directory)
- [Configuration](#configuration)
- [Limitations](#limitations)
- [Tests](#tests)
- [Further reading](#further-reading)

## Requirements

- Python 3.10 or later, managed with [uv](https://docs.astral.sh/uv/)
- Phast or Safeti, to run the sampled study
- The Safeti input template workbook (not included; see below)

## Install

```bash
git clone https://github.com/faiqraedaya/casm
cd casm
uv sync
```

The Safeti input template is a client workbook, so it is not in the repository. Either copy it to
`templates/Safeti Template Input Sheet.xlsx`, or set `phast.template` in the project's
`casm.json`.

## Quick start

Desktop application:

```bash
uv run casm gui
```

The window has five stages, worked in order: Project, Sample, Phast, Train, Predict. Each stage
shows its inputs and outputs, and a stage is locked until the one before it has finished.

Command line:

```bash
uv run casm init                         # create ./workspace with a default config
uv run casm sample --vessels 500         # -> cases/cases.csv
uv run casm export                       # -> phast/input/*.xlsx

# Import the workbook into Phast, run the study, export the results workbook.

uv run casm import path/to/results.xlsx  # -> datasets/training_data.csv
uv run casm train                        # -> models/run_<stamp>/
uv run casm predict --temperature 25 --pressure 60 --orifice 25 --material METHANE
```

Every command accepts `--project/-p <dir>`. The default is `./workspace` in the current
directory. `uv run casm info` summarises a project's cases, dataset and trained runs.

## Workflow

| Command | Input | Output | What it does |
| --- | --- | --- | --- |
| `sample` | `casm.json` | `cases/cases.csv` | Space-filling design per material (Latin hypercube by default) over temperature and pressure, within that material's envelope, with stratified hole sizes. Vessel names carry a design ID, so separate designs never collide. |
| `export` | cases, template | `phast/input/*.xlsx` | Writes the cases into a copy of the Safeti template, ready for Phast to import. |
| `import` | Phast results workbook | `datasets/training_data.csv` | Joins results back to their cases. Scenarios that failed to converge are reported and dropped, never scored as zero. |
| `train` | dataset | `models/run_<stamp>/` | Fits one network across all materials and consequences. The train/test split is by vessel, so the score measures performance on unseen equipment. |
| `predict` | a point or a CSV | printed values or a CSV | Predicts consequences and flags inputs outside the training envelope. |

Options per command: `uv run casm <command> --help`.

### Consequences

Four are trained by default:

| Target | Column |
| --- | --- |
| Release rate | `Release_rate` |
| Release velocity | `Velocity` |
| Distance to LFL | `Distance_to_LFL` |
| Jet flame length | `Flame_length` |

About twenty are extracted from the results workbook. To train others, add them to
`training.targets` in `casm.json`.

## Predicting

Single point:

```bash
uv run casm predict --temperature 25 --pressure 60 --orifice 25 --material METHANE --mc 50
```

| Option | Unit | Default |
| --- | --- | --- |
| `--temperature` | °C | required |
| `--pressure` | barg | required |
| `--orifice` | mm | required |
| `--material` | name as trained | none |
| `--elevation` | m | none |
| `--inventory` | kg | none |
| `--wind` | m/s | 5 |
| `--stability` | Pasquill index, A = 1 to F = 6 | 4 (D) |
| `--mc` | Monte Carlo dropout samples; gives a ± spread | 0 (off) |
| `--run` | run directory | latest run |

Batch:

```bash
uv run casm predict --csv inputs.csv --out results.csv
```

The CSV columns are `temperature_degC`, `pressure_barg`, `orifice_mm`, `wind_speed_ms`,
`stability_index`, and optionally `material`, `elevation_m` and `mass_inventory_kg`. The output
adds one column per consequence and a `domain_warnings` column.

Materials:

- A material the model was trained on is looked up by name, with the same property descriptors
  used in training.
- A new material needs its descriptors as `mat_*` columns. Without them CASM refuses the
  prediction, so it never returns an answer for an averaged fluid.

## Project directory

```
workspace/
├── casm.json                  # project configuration
├── cases/cases.csv            # sampling design, one row per leak scenario
├── phast/input/*.xlsx         # workbooks to import into Phast
├── phast/output/*.xlsx        # Phast results workbooks go here
├── datasets/training_data.csv # results joined to cases
├── models/run_<stamp>/        # model.keras, scalers, meta.json, metrics, history
├── models/registry.json       # records the current run
└── plots/                     # design and diagnostic plots
```

Projects created before the rename have `nncm.json`. CASM renames it to `casm.json` when the
project is opened.

## Configuration

`casm.json` holds all project settings. The Project stage in the app edits the same file.

| Section | Contents |
| --- | --- |
| `sampling` | Vessel and leak counts, sampler and seed, input ranges, materials and their envelopes |
| `phast` | Template path, per-column defaults for vessels and leaks |
| `extraction` | Weather filter, required targets, rules for dropping failed cases |
| `training` | Targets, log-transformed targets, hyperparameters |

### Materials

A material is a pure component or a mixture. In the app, double-click a row of the Materials
table to edit it. Component names must match the Phast property system exactly, for example
`NITROGEN (ASPHYXIATING)`, not `NITROGEN`.

A new project starts with thirteen materials, each with its typical storage temperature and
pressure envelope:

| Type | Materials |
| --- | --- |
| Pure | Methane, ethane, propane, n-butane, ammonia, CO2, hydrogen |
| Process streams | Natural gas, LNG, LPG, sour feed gas, NGL, stabilised condensate |

The stream compositions are representative. Replace them with the stream data for the plant you
are modelling.

## Limitations

- A model is valid only inside the envelope it was trained on. Predictions outside it carry a
  domain warning; treat them as extrapolation.
- Settings held constant across the training study (template parameter sets, fixed vessel and
  leak defaults) cannot vary at prediction time. `predict` prints them after every result.
- The surrogate approximates Phast. It does not replace a Phast run for results that will be
  relied on in a safety case. Check the per-target R² and median percentage error in the run
  metrics before using a model.

## Tests

```bash
uv run --extra dev pytest -q
```

Workbook tests are skipped unless the template is present.

## Further reading

[TECHNICAL.md](TECHNICAL.md) explains the design choices behind each stage: the sampling design,
the mixture format, why the workbook is patched in place instead of re-saved, how results are
matched to cases, and what the model fits. Read it when a result looks wrong or before relying
on a number.

## Licence

MIT. See [LICENSE](LICENSE).
