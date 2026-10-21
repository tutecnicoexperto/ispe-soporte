#!/usr/bin/env python3
"""Firma la personalización de una variante y la convierte en custom.txt.

Uso:  ISPE_FIRMA=<semilla ed25519 en base64> python3 ispe/firmar_custom.py variantes/X.json > custom.txt
      python3 ispe/firmar_custom.py --nueva-clave      (genera semilla y clave pública, una sola vez)

Formato que espera RustDesk (src/common.rs, read_custom_client): base64 de
firma(64 bytes) + JSON, la firma de libsodium crypto_sign. La clave pública debe coincidir
con CLAVE_FIRMA_CUSTOM de aplicar_marca.py.
"""
import base64
import json
import os
import sys

from nacl.signing import SigningKey


def main():
    if sys.argv[1:] == ["--nueva-clave"]:
        # Una sola vez: la semilla va al secreto ISPE_FIRMA del repo; la pública a aplicar_marca.py
        sk = SigningKey.generate()
        print("SEMILLA (secreto ISPE_FIRMA):", base64.b64encode(bytes(sk)).decode())
        print("PUBLICA (CLAVE_FIRMA_CUSTOM):", base64.b64encode(bytes(sk.verify_key)).decode())
        return
    if len(sys.argv) != 2 or "ISPE_FIRMA" not in os.environ:
        sys.exit(__doc__)
    # JSON compacto y validado antes de firmar (un error aquí es mejor que un cliente sin marca)
    datos = json.load(open(sys.argv[1], encoding="utf-8"))
    mensaje = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    sk = SigningKey(base64.b64decode(os.environ["ISPE_FIRMA"]))
    firmado = sk.sign(mensaje)  # firma (64 bytes) + mensaje, igual que crypto_sign de libsodium
    sys.stdout.write(base64.b64encode(bytes(firmado)).decode())


if __name__ == "__main__":
    main()
