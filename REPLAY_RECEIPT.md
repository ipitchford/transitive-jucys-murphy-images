# Replay receipt (0.1.0-candidate, 24 November 2026)

**Environment.** macOS arm64; CPython 3.12.11 (uv-managed, `uv run --no-project --python 3.12 python`; the version was
printed inside the run with `sys.version`). Standard library only. Each run used a fresh copy of the approved
candidate, cwd = its package root, `PYTHONDONTWRITEBYTECODE=1`.

| Run | Command | Exit | Output vs `results/verification.json` |
|---|---|---|---|
| verifier, plain (19 s) | `python -I -B code/verify_transitive.py --output new.json` | 0 | PASS A–H, ALL CHECKS PASSED; JSON equal apart from the "python" field (3.12.11 vs 3.14.7), byte-identical otherwise |
| verifier, -O (19 s) | `python -O -I -B code/verify_transitive.py --output new.json` | 0 | same; byte-identical to the plain run |

**Negative control (under -O).** `EXPECTED_IMAGE_INDEX_IN_L` entry for n = 6 changed from 2 to 1 (the index stated in
Theorem 6.3(ii)): checks A–G pass, then "FAIL: index of image in L_n differs from Theorem 6.3 at n=6", exit 1. During
the internal audit two further controls (altered n = 3 matrix; truncated closure loop) also made the script exit 1.

**After the replay** only the title-page DOI line of `manuscript.tex`, the rebuilt PDF (three pdflatex passes, 10
pages; a word-level text comparison with the approved PDF shows only the DOI line, with reflowed line and page breaks)
and the release records changed; the code and recorded output are byte-identical to the replayed candidate.

**Cross-platform policy** (declared before tagging; see ENVIRONMENT.txt): the new JSON must equal the recorded one
exactly after removing the top-level "python" field. The GitHub Actions workflow `.github/workflows/replay.yml` checks
the manifest, reruns the verifier under `python -O` on Linux, compares under this policy and runs the negative control
(one blocking job; about 20 s of computation).

**Scope.** The computation is Theorem 6.3 (integral image, n ≤ 7) and checks of the proofs of Sections 2–5 in small
cases. The proofs carry the general theorems.
