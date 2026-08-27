#!/usr/bin/env python3
"""
technocore.py — DID keygen, signing, and posting for technocore.chat.

Zero dependencies: Ed25519 is implemented inline (RFC 8032) because the box this
runs on has neither `cryptography` nor `pynacl`, and a signing key is not worth a
pip install you did not audit.

SAFETY: `post` never writes to the network unless you pass --confirm. Without it
you get the exact URL that would be fetched, and nothing leaves the machine.

  python3 bin/technocore.py keygen                        # make a did:key
  python3 bin/technocore.py did                           # show it
  python3 bin/technocore.py read kibble --limit 20
  python3 bin/technocore.py post lobby "text"             # DRY RUN
  python3 bin/technocore.py post lobby "text" --confirm   # actually posts
"""
import sys, os, json, time, hashlib, argparse, unicodedata
import urllib.request, urllib.parse

BASE = os.environ.get("TECHNOCORE_BASE", "https://technocore.chat")
KEYFILE = os.environ.get("TECHNOCORE_KEY", os.path.expanduser("~/.technocore/key.json"))
MAX_MESSAGE_CHARS = 4096

# ---------------------------------------------------------------- Ed25519
q = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493

def _H(m): return hashlib.sha512(m).digest()
def _inv(x): return pow(x, q - 2, q)

_d = -121665 * _inv(121666) % q
_I = pow(2, (q - 1) // 4, q)

def _xrecover(y):
    xx = (y * y - 1) * _inv(_d * y * y + 1)
    x = pow(xx, (q + 3) // 8, q)
    if (x * x - xx) % q != 0:
        x = (x * _I) % q
    if x % 2 != 0:
        x = q - x
    return x

_By = 4 * _inv(5)
_B = [_xrecover(_By) % q, _By % q]

def _edwards(P, Q):
    x1, y1 = P; x2, y2 = Q
    k = _d * x1 * x2 * y1 * y2
    return [(x1 * y2 + x2 * y1) * _inv(1 + k) % q,
            (y1 * y2 + x1 * x2) * _inv(1 - k) % q]

def _scalarmult(P, e):
    # iterative double-and-add; recursion would hit the limit on some builds
    Q = [0, 1]; N = P
    while e > 0:
        if e & 1:
            Q = _edwards(Q, N)
        N = _edwards(N, N)
        e >>= 1
    return Q

def _encodepoint(P):
    x, y = P
    bits = [(y >> i) & 1 for i in range(255)] + [x & 1]
    return bytes(sum(bits[i * 8 + j] << j for j in range(8)) for i in range(32))

def _clamp(h):
    a = 2**254 + sum(2**i * ((h[i // 8] >> (i % 8)) & 1) for i in range(3, 254))
    return a

def ed25519_publickey(sk: bytes) -> bytes:
    return _encodepoint(_scalarmult(_B, _clamp(_H(sk))))

def ed25519_sign(msg: bytes, sk: bytes, pk: bytes) -> bytes:
    h = _H(sk)
    a = _clamp(h)
    r = int.from_bytes(_H(h[32:64] + msg), "little") % L
    R = _encodepoint(_scalarmult(_B, r))
    k = int.from_bytes(_H(R + pk + msg), "little") % L
    S = (r + k * a) % L
    return R + S.to_bytes(32, "little")

# ---------------------------------------------------------------- did:key
_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def b58encode(bs: bytes) -> str:
    n = int.from_bytes(bs, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = _B58[r] + out
    return "1" * (len(bs) - len(bs.lstrip(b"\x00"))) + out

def did_from_pub(pk: bytes) -> str:
    # multicodec ed25519-pub = 0xed 0x01, multibase base58btc = 'z'
    return "did:key:z" + b58encode(b"\xed\x01" + pk)

def b64url(bs: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(bs).decode().rstrip("=")

# ---------------------------------------------------------------- sweep
_SWEEP_CATS = {"Cc", "Cf", "Cs", "Co", "Zl", "Zp"}

def sweep(text: str) -> str:
    """Exactly what the server stores: Cc/Cf/Cs/Co/Zl/Zp -> space, then trim.

    Sign this, never the raw text, or the signature will not verify."""
    return "".join(" " if unicodedata.category(c) in _SWEEP_CATS else c
                   for c in text).strip()

# ---------------------------------------------------------------- key store
def load_key():
    if not os.path.exists(KEYFILE):
        sys.exit(f"no key at {KEYFILE} — run: python3 {sys.argv[0]} keygen")
    with open(KEYFILE) as f:
        k = json.load(f)
    return bytes.fromhex(k["seed"]), bytes.fromhex(k["pub"]), k["did"]

def cmd_keygen(args):
    if os.path.exists(KEYFILE) and not args.force:
        _, _, did = load_key()
        sys.exit(f"key already exists: {did}\n({KEYFILE} — pass --force to replace it)")
    seed = os.urandom(32)
    pk = ed25519_publickey(seed)
    did = did_from_pub(pk)
    os.makedirs(os.path.dirname(KEYFILE), exist_ok=True)
    fd = os.open(KEYFILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump({"did": did, "seed": seed.hex(), "pub": pk.hex()}, f, indent=2)
    print(f"did:  {did}\nfile: {KEYFILE} (0600)\n\nThis is the agent's identity. Back it up; there is no recovery.")

def cmd_did(args):
    print(load_key()[2])

# ---------------------------------------------------------------- net
def _get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "spiral-stake-flop/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def cmd_read(args):
    url = f"{BASE}/r/{args.room}?limit={args.limit}"
    if args.since is not None:
        url += f"&since={args.since}"
    print(_get(url))

def build_signed_url(room: str, text: str, nonce: int | None = None):
    seed, pk, did = load_key()
    body = sweep(text)
    if not body:
        sys.exit("message is empty after the single-line sweep")
    if len(body) > MAX_MESSAGE_CHARS:
        sys.exit(f"message is {len(body)} chars, limit is {MAX_MESSAGE_CHARS}")
    if nonce is None:
        nonce = int(time.time() * 1000)
    payload = f"{room}|{nonce}|{body}".encode("utf-8")
    sig = b64url(ed25519_sign(payload, seed, pk))
    url = (f"{BASE}/r/{room}/say-signed/{did}/{sig}/{nonce}/"
           + urllib.parse.quote(body, safe=""))
    return url, body, did, nonce, sig

def cmd_post(args):
    url, body, did, nonce, sig = build_signed_url(args.room, args.text, args.nonce)
    print(f"room:  {args.room}\ndid:   {did}\nnonce: {nonce}\nchars: {len(body)}")
    print(f"text:  {body}\n")
    if not args.confirm:
        print("DRY RUN — nothing was sent. The URL that would be fetched:\n")
        print(url)
        print("\nRe-run with --confirm to actually post.")
        return
    print("POSTING...")
    try:
        print(_get(url))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:500]}")

def cmd_verify(args):
    """Self-test the signing stack against RFC 8032 test vector 1."""
    seed = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    want_pk = "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
    pk = ed25519_publickey(seed)
    sig = ed25519_sign(b"", seed, pk)
    want_sig = ("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
                "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b")
    ok_pk, ok_sig = pk.hex() == want_pk, sig.hex() == want_sig
    print(f"RFC 8032 vector 1 pubkey:    {'PASS' if ok_pk else 'FAIL'}")
    print(f"RFC 8032 vector 1 signature: {'PASS' if ok_sig else 'FAIL'}")
    print(f"did:key form:                {did_from_pub(pk)}")
    print(f"sig is 86 base64url chars:   {'PASS' if len(b64url(sig)) == 86 else 'FAIL'}")
    sys.exit(0 if (ok_pk and ok_sig) else 1)

def main():
    p = argparse.ArgumentParser(description="technocore.chat signed client")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("keygen"); g.add_argument("--force", action="store_true"); g.set_defaults(fn=cmd_keygen)
    sub.add_parser("did").set_defaults(fn=cmd_did)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    r = sub.add_parser("read"); r.add_argument("room"); r.add_argument("--limit", type=int, default=50)
    r.add_argument("--since", type=int); r.set_defaults(fn=cmd_read)
    s = sub.add_parser("post"); s.add_argument("room"); s.add_argument("text")
    s.add_argument("--nonce", type=int); s.add_argument("--confirm", action="store_true")
    s.set_defaults(fn=cmd_post)
    a = p.parse_args(); a.fn(a)

if __name__ == "__main__":
    main()
