#!/usr/bin/env python3
"""Aplica la marca «ISPE Soporte» sobre una copia limpia del código oficial de RustDesk.

Uso:  python3 ispe/aplicar_marca.py <carpeta-del-codigo-rustdesk> <revision-ispe> <variante>
      revisión 1-9: nuestra versión será <versión-rustdesk>-<revisión>, p. ej. 1.5.0-3
      variante: ISPE-Soporte (clientes: solo recibe conexiones) | ISPE-Tecnico (técnicos: completo)

Lo ejecuta el workflow de GitHub Actions justo después de descargar rustdesk/rustdesk, así el
repositorio solo guarda nuestra personalización y subir de versión es cambiar un número.

Qué cambia:
  1. Servidor propio (remoto.negociosdigitalesonline.es) y su clave pública como valores de fábrica.
  2. Nombre interno de la app «ISPE-Soporte» (sin espacios: RustDesk crea el servicio de Windows
     con `sc create <nombre>` sin comillas y un espacio lo rompería).
  3. Clave con la que se verifica custom.txt: la nuestra en vez de la de RustDesk, para poder
     firmar nosotros las variantes (cliente / técnico) igual que hace el generador de RustDesk Pro.
  4. Iconos, logos y textos de versión del .exe (empresa, descripción, producto).
  5. Actualización automática desde NUESTRO repositorio: la última versión se consulta en
     ispe/latest.json (raw.githubusercontent.com) y se descarga de las releases de
     tutecnicoexperto/ispe-soporte el ejecutable de cada variante (<app>-<versión>-x86_64.exe).
Si algún texto a sustituir no aparece (cambio de versión upstream) el script falla en vez de
compilar un cliente a medio personalizar.
"""
import os
import shutil
import sys

# --- Datos de la personalización -----------------------------------------------------------
SERVIDOR = "remoto.negociosdigitalesonline.es"
CLAVE_SERVIDOR = "sDUE7s9NgN2R0kJqMZbThSxLR9k8xdRvOXxG8f+ubGE="      # id_ed25519.pub de hbbs (CT183)
CLAVE_FIRMA_CUSTOM = "ybrGVGy627hCRi+qD38M45N4LYnM3n/TpdpBvc9fruo="                        # pública; firma los custom.txt
# Variantes: cada una se compila por separado con su nombre y sus ajustes fijos (HARD_SETTINGS).
# conn-type=incoming deja el cliente en «solo recibir» (pantalla simple con ID y contraseña).
VARIANTES = {
    "ISPE-Soporte": [("conn-type", "incoming")],
    "ISPE-Tecnico": [],
}
EMPRESA = "ISPE Internet Seguro para Empresas"
PRODUCTO = "ISPE Soporte"
DESCRIPCION = "ISPE Soporte - Asistencia remota"
COPYRIGHT = "ISPE Internet Seguro para Empresas. Basado en RustDesk (AGPL-3.0) de Purslane Tech Pte. Ltd."

REPO_DUENO, REPO_NOMBRE = "tutecnicoexperto", "ispe-soporte"     # repo público con releases
URL_ULTIMA = f"https://raw.githubusercontent.com/{REPO_DUENO}/{REPO_NOMBRE}/main/ispe/latest.json"

MARCA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marca")


def sustituir(src, ruta, pares):
    """Reemplaza cada (viejo, nuevo) en el fichero; aborta si algún 'viejo' no está."""
    p = os.path.join(src, ruta)
    with open(p, encoding="utf-8") as f:
        texto = f.read()
    for viejo, nuevo in pares:
        if viejo not in texto:
            sys.exit(f"ERROR: no encuentro {viejo!r} en {ruta} (¿ha cambiado RustDesk?)")
        texto = texto.replace(viejo, nuevo)
    with open(p, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"  OK {ruta}")


def copiar(src, origen, destinos):
    """Copia un fichero de ispe/marca a una o varias rutas del código."""
    for d in destinos:
        shutil.copy(os.path.join(MARCA, origen), os.path.join(src, d))
        print(f"  OK {d}")


def main():
    if (len(sys.argv) != 4 or not sys.argv[2].isdigit() or not 1 <= int(sys.argv[2]) <= 9
            or sys.argv[3] not in VARIANTES):
        sys.exit(__doc__)
    src, revision, NOMBRE_APP = sys.argv[1], sys.argv[2], sys.argv[3]
    print(f"Variante: {NOMBRE_APP}")

    print("1-3. Servidor, clave, nombre y firma de custom.txt")
    sustituir(src, "libs/hbb_common/src/config.rs", [
        ('RwLock::new("RustDesk".to_owned())', f'RwLock::new("{NOMBRE_APP}".to_owned())'),
        ('&["rs-ny.rustdesk.com"]', f'&["{SERVIDOR}"]'),
        ('"OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw="', f'"{CLAVE_SERVIDOR}"'),
    ])
    # Opciones fijas compiladas en el binario (en lugar de custom.txt: con custom.txt el servidor
    # de Windows lanzado por el servicio en la sesión del usuario cae en bucle, 21/10/2026).
    #  - OVERWRITE: actualización automática activada siempre.
    #  - BUILTIN:   ocultar ajustes de servidor/proxy/websocket y tarjetas de ayuda.
    #  - HARD:      sin cuenta ni libreta de direcciones de RustDesk (no tenemos servidor Pro).
    def mapa(pares):
        return ("RwLock::new([" + ", ".join(f'("{k}", "{v}")' for k, v in pares)
                + "].iter().map(|(k, v)| (k.to_string(), v.to_string())).collect())")
    sustituir(src, "libs/hbb_common/src/config.rs", [
        ("pub static ref OVERWRITE_SETTINGS: RwLock<HashMap<String, String>> = Default::default();",
         "pub static ref OVERWRITE_SETTINGS: RwLock<HashMap<String, String>> = "
         + mapa([("allow-auto-update", "Y")]) + ";"),
        ("pub static ref BUILTIN_SETTINGS: RwLock<HashMap<String, String>> = Default::default();",
         "pub static ref BUILTIN_SETTINGS: RwLock<HashMap<String, String>> = "
         + mapa([("hide-server-settings", "Y"), ("hide-proxy-settings", "Y"),
                 ("hide-websocket-settings", "Y"), ("hide-help-cards", "Y")]) + ";"),
        ("pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = Default::default();",
         "pub static ref HARD_SETTINGS: RwLock<HashMap<String, String>> = "
         + mapa([("disable-account", "Y"), ("disable-ab", "Y")] + VARIANTES[NOMBRE_APP]) + ";"),
    ])
    sustituir(src, "src/common.rs", [
        ('const KEY: &str = "5Qbwsde3unUcJBtrx9ZkvUmwFNoExHzpryHuPUdqlWM=";',
         f'const KEY: &str = "{CLAVE_FIRMA_CUSTOM}";'),
    ])

    print("4a. Iconos y logos")
    copiar(src, "icon.png", ["flutter/assets/icon.png", "res/icon.png"])
    copiar(src, "icon.svg", ["flutter/assets/icon.svg"])
    copiar(src, "icon.ico", ["flutter/assets/icon.ico", "res/icon.ico"])
    copiar(src, "app_icon.ico", ["flutter/windows/runner/resources/app_icon.ico"])
    for n in ("logo.png", "logo_light.png", "logo_dark.png"):
        copiar(src, n, [f"flutter/assets/{n}"])
    for n in ("32x32.png", "64x64.png", "128x128.png", "128x128@2x.png"):
        copiar(src, n, [f"res/{n}"])

    print("4b. Textos de versión del ejecutable")
    sustituir(src, "flutter/windows/runner/Runner.rc", [
        ('VALUE "CompanyName", "Purslane Tech Pte. Ltd."', f'VALUE "CompanyName", "{EMPRESA}"'),
        ('VALUE "FileDescription", "RustDesk Remote Desktop"', f'VALUE "FileDescription", "{DESCRIPCION}"'),
        ('VALUE "LegalCopyright", "Copyright © 2026 Purslane Tech Pte. Ltd. All rights reserved."',
         f'VALUE "LegalCopyright", "{COPYRIGHT}"'),
        ('VALUE "ProductName", "RustDesk"', f'VALUE "ProductName", "{PRODUCTO}"'),
    ])
    sustituir(src, "Cargo.toml", [
        ('LegalCopyright = "Copyright © 2026 Purslane Tech Pte. Ltd. All rights reserved."',
         f'LegalCopyright = "{COPYRIGHT}"'),
        ('ProductName = "RustDesk"', f'ProductName = "{PRODUCTO}"'),
        ('FileDescription = "RustDesk Remote Desktop"', f'FileDescription = "{DESCRIPCION}"'),
    ])
    print("5. Versión propia y actualización automática desde nuestro repositorio")
    # Versión 1.5.0 -> 1.5.0-<revisión>: al comparar, RustDesk suma lo que va tras el guion
    p = os.path.join(src, "Cargo.toml")
    with open(p, encoding="utf-8") as f:
        toml = f.read()
    ver = toml.split('version = "', 1)[1].split('"', 1)[0]
    with open(p, "w", encoding="utf-8") as f:
        f.write(toml.replace(f'version = "{ver}"', f'version = "{ver}-{revision}"', 1))
    print(f"  OK Cargo.toml: versión {ver}-{revision}")
    # build.py compila con --locked: Cargo.lock tiene que llevar la misma versión del paquete
    sustituir(src, "Cargo.lock", [
        (f'name = "rustdesk"\nversion = "{ver}"', f'name = "rustdesk"\nversion = "{ver}-{revision}"'),
    ])
    # Consulta de la última versión: antes POST a api.rustdesk.com, ahora GET a nuestro latest.json
    sustituir(src, "libs/hbb_common/src/lib.rs", [
        ('const URL: &str = "https://api.rustdesk.com/version/latest";',
         f'const URL: &str = "{URL_ULTIMA}";'),
    ])
    sustituir(src, "src/common.rs", [
        ("client.post(&url).json(&request).send()", "client.get(&url).send()"),
        ("hbb_common::version_check_request(hbb_common::VER_TYPE_RUSTDESK_CLIENT.to_string());",
         "hbb_common::version_check_request(hbb_common::VER_TYPE_RUSTDESK_CLIENT.to_string());\n"
         "    let _ = &request; // ISPE: ya no se envía, la consulta es un GET"),
    ])
    # Descarga: el .exe de la variante instalada (ISPE-Soporte / ISPE-Tecnico), solo de nuestras releases
    sustituir(src, "src/updater.rs", [
        ('"{}/rustdesk-{}-{}.{}",\n                download_url,\n                version,',
         '"{}/{}-{}-{}.{}",\n                download_url,\n                crate::get_app_name(),\n                version,'),
        ('if owner != "rustdesk"\n        || repo != "rustdesk"',
         f'if owner != "{REPO_DUENO}"\n        || repo != "{REPO_NOMBRE}"'),
    ])
    print(f"Marca ISPE aplicada (versión {ver}-{revision}).")


if __name__ == "__main__":
    main()
