# Variantes del cliente

Cada `.json` es la personalización de una variante. El workflow la firma con el secreto
`ISPE_FIRMA` y la deja como `custom.txt` junto al ejecutable, igual que hace RustDesk Pro.

- **ISPE-Soporte**: para los equipos de los clientes. Solo recibe conexiones (`conn-type: incoming`).
  Servidor bloqueado, se actualiza solo. Se instala como servicio (acceso desatendido con contraseña
  permanente) o se ejecuta sin instalar para un soporte puntual.
- **ISPE-Tecnico**: para los técnicos de ISPE. Cliente completo (conecta y recibe), servidor bloqueado.

Las claves admitidas están en `libs/base/src/config/keys.rs` de RustDesk (`KEYS_SETTINGS`,
`KEYS_BUILDIN_SETTINGS`…). Las que no van en `default-settings` ni en `override-settings`
(`conn-type`, `disable-*`) se aplican como ajustes fijos.
