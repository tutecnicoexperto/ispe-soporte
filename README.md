# ISPE Soporte

Cliente de asistencia remota de **ISPE Internet Seguro para Empresas**, basado en
[RustDesk](https://github.com/rustdesk/rustdesk) (AGPL-3.0) y conectado a nuestro servidor
`remoto.negociosdigitalesonline.es`.

## Descargas

En [Releases](../../releases/latest):

| Fichero | Para quién | Uso |
|---|---|---|
| `ISPE-Soporte-<ver>-x86_64.exe` | Clientes (solo recibe conexiones) | Doble clic: muestra ID y contraseña para un soporte puntual. Desde el propio programa se puede **instalar** (acceso desatendido). |
| `ISPE-Soporte-<ver>-x86_64.msi` | Clientes | Instalación silenciosa o masiva (`msiexec /i ... /qn`). |
| `ISPE-Tecnico-<ver>-x86_64.exe/.msi` | Técnicos de ISPE | Cliente completo para conectarse a los equipos. |

Acceso desatendido: tras instalar, fijar la contraseña permanente (como administrador):

```
"C:\Program Files\ISPE-Soporte\ISPE-Soporte.exe" --password <contraseña>
"C:\Program Files\ISPE-Soporte\ISPE-Soporte.exe" --get-id
```

## Cómo se genera una versión

1. **Actions › ISPE Soporte Windows › Run workflow**.
2. `version` = etiqueta oficial de RustDesk (p. ej. `1.5.0`), `revision` = 1-9 (nuestra revisión).
3. En ~1 h aparece la release `<version>-<revision>` con los `.exe` y `.msi` de cada variante.
4. Si «Publicar» está marcado, se actualiza `ispe/latest.json` y **los equipos instalados se
   actualizan solos** en las siguientes 24 h (solo cuando no hay ninguna sesión remota abierta).

Para cambiar logo o colores: `ispe/marca/` (regenerar con `ispe/dibujar_escudo.py` y
`ispe/generar_marca.py`). Para cambiar opciones de una variante: `VARIANTES` y los mapas de ajustes en `ispe/aplicar_marca.py`.

## Cómo funciona

- `ispe/aplicar_marca.py` parchea el código oficial descargado en cada compilación: servidor y
  clave, nombre, iconos, textos del ejecutable y la actualización automática (consulta
  `ispe/latest.json` y descarga solo de las releases de este repositorio).
- Cada variante se **compila por separado** con su nombre y sus ajustes fijos (`VARIANTES` en
  `ispe/aplicar_marca.py`): ISPE-Soporte con `conn-type=incoming`, ISPE-Tecnico completo.
- No se usa `custom.txt`: con él, el servidor que lanza el servicio de Windows en la sesión del
  usuario caía en bucle (pánico, código 0x3). `ispe/variantes/*.json` y `ispe/firmar_custom.py`
  quedan solo como referencia.

## Licencia

RustDesk se distribuye bajo **AGPL-3.0**; esta personalización también. El código fuente de cada
versión es este repositorio más `rustdesk/rustdesk` en la etiqueta indicada en la release.
