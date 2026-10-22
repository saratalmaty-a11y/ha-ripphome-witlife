# RippHome FastCon‑mesh — command frame specification

Verified against live captures: the self‑test reproduces the exact over‑the‑air frames
for on/off, brightness and color‑temp.

## Over‑the‑air layout (31 bytes)
```
02 01 06            flags
1b ff               manufacturer specific, length 0x1b
<frame : 26 bytes>  manufacturer data (starts with company-id low byte 0x72)
```

## Inputs
- `SEQ` — per‑frame counter (1 byte, increments every command; nonce source).
- `TID` — transaction id (1 byte, increments every command).
- `F`   — flag (`0xd6`/`0x96`; parity/retry marker).
- `DST` — target ShortId (2 bytes, e.g. `4d 37`).
- `ATTR`,`VAL` — command.

## Plaintext (22 bytes)
```
P_hdr (7)   = 72 80 a0 00 SEQ 7c 00
payload(15) = DST(2) TID F ATTR VAL 00*9
```

## Crypto
- `KEY_ENC`  (CipherType 0x0238ee61) — AES‑128‑CCM.
- `KEY_PRIV` (CipherType 0x0238ee41) — AES‑128‑ECB (privacy).
```
nonce(13) = 00 || P_hdr[1:7] || 00*5 || 01          # 00 80 a0 00 SEQ 7c 00 00 00 00 00 00 01 (IV index 1)
CCM(19)   = AES128_CCM(KEY_ENC, nonce, mac_len=4).encrypt(payload)   # ct15 || mic4
PECB(16)  = AES128_ECB(KEY_PRIV).encrypt(00*8 || 01 || CCM[0:7])
```

## Frame assembly (26 bytes)
```
frame[0]    = 0x72
frame[1:7]  = PECB[0:6] XOR P_hdr[1:7]
frame[7:26] = CCM
```

## Commands
| ATTR | meaning     | VAL                        |
|------|-------------|----------------------------|
| 0x10 | on/off      | 01 = on, 00 = off          |
| 0x11 | brightness  | 00..FF                     |
| 0x13 | color temp  | 00..FF (warm ↔ cold)       |

## Notes
- CCM: 13‑byte nonce (L=2), 4‑byte MIC, no AAD.
- Key derivation (BLE‑mesh k2/k3 style): base net key → encrypt/privacy/beacon keys via
  CMAC‑KDF with salt labels `nkek-id128` / `nkpk` / `nkbk` / `id128` / `nkid-id64`.
- Extract `KEY_ENC`/`KEY_PRIV` once from the app at runtime (Frida on `AesCipher`); they
  are your network's secrets — store them only in the HA config entry / local `keys.json`.
