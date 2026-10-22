#!/usr/bin/env python3
"""Verify the codec against captured vectors.

Usage:  cp keys.json.example keys.json  (fill your keys)  &&  python3 verify.py
Requires: pip install pycryptodome
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "custom_components", "ripphome"))
from codec import RippMeshCodec, ATTR_ONOFF, ATTR_BRIGHTNESS, ATTR_COLORTEMP, DEFAULT_FLAG

# (label, SEQ, TID, FLAG, ATTR, VAL, expected 26-byte frame) — live captured & verified
VECTORS = [
    ("ON       ", 0x0b, 0x46, DEFAULT_FLAG, ATTR_ONOFF, 0x01,
     "72a44d1346ffad2721ec1d739201cfa35d6d0d5f95e98c959a9a"),
    ("BRIGHT 9e", 0x17, 0x52, DEFAULT_FLAG, ATTR_BRIGHTNESS, 0x9e,
     "72c457203ee1487f1570660fa38578956b2febf41958ed3626d6"),
    ("CCT ff   ", 0x00, 0x1e, DEFAULT_FLAG, ATTR_COLORTEMP, 0xff,
     "72a7112da9cd0934eb5092e6a1e4fcefd6c3f363e5f85b3032f7"),
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
