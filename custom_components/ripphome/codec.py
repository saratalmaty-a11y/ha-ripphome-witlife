"""RippHome / Wit Life (OE Technology) FastCon-mesh BLE-ADV codec.

Original implementation of the command protocol (algorithm, not vendor code).
See docs/SPEC.md. Requires pycryptodome.
"""
from __future__ import annotations
import itertools
from Crypto.Cipher import AES

ATTR_ONOFF = 0x10
ATTR_BRIGHTNESS = 0x11
ATTR_COLORTEMP = 0x13

_HDR_12 = bytes([0x80, 0xA0, 0x00])
_HDR_56 = bytes([0x7C, 0x00])
DEFAULT_FLAG = 0xD6


class RippMeshCodec:
    """Encode lamp commands into the 26-byte manufacturer frame / 31-byte ADV."""

    def __init__(self, key_enc: bytes, key_priv: bytes, dst: bytes = b"\x4d\x37"):
        if len(key_enc) != 16 or len(key_priv) != 16:
            raise ValueError("keys must be 16 bytes")
        if len(dst) != 2:
            raise ValueError("dst must be 2 bytes")
        self.key_enc = key_enc
        self.key_priv = key_priv
        self.dst = dst
        self._seq = itertools.cycle(range(256))
        self._tid = itertools.cycle(range(256))

    def build_frame(self, seq: int, tid: int, attr: int, val: int,
                    flag: int = DEFAULT_FLAG) -> bytes:
        seq &= 0xFF
        tid &= 0xFF
        p_hdr = bytes([0x72]) + _HDR_12 + bytes([seq]) + _HDR_56
        payload = self.dst + bytes([tid, flag, attr, val]) + b"\x00" * 9
        nonce = b"\x00" + p_hdr[1:7] + b"\x00" * 5 + b"\x01"
        c = AES.new(self.key_enc, AES.MODE_CCM, nonce=nonce, mac_len=4)
        ccm = c.encrypt(payload) + c.digest()
        pecb = AES.new(self.key_priv, AES.MODE_ECB).encrypt(b"\x00" * 8 + b"\x01" + ccm[:7])
        obf = bytes(a ^ b for a, b in zip(pecb[:6], p_hdr[1:7]))
        return bytes([0x72]) + obf + ccm

    def build_adv(self, *a, **kw) -> bytes:
        return bytes([0x02, 0x01, 0x06, 0x1B, 0xFF]) + self.build_frame(*a, **kw)

    def _cmd(self, attr: int, val: int) -> bytes:
        return self.build_adv(next(self._seq), next(self._tid), attr, val)

    def on(self) -> bytes:
        return self._cmd(ATTR_ONOFF, 0x01)

    def off(self) -> bytes:
        return self._cmd(ATTR_ONOFF, 0x00)

    def brightness(self, value_0_255: int) -> bytes:
        return self._cmd(ATTR_BRIGHTNESS, max(0, min(255, value_0_255)))

    def color_temp(self, value_0_255: int) -> bytes:
        return self._cmd(ATTR_COLORTEMP, max(0, min(255, value_0_255)))
