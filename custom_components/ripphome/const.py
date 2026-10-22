"""Constants for the RippHome / Wit Life integration."""
DOMAIN = "ripphome"

CONF_KEY_ENC = "key_enc"      # 16-byte hex, encrypt key (CipherType 0x0238ee61)
CONF_KEY_PRIV = "key_priv"    # 16-byte hex, privacy key (CipherType 0x0238ee41)
CONF_DST = "dst"              # 2-byte hex ShortId, e.g. "4d37"
CONF_NAME = "name"
CONF_TX = "transmitter"       # "btmgmt" | "log"
CONF_HCI = "hci_index"        # adapter index for btmgmt (default 0)
CONF_REPEAT = "repeat"        # how many times to broadcast each command

DEFAULT_TX = "btmgmt"
DEFAULT_HCI = 0
DEFAULT_REPEAT = 4
