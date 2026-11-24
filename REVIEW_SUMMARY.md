# Review summary (public, 0.1.0-candidate)

This records the internal review of the candidate: who looked, what they raised, and what was done. It is
AI-assisted internal review, not peer review or independent reproduction.

## What ran

1. **Panel (round 1).** Five Claude reviewer roles, editor, methodology (line-by-line proof check), domain
   (literature, attribution and novelty), perspective (readability and significance) and devil's advocate, run as one
   combined pass. The panel recomputed the quantitative claims independently. No reviewer found a mathematical error;
   the objections concerned scope, exposition of the foundation, attribution and completeness over the integers.
2. **Revision round** with an extension: the earlier draft also treated a second topic, which was removed from this
   release; the introduction and the definition of the transitive image were rewritten; and the exact integral image
   was computed for n ≤ 7 (Theorem 6.3).
3. **Verification.** A re-review checked every first-round item against the revised text, and a line-by-line proof
   audit checked Sections 2–6, together with a prose-against-code audit, a replay and negative controls. Every proof
   was found correct. The one MAJOR item was in the code: the integral-image check computed the numbers of Theorem 6.3
   without comparing them with the stated values. Expected-value tables were added, and a negative control (changing a
   stated index) now makes the script fail, also under `python -O`. Minor wording items were applied.

No second-model (Astra/Codex) adversarial review took place for this release.

## Sources

The cited works were read: Campion Loth and Rattan (arXiv v2 of the BLMS paper; Theorems 1, 2, 6, Questions 12 and 13,
Section 1.3), Goulden and Jackson (Section 1.1), Féray (partial Jucys–Murphy elements) and Murray (Introduction). The
primary sources of the integral Jucys–Murphy theorem, Jucys (1974) and Murphy (1983), were read in full: Murphy's
Theorem 1.9 (the centre of K S_n is the ring of symmetric polynomials in the Jucys–Murphy elements over every integral
domain K) and Jucys's equation (8) with the Farahat–Higman generators. Coulter, Do and Moskovsky is cited only as a
pointer in a remark that makes no claims.

## Main objections and dispositions

| Objection | Disposition |
|---|---|
| Correctness | No error was found in round 1, in the re-review or in the proof audit. |
| Title, abstract and introduction described material outside this release | Rewritten for the present scope; the other material is mentioned only in a one-paragraph remark with no claims (Section 8). |
| Well-definedness of the transitive image rested on a two-line argument with undefined terms | Words, orbit partitions and ordered monomials are defined (Section 2, Definition 2.2); Lemma 2.3 proves the Möbius formula for every expression and deduces independence and linearity; Lemma 2.1 proves the Möbius values. |
| Small missing justifications (unitriangular diagonal, base change from the integers, action through augmentations) | Added (Lemma 3.1, Section 2, proof of Theorem 4.1). |
| Statement of the optimal degree | Theorem 4.1 states both the upper bound and the vanishing of identity coefficients below 2n−2. |
| Integral Jucys–Murphy theorem cited only to a secondary source | Cited directly to Murphy (Theorem 1.9) and Jucys (Sections 2–3, equation (8)); Murray and CLR Theorem 2 kept as secondary references. |
| Féray (2012) and the standard nature of the Möbius device | Féray cited; the method paragraph says inclusion–exclusion goes back to Goulden and Jackson and that Möbius inversion between all and connected objects is standard in Hurwitz theory. |
| The z/h divisibility was a remark; the integral answer was left unstated | Proposition 6.1 with proof; Theorem 6.3 computes the integral image exactly for n ≤ 7. The panel's suggested statement (image = L_n) holds for n ≤ 5 and n = 7 but fails at n = 6 (index 2, explicit congruence). Question 6.4 states what remains open. |
| Readability | Context-first introduction (objects, transitivity, the question, why it is natural, results, method, what is not done, roadmap); every section opens with a sentence saying what it does. |
| Integral-image check did not compare with the stated values | Expected-value tables added; negative control confirmed. |

## Limits that remain

The integral image for n ≥ 8, the explanation of the n = 6 parity condition and closure for all n (Question 6.4), and
closed forms for transitive images of the classical bases (Question 13 of Campion Loth and Rattan). The literature
search is recorded in RESEARCH_GATES.json.
