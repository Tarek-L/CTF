
from pwn import remote, context
import random
from math import gcd

context.log_level = "info"

HOST = "ssss.chals.sekai.team"
PORT = 1337

# Field modulus
p = 2**256 - 189

def modinv(a):
    return pow(a, p-2, p)

def factor_small(n):
    """Return prime factorization (multiset as dict) for small n <= 50."""
    f = {}
    d = 2
    x = n
    while d * d <= x:
        while x % d == 0:
            f[d] = f.get(d, 0) + 1
            x //= d
        d += 1
    if x > 1:
        f[x] = f.get(x, 0) + 1
    return f

def find_primitive_t_root(t):
    """
    Find element r in F_p of exact order t (a primitive t-th root of unity).
    We sample g and set r = g^((p-1)/t); verify order by checking prime factors.
    """
    assert (p-1) % t == 0, "t must divide p-1 to have t-th roots of unity"
    exp = (p-1) // t
    pf = factor_small(t)  # tiny; t <= 50
    while True:
        g = random.randrange(2, p-1)
        r = pow(g, exp, p)
        if r == 1:
            continue
        ok = True
        for q in pf.keys():
            # If r^(t/q) == 1 for some prime q|t, order is not exactly t
            if pow(r, t//q, p) == 1:
                ok = False
                break
        if ok:
            return r

def poly_add(a, b):
    """Add polynomials (coeff lists, a[i] = coeff x^i) mod p."""
    n = max(len(a), len(b))
    out = [(0) for _ in range(n)]
    for i in range(n):
        out[i] = ((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p
    return out

def poly_mul(a, b, max_deg=None):
    """Multiply polynomials mod p. If max_deg provided, truncate to that degree."""
    deg = (len(a)-1) + (len(b)-1)
    if max_deg is not None:
        out_len = max_deg + 1
    else:
        out_len = deg + 1
    out = [0] * out_len
    for i, ai in enumerate(a):
        if ai == 0: continue
        for j, bj in enumerate(b):
            d = i + j
            if max_deg is not None and d > max_deg:
                continue
            out[d] = (out[d] + ai * bj) % p
    return out

def lagrange_coeffs(xs, ys):
    """
    Given t pairs (x_i, y_i) with distinct x_i, return coefficients of the unique
    polynomial H(x) of degree <= t-1 with H(x_i)=y_i, as a list h[0..t-1].
    O(t^2), fine for t<=50.
    """
    t = len(xs)
    h = [0] * t  # degree <= t-1
    for i in range(t):
        # Build numerator poly: prod_{j != i} (x - x_j), degree t-1
        numer = [1]
        denom = 1
        xi = xs[i]
        for j in range(t):
            if j == i: continue
            xj = xs[j]
            numer = poly_mul(numer, [(-xj) % p, 1], max_deg=t-1)
            denom = (denom * ((xi - xj) % p)) % p
        li_scale = (ys[i] * modinv(denom)) % p  # Lagrange basis scaling
        # h += li_scale * numer
        for k in range(t):
            h[k] = (h[k] + li_scale * (numer[k] if k < len(numer) else 0)) % p
    return h  # h[0..t-1]

def pick_points_roots_of_unity(t):
    """
    Choose x_i as t-th roots of unity so that ∏(x - x_i) = x^t - 1.
    Returns list xs of length t in F_p\{0}.
    """
    # Ensure t | (p-1). For our p, this holds for many t in [20,50]; we’ll check and, if not, adjust t.
    if (p-1) % t != 0:
        return None
    r = find_primitive_t_root(t)
    xs = [pow(r, i, p) for i in range(t)]
    # All xi are nonzero and < p automatically.
    return xs

def recv_int_line(conn):
    """Read lines until one parses as an integer modulo p. Returns int."""
    while True:
        line = conn.recvline(timeout=5)
        if not line:
            raise EOFError("Connection closed.")
        s = line.strip().decode(errors="ignore")
        # try to parse base-10 integer (possibly huge)
        try:
            val = int(s)
            # normalize mod p in case negative (shouldn't happen from server)
            return val % p
        except ValueError:
            # ignore banner or text lines
            continue

def send_int(conn, x):
    conn.sendline(str(int(x)).encode())

def play_round_collect_known(conn, t):
    """
    Plays one challenge round:
    - sends t
    - chooses t-th roots of unity as x_i
    - receives y_i
    - interpolates H of degree <= t-1
    - returns the set of fixed coefficients {h_1, ..., h_{t-1}}
    Also returns whether we used roots-of-unity (should be True), and the x list (for debug).
    """
    xs = pick_points_roots_of_unity(t)
    if xs is None:
        # Fallback: if t doesn't divide p-1 (unlikely), decrement until it does.
        tt = t
        while tt >= 20 and (p-1) % tt != 0:
            tt -= 1
        if tt < 20:
            raise RuntimeError("Could not find t | (p-1) in allowed range.")
        t = tt
        xs = pick_points_roots_of_unity(t)

    # send t
    send_int(conn, t)

    ys = []
    for i in range(t):
        send_int(conn, xs[i])
        yi = recv_int_line(conn)
        ys.append(yi)

    # interpolate degree <= t-1 polynomial H matching the samples
    h = lagrange_coeffs(xs, ys)  # len t
    # fixed coefficients are h[1..t-1]
    fixed = set(h[1:])  # exclude h[0], which may differ from true c0 by ±α
    return fixed, t

def main():
    r = remote(HOST, PORT, ssl=True)

    # --- Round 1: reconnaissance (we'll guess garbage at the end) ---
    # choose the max t for more fixed coefficients
    t1 = 50
    fixed1, t1 = play_round_collect_known(r, t1)
    # throwaway guess for round 1
    send_int(r, 0)  # almost surely wrong; we just advance to round 2

    # Consume the server's response line (":<" or flag if we got lucky by chance)
    try:
        _ = r.recvline(timeout=2)
    except:
        pass

    # --- Round 2: compute intersection and answer ---
    # Use a different t to make accidental collisions astronomically unlikely
    t2 = 49
    fixed2, t2 = play_round_collect_known(r, t2)

    # Intersection should be exactly the secret with overwhelming probability
    cand = fixed1.intersection(fixed2)
    if len(cand) != 1:
        # Extremely unlikely; as a fallback, pick something deterministic
        # (e.g., min) so we still send an answer.
        # You could also add more logic (e.g., try include h0 estimates) but we only get 2 rounds.
        print(f"[!] Unexpected intersection size {len(cand)}; falling back.", flush=True)
        guess = min(cand) if cand else 0
    else:
        (guess,) = tuple(cand)

    send_int(r, guess)

    # print whatever the service responds (flag or sad face)
    try:
        while True:
            line = r.recvline(timeout=2)
            if not line:
                break
            print(line.decode(errors="ignore").rstrip())
    except EOFError:
        pass

    r.close()

if __name__ == "__main__":
    main()
