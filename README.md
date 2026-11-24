# Which central elements are transitive?

*An answer to a question of Campion Loth and Rattan on Jucys–Murphy evaluations*

Every central element is transitive, exactly when (n−1)! is invertible: transitive Jucys–Murphy images fill the
centre of the symmetric group algebra under that condition, with optimal degree 2n−2.

Version 0.1.0-candidate. DOI [10.5281/zenodo.24516957](https://doi.org/10.5281/zenodo.24516957) (all versions:
[10.5281/zenodo.24516956](https://doi.org/10.5281/zenodo.24516956)). Release page:
https://evidencepress.org/releases/transitive-jucys-murphy-images/

**Status: unrefereed research candidate.** Author: Anonymous. Text CC0-1.0; code MIT (see [LICENSE.md](LICENSE.md)).

## What this is about

**The setting.** The symmetric group S_n is the group of all shuffles (permutations) of n objects. Its group algebra
contains formal combinations of shuffles, and its *centre* consists of the combinations that do not depend on how the
objects are labelled. A basis of the centre is given by the class sums K_λ: add up all shuffles with the same cycle
type λ. The Jucys–Murphy elements J_i = (1 i) + (2 i) + ... + (i−1 i) are particular sums of swaps (transpositions).
A classical theorem of Jucys and of Murphy says that plugging them into symmetric polynomials produces exactly the
centre, even with integer coefficients. Expanding such a polynomial gives sums of products of swaps; the number of
times a shuffle appears counts its factorisations into swaps of a prescribed kind. These counts are Hurwitz-type
numbers, which also count branched covers of the sphere.

**Transitivity.** In geometry one often wants only *connected* covers. On the algebra side this means keeping only the
products whose swaps link all n objects together: the *transitive* products. Keeping only those in the expansion of
f(J_1, ..., J_n) gives the *transitive image* T_n(f). Goulden and Jackson (2009) showed that transitive powers are
still central, and Campion Loth and Rattan (2025) showed the same for every symmetric function f. They then asked
(their Question 12) which part of the centre these connected versions produce. It is not obvious, because T_n is
linear but not multiplicative: throwing away the disconnected products might lose information.

**What is new.**
1. **All of it** (Theorem 3.2). Over the complex numbers every central element is the transitive image of a single
   symmetric function, so the answer to Question 12 is the whole centre.
2. **The arithmetic condition** (Theorems 3.2 and 6.2). Over a general commutative ring R, transitive images fill the
   centre exactly when (n−1)! can be divided by in R. Otherwise even products of transitive images fall short: for a
   prime p ≤ n−1, the class of a single p-cycle stays out of reach modulo p.
3. **Optimal degree** (Theorem 4.1). Degree 2n−2 is enough, and it is the minimum: a connected product of swaps that
   returns every object to its start needs at least 2n−2 swaps.
4. **Ordinary and connected together** (Theorem 5.1). The pairs (ordinary evaluation, transitive image) that occur are
   exactly the pairs of central elements whose coefficients at the n-cycles agree.
5. **Over the integers** (Proposition 6.1, Theorem 6.3). A conjugation-orbit argument shows that the coefficient of
   K_λ in a transitive image is divisible by z_λ/h_λ. An exact computer computation shows that this bound describes
   the integral image exactly for n ≤ 5 and n = 7, but not for n = 6, where one extra parity condition appears and the
   image has index 2 in the lattice the bound allows.

For n = 3, with columns K_111, K_21, K_3, the three transitive images built in Section 3 are the rows of

    [  2   0   0 ]
    [ -3  -1   0 ]
    [  1   1   1 ]

The 2 in the corner is the obstruction: (3−1)! = 2, so over a ring where 2 cannot be divided by, no transitive image
has identity coefficient 1.

**The idea.** An inclusion–exclusion (Möbius) formula over the ways to split the n objects into groups writes the
transitive image as an alternating sum of ordinary evaluations on the groups. Multiplying by the sum of all shuffles
inside the groups turns each Jucys–Murphy element into a plain number, its rank inside its group, so suitable
polynomials can read off the group sizes, and a triangular system is inverted.

**Limits.** The paper answers Question 12 as posed. The description over the integers is complete only for n ≤ 7, by
exact computation, and the n = 6 parity condition is not explained conceptually (Question 6.4 asks for the general
answer). Closed forms for transitive images of the classical bases (Question 13 of Campion Loth and Rattan) are not
addressed. This is an unrefereed candidate; its assurance is internal AI-assisted review and exact computational checks.

## Contents

| Path | What |
|---|---|
| `manuscript.pdf`, `manuscript.tex` | The paper (10 pages); Section 1 is a plain introduction with a roadmap |
| `code/verify_transitive.py` | Exact verifier (standard library only): checks A–H of Section 7 |
| `results/verification.json` | Recorded output of the verifier |
| `refs.bib` | Bibliography (seven cited works) |
| `AI_INDEX.md` | Machine-oriented map of claims, evidence and limits |
| `REVIEW_SUMMARY.md` | Public summary of the internal review |
| `RESEARCH_GATES.json` | Prior-art searches, sources read and limitation triage |
| `REPLAY_RECEIPT.md`, `ENVIRONMENT.txt` | Release replay record and environment |
| `requirements.txt` | No third-party dependencies; Python >= 3.10 |
| `CITATION.cff`, `.zenodo.json`, `LICENSE.md` | Citation, archive metadata and licences |
| `.github/workflows/replay.yml` | CI: manifest, verifier under `python -O`, output comparison, negative control |
| `MANIFEST.sha256` | SHA-256 of every file |

## Replay

From the package root, with Python 3.10 or later (no packages needed):

    python3 -O -I -B code/verify_transitive.py --output new-verification.json

Expected: eight lines `PASS A_...` to `PASS H_integral_image`, then `ALL CHECKS PASSED`, exit status 0 (about 20 s).
Every check exits with status 1 on failure, also under `python -O`. All arithmetic is exact (integers and fractions).

**Comparison policy** (declared before tagging; the same in CI, ENVIRONMENT.txt and REPLAY_RECEIPT.md): the new JSON
must equal `results/verification.json` exactly, except the top-level `"python"` field, which records the interpreter
version (the recorded file says 3.14.7; the release replay ran CPython 3.12.11 and CI runs CPython 3.12 on Linux). No
floating-point tolerance is needed.

**Negative control:** changing the n = 6 entry of `EXPECTED_IMAGE_INDEX_IN_L` from 2 to 1 makes the script print
`FAIL: index of image in L_n differs from Theorem 6.3 at n=6` and exit 1 under `python -O`.

## Assurance

Written proofs (Sections 2–6) with exact computational checks (Section 7); Theorem 6.3 is a computation. Internal
AI-assisted review only: a five-role Claude review panel run as one combined pass, the lead's proof audit and exact
verifier with negative controls, one revision round with an extension (the integral image for n ≤ 7), then a
re-review and proof audit of the revised text. The primary sources for the integral Jucys–Murphy theorem, Jucys (1974)
and Murphy (1983), were read in full. No second-model (Astra/Codex) review took place. This is not peer review,
independent reproduction or formal verification. See [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md).

## How to cite

Anonymous (2026). *Which central elements are transitive? An answer to a question of Campion Loth and Rattan on
Jucys–Murphy evaluations*. Version 0.1.0-candidate. Zenodo. https://doi.org/10.5281/zenodo.24516957
