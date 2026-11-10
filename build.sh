#!/bin/sh
# Recompute every result, figure and table of the paper from the released calls and checkpoints (CPU, minutes).
# Not repeated here: the LLM calls (run_claude_code.py, run_openai.py), Adam training (adam.py train) and the
# MedSigLIP embeddings (medsiglip.py, needs the gated model); their outputs are in runs/, checkpoints/, results/.
set -e
cd "$(dirname "$0")"
for r in runs/opus1 runs/opus2 runs/opus3 runs/astra1 runs/astra2 runs/astra3; do python3 evaluate.py $r; done
python3 adam.py eval
python3 score_subset.py
python3 evidence_maps.py
python3 uterus_probe.py
python3 agreement.py
python3 figures.py
python3 make_tables.py
