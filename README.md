# RippHome / Wit Life — Home Assistant integration (FastCon‑mesh BLE lamps)

Local control for **RippHome / Wit Life** (OE Technology, `com.oecore.ripphome`) lamps —
the Telink FastCon‑mesh bulbs controlled by non‑connectable BLE advertising. No cloud,
no frame replay: commands are computed and broadcast.

> Control is a BLE **advertising broadcast**, so the HA host needs a Bluetooth adapter
> that can transmit advertisements (or pair this with an ESPHome `ble_adv` broadcaster).
> The default transmitter shells out to BlueZ `btmgmt add-adv`.

## Install (HACS)
1. HACS → Integrations → ⋮ → Custom repositories → add this repo as *Integration*.
2. Install **RippHome / Wit Life**, restart HA.
3. Settings → Devices & Services → Add Integration → **RippHome / Wit Life**.
4. Enter your network keys and the lamp ShortId (`dst`).

## Getting your keys
The two 16‑byte keys are secrets derived from **your** mesh network key. Extract them
once from the phone app (see `docs/SPEC.md` for how; Frida on the app's `AesCipher`).
They are stored only in the HA config entry — **never commit them**.

- `key_enc`  — encrypt key (CipherType `0x0238ee61`)
- `key_priv` — privacy key (CipherType `0x0238ee41`)
- `dst`      — lamp ShortId, e.g. `4d37`

## Features
- On / off
- Brightness (0–255)
- Color temperature (2700–6500 K, mapped to the lamp's 0x00–0xFF)

## How it works
See **`docs/SPEC.md`** for the full protocol. In short: access PDU → AES‑128‑CCM
(encrypt key, 13‑byte nonce, 4‑byte MIC) → AES‑128‑ECB privacy over the header →
`02 01 06 1b ff || frame(26)`. Verified against live captures (`verify.py`, `vectors.txt`).

## Verify the codec
```
pip install pycryptodome
cp keys.json.example keys.json   # fill your two keys (chmod 600)
python3 verify.py                # -> All frames match: True
```

## Credits / legal
Independent interoperability work for lamps the user owns. This repo contains an
original implementation of the protocol and a factual specification — **no vendor code**.
Not affiliated with OE Technology / RippHome / Wit Life. MIT licensed.
