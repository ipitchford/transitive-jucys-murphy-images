#!/usr/bin/env python3
"""Exact checks for "Which central elements are transitive?" (transitive Jucys-Murphy images).

Standard library only; all arithmetic is exact (integers and fractions). Every check
raises CheckFailure on disagreement (no `assert`), so the script also fails under -O.

Checks (section numbers refer to the manuscript):
  A. Word level, n <= 4: the transitive part of the marker polynomial F(x; y) of
     Section 3, computed by expanding transposition words and tracking their orbits,
     equals the Moebius formula of Lemma 2.2 (sum over set partitions of H_pi).
  B. Word level, n <= 4: Lemma 2.2 itself for every monomial J_{i_1}...J_{i_k}, k <= 4,
     and independence of the expansion order.
  C. Section 4: the compressed shape selectors evaluate correctly on every pair of
     integer partitions, n <= 9, and every inclusion-exclusion term has degree <= n - 1.
  D. Class-level engine (characters and contents) agrees with the word-level evaluation
     of T_n(e_mu) for n <= 4 and all mu with |mu| <= 2n - 2.
  E. n = 3 matrix of Section 3.
  F. Section 4 sharpness, n <= 7: no symmetric function of degree < 2n - 2 has a
     transitive image with nonzero identity coefficient, and degree <= 2n - 2 already
     spans the centre over Q.
  G. Section 5, n <= 6: the pair map f -> (E_n(f), T_n(f)) has rank 2p(n) - 1 over Q.
  H. Section 6, n <= N_MAX: the exact integral image T_n(Lambda_Z), certified without a
     degree cut-off by ring closure; its containment in the classwise lattice L_n; its
     index in L_n; the extra congruence at n = 6; and closure of Z.1 + T_n(Lambda_Z)
     under multiplication.
"""
import argparse
import json
import platform
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import permutations
from math import comb, factorial, gcd, prod


class CheckFailure(Exception):
    pass


def require(cond, message):
    if not cond:
        raise CheckFailure(message)


# ---------------------------------------------------------------- combinatorics
def integer_partitions(n, maxpart=None):
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield ()
        return
    for k in range(min(n, maxpart), 0, -1):
        for rest in integer_partitions(n - k, k):
            yield (k,) + rest


def set_partitions(items):
    items = list(items)
    if not items:
        yield []
        return
    head, rest = items[0], items[1:]
    for tail in set_partitions(rest):
        yield [[head]] + tail
        for j in range(len(tail)):
            yield tail[:j] + [[head] + tail[j]] + tail[j + 1:]


def mobius_top(k):
    """Moebius function mu(pi, 1) of the set-partition lattice for a k-block pi."""
    return (-1) ** (k - 1) * factorial(k - 1)


def z_lambda(lam):
    c = Counter(lam)
    return prod(i ** m * factorial(m) for i, m in c.items())


def h_lambda(lam):
    g = 0
    for i, m in Counter(lam).items():
        g = gcd(g, i * m)
    return g


# ---------------------------------------------------------------- word level
def compose(p, q):
    """(p q)(i) = p(q(i)); class coefficients do not depend on this convention."""
    return tuple(p[q[i]] for i in range(len(p)))


def transposition(n, a, b):
    t = list(range(n))
    t[a], t[b] = t[b], t[a]
    return tuple(t)


def canon(labels):
    seen = {}
    return tuple(seen.setdefault(x, len(seen)) for x in labels)


def merge(labels, a, b):
    la, lb = labels[a], labels[b]
    if la == lb:
        return labels
    return canon(tuple(la if x == lb else x for x in labels))


def cycle_type(p):
    n = len(p)
    seen = [False] * n
    out = []
    for i in range(n):
        if not seen[i]:
            c, j = 0, i
            while not seen[j]:
                seen[j] = True
                j = p[j]
                c += 1
            out.append(c)
    return tuple(sorted(out, reverse=True))


def eval_monomial_words(n, letters, block=None):
    """Expand J_{letters[0]} J_{letters[1]} ... (0-based letters) into transposition words.
    With block (a list giving the block of each point), only transpositions inside blocks
    are used (this is J^pi). Returns dict (permutation, orbit labels) -> multiplicity."""
    ident = tuple(range(n))
    states = {(ident, ident): 1}
    for i in letters:
        new = defaultdict(int)
        for (perm, lab), c in states.items():
            for a in range(i):
                if block is not None and block[a] != block[i]:
                    continue
                new[(compose(perm, transposition(n, a, i)), merge(lab, a, i))] += c
        states = new
    return states


def transitive_sum(states):
    out = defaultdict(int)
    for (perm, lab), c in states.items():
        if max(lab) == 0:
            out[perm] += c
    return {k: v for k, v in out.items() if v}


def plain_sum(states):
    out = defaultdict(int)
    for (perm, lab), c in states.items():
        out[perm] += c
    return {k: v for k, v in out.items() if v}


def add_into(acc, d, scale):
    for k, v in d.items():
        acc[k] += scale * v


def block_vector(n, pi):
    b = [0] * n
    for idx, B in enumerate(pi):
        for x in B:
            b[x] = idx
    return b


def check_B_lemma(nmax=4, kmax=4):
    """Lemma 2.2 for all monomials of length <= kmax in J_2..J_n (J_1 = 0), n <= nmax."""
    count = 0
    for n in range(1, nmax + 1):
        letters_all = list(range(1, n))  # 0-based index i stands for J_{i+1}
        parts = list(set_partitions(range(n)))
        blocks = [(block_vector(n, pi), len(pi)) for pi in parts]

        def words(k):
            if k == 0:
                yield ()
                return
            for w in words(k - 1):
                for i in letters_all:
                    yield w + (i,)
        for k in range(0, kmax + 1):
            for w in words(k):
                lhs = transitive_sum(eval_monomial_words(n, w))
                rhs = defaultdict(int)
                for bv, kb in blocks:
                    add_into(rhs, plain_sum(eval_monomial_words(n, w, bv)), mobius_top(kb))
                rhs = {p: v for p, v in rhs.items() if v}
                require(lhs == rhs, f"Lemma 2.2 fails for n={n}, word {w}")
                rev = transitive_sum(eval_monomial_words(n, tuple(reversed(w))))
                require(rev == lhs, f"order dependence for n={n}, word {w}")
                count += 1
    return {"monomials_checked": count, "n_max": nmax, "length_max": kmax}


# ---- check A: the marker construction of Section 3, by direct word evaluation
def multiply_linear(poly, root):
    out = [0] * (len(poly) + 1)
    for k, val in enumerate(poly):
        out[k] -= root * val
        out[k + 1] += val
    return out


def marker_factors(n):
    """Integer polynomials (n-1)! (1+x) L_j(x), j = 0..n-1 (coefficients, ascending)."""
    polys = []
    for j in range(n):
        den = factorial(j) * factorial(n - 1 - j) * (-1) ** (n - 1 - j)
        poly = [factorial(n - 1) // den]
        for point in [-1] + [k for k in range(n) if k != j]:
            poly = multiply_linear(poly, point)
        polys.append(poly)
    return polys


def use_letter(states, high):
    out = defaultdict(int)
    for (perm, comps, marks), value in states.items():
        for low in range(high):
            out[(compose(perm, transposition(len(perm), low, high)),
                 merge(comps, low, high), marks)] += value
    return out


def check_A_marker(nmax=4):
    results = {}
    for n in range(1, nmax + 1):
        polys = marker_factors(n)
        ident = tuple(range(n))
        states = {(ident, ident, (0,) * n): 1}
        for high in range(n):
            updated = defaultdict(int)
            powers = states
            for power in range(n + 1):
                for (perm, comps, marks), value in powers.items():
                    for j, poly in enumerate(polys):
                        if power < len(poly) and poly[power]:
                            m = list(marks)
                            m[j] += 1
                            updated[(perm, comps, tuple(m))] += value * poly[power]
                if power < n:
                    powers = use_letter(powers, high)
            states = {k: v for k, v in updated.items() if v}
        direct = {(p, marks): v for (p, comps, marks), v in states.items() if max(comps) == 0}
        expected = defaultdict(int)
        for pi in set_partitions(range(n)):
            marks = tuple(sum(len(B) > i for B in pi) for i in range(n))
            bv = block_vector(n, pi)
            for perm in permutations(range(n)):
                if all(bv[perm[i]] == bv[i] for i in range(n)):
                    expected[(perm, marks)] += mobius_top(len(pi)) * factorial(n - 1) ** n
        expected = {k: v for k, v in expected.items() if v}
        require(direct == expected, f"marker construction fails at n={n}")
        results[str(n)] = len(direct)
    return {"nonzero_permutation_marker_pairs": results}


# ---- check C: compressed selectors of Section 4
@lru_cache(maxsize=None)
def subset_union_counts(sizes):
    out = []
    for s in range(max(sizes), sum(sizes) + 1):
        cnt = sum((-1) ** (s - j) * comb(s, j) * prod(comb(j, a) for a in sizes)
                  for j in range(s + 1))
        if cnt:
            out.append((s, cnt))
    return tuple(out)


def check_C_selectors(nmax=9):
    pairs = 0
    for n in range(1, nmax + 1):
        shapes = list(integer_partitions(n))
        for beta in shapes:
            ranks = [r for size in beta for r in range(size)]
            feats = {s: sum(comb(r, s - 1) for r in ranks) for s in range(1, n + 1)}
            complement = 1
            for alpha in shapes:
                if alpha == (1,) * n:
                    continue
                total = 0
                for eta in set_partitions(range(len(alpha))):
                    # inclusion-exclusion over set partitions eta of the index set, weight mu(0, eta)
                    weight = prod((-1) ** (len(g) - 1) * factorial(len(g) - 1) for g in eta)
                    term = weight
                    degree = 0
                    for g in eta:
                        counts = subset_union_counts(tuple(alpha[i] for i in g))
                        term *= sum(c * feats[s] for s, c in counts)
                        degree += max(s - 1 for s, c in counts)
                    require(degree <= n - len(eta), f"degree bound fails n={n} alpha={alpha}")
                    total += term
                mult = prod(factorial(m) for m in Counter(alpha).values())
                require(total == mult * (alpha == beta),
                        f"selector value wrong n={n} alpha={alpha} beta={beta}")
                complement -= total // mult
                pairs += 1
            require(complement == (beta == (1,) * n), f"complement selector wrong n={n} beta={beta}")
            pairs += 1
    return {"selector_shape_pairs": pairs, "n_max": nmax}


# ---------------------------------------------------------------- class level
@lru_cache(maxsize=None)
def character(nu, rho):
    """chi^nu(rho) by the Murnaghan-Nakayama rule on beta-sets."""
    if not rho:
        return 1 if sum(nu) == 0 else 0
    r, rest = rho[0], rho[1:]
    L = len(nu)
    beta = [nu[i] + (L - 1 - i) for i in range(L)]
    bset = set(beta)
    total = 0
    for b in beta:
        if b - r >= 0 and (b - r) not in bset:
            sign = (-1) ** sum(1 for c in beta if b - r < c < b)
            nb = sorted([c for c in beta if c != b] + [b - r], reverse=True)
            Ln = len(nb)
            new = tuple(x for x in (nb[i] - (Ln - 1 - i) for i in range(Ln)) if x > 0)
            total += sign * character(new, rest)
    return total


def contents(nu):
    return tuple(sorted(j - i for i, row in enumerate(nu) for j in range(row)))


@lru_cache(maxsize=None)
def block_weights(btype):
    b = sum(btype)
    out = []
    for nu in integer_partitions(b):
        ch = character(nu, btype)
        if ch:
            out.append((contents(nu), Fraction(character(nu, (1,) * b) * ch, factorial(b))))
    return tuple(out)


@lru_cache(maxsize=None)
def class_weights(lam, transitive=True):
    """Return {content multiset: weight} with [sigma] T_n(f) = sum weight * f(multiset)
    for sigma of cycle type lam and every symmetric f (ordinary E_n if transitive=False).
    Uses Lemma 2.2 over set partitions of the cycles of sigma and, on each block, the
    central-character formula [tau] g(J) = (1/b!) sum_nu f^nu chi^nu(tau) g(contents(nu))."""
    cyc = list(lam)
    acc = Counter()
    parts = set_partitions(range(len(cyc))) if transitive else [[list(range(len(cyc)))]]
    for pi in parts:
        mob = mobius_top(len(pi)) if transitive else 1
        combos = {(): Fraction(1)}
        for B in pi:
            bt = tuple(sorted((cyc[i] for i in B), reverse=True))
            new = Counter()
            for ms, w in combos.items():
                for cm, cw in block_weights(bt):
                    new[tuple(sorted(ms + cm))] += w * cw
            combos = new
        for ms, w in combos.items():
            acc[ms] += mob * w
    return {ms: w for ms, w in acc.items() if w}


def esym_list(ms, kmax):
    e = [1] + [0] * kmax
    for x in ms:
        for k in range(kmax, 0, -1):
            e[k] += e[k - 1] * x
    return e


def class_vector(n, mu, transitive=True):
    vec = []
    for lam in integer_partitions(n):
        s = Fraction(0)
        for ms, w in class_weights(lam, transitive).items():
            e = esym_list(ms, n)
            s += w * prod(e[k] if k <= n else 0 for k in mu)
        require(s.denominator == 1, f"non-integral class coefficient n={n} mu={mu} lam={lam}")
        vec.append(int(s))
    return vec


def check_D_engine(nmax=4):
    checked = 0
    for n in range(1, nmax + 1):
        classes = list(integer_partitions(n))
        for d in range(0, 2 * n - 1):
            for mu in integer_partitions(d, max(n - 1, 0) if n > 1 else 0):
                if n == 1 and d > 0:
                    continue
                # word level: e_mu(J) = product of e_k(J); e_k(J) = sum over increasing letter sets
                ident = tuple(range(n))
                states = {(ident, ident): 1}
                for k in mu:
                    new = defaultdict(int)
                    for (perm, lab), c in states.items():
                        # all words J_{i1}...J_{ik} with i1 < ... < ik
                        sub = {(perm, lab): c}
                        def rec(st, start, left):
                            if left == 0:
                                for key, v in st.items():
                                    new[key] += v
                                return
                            for i in range(start, n):
                                st2 = defaultdict(int)
                                for (p, l), v in st.items():
                                    for a in range(i):
                                        st2[(compose(p, transposition(n, a, i)), merge(l, a, i))] += v
                                rec(st2, i + 1, left - 1)
                        rec(sub, 1, k)
                    states = new
                tw = transitive_sum(states)
                byclass = defaultdict(set)
                for p in permutations(range(n)):
                    byclass[cycle_type(p)].add(tw.get(p, 0))
                for lam in classes:
                    require(len(byclass[lam]) == 1, f"non-central transitive image n={n} mu={mu}")
                word_vec = [byclass[lam].pop() for lam in classes]
                require(word_vec == class_vector(n, mu), f"engine disagrees n={n} mu={mu}")
                checked += 1
    return {"T_n(e_mu) vectors compared": checked, "n_max": nmax}


# ---------------------------------------------------------------- integer linear algebra
def egcd(x, y):
    a0, a1, b0, b1 = 1, 0, 0, 1
    while y:
        q = x // y
        x, y = y, x - q * y
        a0, a1 = a1, a0 - q * a1
        b0, b1 = b1, b0 - q * b1
    return x, a0, b0


def hnf(rows, ncols):
    """Row Hermite normal form over Z as {pivot column: row}."""
    H = {}
    for v in rows:
        v = list(v)
        for col in range(ncols):
            if v[col] == 0:
                continue
            if col not in H:
                if v[col] < 0:
                    v = [-x for x in v]
                H[col] = v
                break
            r = H[col]
            a, b = r[col], v[col]
            g, s, t = egcd(a, b)
            if g < 0:
                g, s, t = -g, -s, -t
            H[col] = [s * x + t * y for x, y in zip(r, v)]
            v = [(a // g) * y - (b // g) * x for x, y in zip(r, v)]
    cols = sorted(H)
    for i, c in enumerate(cols):
        for c2 in cols[:i]:
            q = H[c2][c] // H[c][c]
            if q:
                H[c2] = [x - q * y for x, y in zip(H[c2], H[c])]
    return H


def rank_q(rows, ncols):
    M = [[Fraction(x) for x in r] for r in rows]
    rank, col = 0, 0
    for col in range(ncols):
        piv = next((i for i in range(rank, len(M)) if M[i][col] != 0), None)
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        for i in range(len(M)):
            if i != rank and M[i][col] != 0:
                f = M[i][col] / M[rank][col]
                M[i] = [x - f * y for x, y in zip(M[i], M[rank])]
        rank += 1
    return rank


def member(H, v):
    v = list(v)
    for c in sorted(H):
        if v[c] % H[c][c]:
            return False
        q = v[c] // H[c][c]
        v = [x - q * y for x, y in zip(v, H[c])]
    return not any(v)


def check_E_n3():
    rows = []
    # F_alpha images = mobius(alpha) * sum over set partitions of type alpha of H_pi, n = 3
    n = 3
    classes = list(integer_partitions(n))  # (3,), (2,1), (1,1,1)
    for alpha in [(1, 1, 1), (2, 1), (3,)]:
        vec = Counter()
        for pi in set_partitions(range(n)):
            if tuple(sorted(map(len, pi), reverse=True)) != alpha:
                continue
            bv = block_vector(n, pi)
            for p in permutations(range(n)):
                if all(bv[p[i]] == bv[i] for i in range(n)):
                    vec[cycle_type(p)] += 1
        m = mobius_top(len(alpha))
        # each permutation of a class contributes; the class coefficient is the count at one rep
        size = {lam: factorial(n) // z_lambda(lam) for lam in classes}
        rows.append([m * vec[lam] // size[lam] for lam in [(1, 1, 1), (2, 1), (3,)]])
    require(rows == [[2, 0, 0], [-3, -1, 0], [1, 1, 1]], f"n=3 matrix {rows}")
    return {"rows_K111_K21_K3": rows}


def check_F_degree(nmax=7):
    out = {}
    for n in range(2, nmax + 1):
        classes = list(integer_partitions(n))
        ident = classes.index((1,) * n)
        low = [class_vector(n, mu) for d in range(0, 2 * n - 2)
               for mu in integer_partitions(d, n - 1)]
        require(all(v[ident] == 0 for v in low),
                f"nonzero identity coefficient below degree 2n-2 at n={n}")
        full = low + [class_vector(n, mu) for mu in integer_partitions(2 * n - 2, n - 1)]
        r = rank_q(full, len(classes))
        require(r == len(classes), f"degree <= 2n-2 does not span the centre at n={n}")
        out[str(n)] = {"rank_degree_le_2n-2": r, "classes": len(classes),
                       "identity_coefficient_zero_below_2n-2": True}
    return out


def check_G_pairs(nmax=7):
    out = {}
    for n in range(2, nmax + 1):
        classes = list(integer_partitions(n))
        rows = []
        for d in range(0, 2 * n - 1 + n):
            for mu in integer_partitions(d, n - 1):
                rows.append(class_vector(n, mu, transitive=False) + class_vector(n, mu))
        r = rank_q(rows, 2 * len(classes))
        require(r == 2 * len(classes) - 1, f"pair rank {r} at n={n}")
        out[str(n)] = {"pair_rank": r, "2p(n)-1": 2 * len(classes) - 1}
    return out


# ---------------------------------------------------------------- exact integral image
def integral_image(n):
    """Z-basis (HNF) of T_n(Lambda_Z) in class-sum coordinates, without a degree cut-off.
    ev: Lambda_Z -> Z^M, f -> (f(c))_c over the content multisets M that occur, is a ring map;
    its image R is spanned by products of ev(e_1), ..., ev(e_{n-1}) (e_k vanishes on M for k >= n
    because every multiset contains the content 0). The span of products of at most m factors
    stabilises once two consecutive spans agree, and then equals R."""
    classes = list(integer_partitions(n))
    weights = [class_weights(lam) for lam in classes]
    M = sorted({ms for w in weights for ms in w})
    E = [esym_list(ms, n) for ms in M]
    gens = [[E[i][k] for i in range(len(M))] for k in range(1, n)]
    S = hnf([[1] * len(M)], len(M))
    rounds = 0
    while True:
        rounds += 1
        rows = list(S.values()) + [[g[i] * r[i] for i in range(len(M))]
                                   for g in gens for r in S.values()]
        S2 = hnf(rows, len(M))
        if S2 == S:
            break
        S = S2
    img = []
    for r in S.values():
        vec = []
        for w in weights:
            s = sum(w.get(ms, 0) * r[i] for i, ms in enumerate(M))
            require(Fraction(s).denominator == 1, f"non-integral image vector at n={n}")
            vec.append(int(s))
        img.append(vec)
    return classes, img, len(M), rounds


def class_structure_constants(n):
    classes = list(integer_partitions(n))
    size = {l: factorial(n) // z_lambda(l) for l in classes}
    dim = {nu: character(nu, (1,) * n) for nu in classes}
    C = {}
    for a in classes:
        for b in classes:
            for g in classes:
                s = sum(Fraction(character(nu, a) * character(nu, b) * character(nu, g), dim[nu])
                        for nu in classes)
                v = Fraction(size[a] * size[b], factorial(n)) * s
                require(v.denominator == 1, "non-integral structure constant")
                C[a, b, g] = int(v)
    return C


# Values stated in Theorem 6.3 (index of T_n(Lambda_Z) in L_n; index of Z.1 + T_n(Lambda_Z)
# in the integral centre). The check fails if the computation disagrees with the paper.
EXPECTED_IMAGE_INDEX_IN_L = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 7: 1}
EXPECTED_UNITAL_INDEX = {1: 1, 2: 1, 3: 2, 4: 12, 5: 13824, 6: 26542080, 7: 285315214344192000}


def check_H_integral(nmax):
    out = {}
    for n in range(1, nmax + 1):
        classes, img, msize, rounds = integral_image(n)
        k = len(classes)
        target = [z_lambda(l) // h_lambda(l) for l in classes]
        contained = all(v[i] % target[i] == 0 for v in img for i in range(k))
        require(contained, f"image not inside the classwise lattice at n={n}")
        H = hnf(img, k)
        require(len(H) == k, f"image not of full rank at n={n}")
        index_in_centre = prod(abs(H[c][c]) for c in H)
        index_L = prod(target)
        require(index_in_centre % index_L == 0, "index inconsistency")
        Lc = hnf([[v[i] // target[i] for i in range(k)] for v in img], k)
        quotient_diag = [abs(Lc[c][c]) for c in sorted(Lc)]
        # unital closure of Z.1 + image
        one = [1 if l == (1,) * n else 0 for l in classes]
        A = hnf(list(H.values()) + [one], k)
        C = class_structure_constants(n)
        basis = list(A.values())
        closed = True
        for u in basis:
            for w in basis:
                pv = [sum(u[i] * w[j] * C[classes[i], classes[j], g]
                          for i in range(k) if u[i] for j in range(k) if w[j]) for g in classes]
                if not member(A, pv):
                    closed = False
        require(closed, f"Z.1 + image not closed under multiplication at n={n}")
        ident_coeffs = sorted({abs(v[classes.index((1,) * n)]) for v in H.values()} - {0})
        entry = {
            "classes": k,
            "content_multisets": msize,
            "closure_rounds": rounds,
            "index_in_integral_centre": index_in_centre,
            "index_of_classwise_lattice": index_L,
            "index_of_image_in_classwise_lattice": index_in_centre // index_L,
            "quotient_diagonal_in_lattice_coordinates": quotient_diag,
            "unital_Z_subalgebra_equals_Z1_plus_image": True,
            "index_of_unital_subalgebra": prod(abs(A[c][c]) for c in A),
        }
        if n in EXPECTED_IMAGE_INDEX_IN_L:
            require(entry["index_of_image_in_classwise_lattice"] == EXPECTED_IMAGE_INDEX_IN_L[n],
                    f"index of image in L_n differs from Theorem 6.3 at n={n}")
            require(entry["index_of_unital_subalgebra"] == EXPECTED_UNITAL_INDEX[n],
                    f"unital index differs from Theorem 6.3 at n={n}")
        if n == 6:
            # the extra congruence: x_411 + x_222 + x_21111 = 0 mod 2 with x = c / (z/h)
            idx = [classes.index(l) for l in [(4, 1, 1), (2, 2, 2), (2, 1, 1, 1, 1)]]
            holds = all(sum(v[i] // target[i] for i in idx) % 2 == 0 for v in img)
            require(holds, "n=6 congruence fails")
            witness = [0] * k
            witness[idx[2]] = target[idx[2]]  # c_{21111} = z/h = 24, others 0: in L, not in image
            require(not member(H, witness), "n=6 witness unexpectedly in the image")
            entry["extra_congruence"] = ("c_(4,1,1)/4 + c_(2,2,2)/8 + c_(2,1,1,1,1)/24 is even "
                                         "for every element of T_6(Lambda_Z)")
        out[str(n)] = entry
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="results/verification.json")
    ap.add_argument("--integral-max", type=int, default=7,
                    help="largest n for the exact integral image (8 takes much longer)")
    args = ap.parse_args()
    results = {"python": platform.python_version(), "checks": {}}
    steps = [
        ("A_marker_construction_word_level", lambda: check_A_marker(4)),
        ("B_mobius_lemma_word_level", lambda: check_B_lemma(4, 4)),
        ("C_degree_selectors", lambda: check_C_selectors(9)),
        ("D_class_engine_vs_words", lambda: check_D_engine(4)),
        ("E_n3_matrix", check_E_n3),
        ("F_optimal_degree", lambda: check_F_degree(7)),
        ("G_pair_rank", lambda: check_G_pairs(6)),
        ("H_integral_image", lambda: check_H_integral(args.integral_max)),
    ]
    try:
        for name, fn in steps:
            results["checks"][name] = fn()
            print(f"PASS {name}", flush=True)
    except CheckFailure as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
    with open(args.output, "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
