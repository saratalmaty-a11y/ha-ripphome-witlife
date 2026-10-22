#!/usr/bin/env python3
"""Verify the codec against captured vectors.

Usage:  cp keys.json.example keys.json  (fill your keys)  &&  python3 verify.py
Requires: pip install pycryptodome
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "custom_components", "ripphome"))
from codec import RippMeshCodec, ATTR_ONOFF, ATTR_BRIGHTNESS, ATTR_COLORTEMP, DEFAULT_FLAG

# (label, SEQ, TID, FLAG, ATTR, VAL, expected 26-byte frame)
# Independent live captures (not used to derive the header byte) — see docs/SPEC.md.
VECTORS = [
    ("ON       ", 0x00, 0x3c, DEFAULT_FLAG, ATTR_ONOFF, 0x01,
     "72a3c424c0206b34eb7292e55fe4fcefd6c3f363e5f842fc5665"),
    ("BRIGHT 9e", 0x14, 0x50, DEFAULT_FLAG, ATTR_BRIGHTNESS, 0x9e,
     "7294515232add1ecf2722b66c1e73e9a4739a4cd9ad80e34be97"),
    ("CCT 00   ", 0x03, 0x23, DEFAULT_FLAG, ATTR_COLORTEMP, 0x00,
     "72bf5d9e403d105c08c2946c84eba4a5c8d0b557936561fc77b9"),
]


def main() -> int:
    path = os.environ.get("RIPPMESH_KEYS", os.path.join(os.path.dirname(__file__), "keys.json"))
    try:
        d = json.load(open(path))
    except Exception as e:
        print("No keys.json:", e)
        print("Copy keys.json.example to keys.json and fill in your two keys.")
        return 1
    cdc = RippMeshCodec(bytes.fromhex(d["key_enc"]), bytes.fromhex(d["key_priv"]),
                        bytes.fromhex(d.get("dst", "4d37")))
    ok = True
    for label, seq, tid, flag, attr, val, exp in VECTORS:
        got = cdc.build_frame(seq, tid, attr, val, flag).hex()
        match = got == exp
        ok &= match
        print(f"[{label}] {'OK' if match else 'FAIL'}  {got}")
    print("All frames match:", ok)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
