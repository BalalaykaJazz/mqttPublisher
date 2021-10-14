#!/bin/bash
# Декодирование настроек

scp ../src/mqtt_pub/settings/enc_env ../src/mqtt_pub/settings/.env
scp ../src/mqtt_pub/settings/enc_user.json ../src/mqtt_pub/settings/user.json
sops --hc-vault-transit $VAULT_ADDR/v1/sops/keys/iot  --verbose -d -i ../src/mqtt_pub/settings/.env
sops --hc-vault-transit $VAULT_ADDR/v1/sops/keys/iot  --verbose -d -i ../src/mqtt_pub/settings/user.json