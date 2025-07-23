# Proyecto de Automatización con Zabbix API

Este proyecto contiene un conjunto de scripts de Python para interactuar con la API de Zabbix, permitiendo automatizar tareas comunes como la creación de hosts, la consulta de grupos y la gestión de plantillas.

## ⚙️ Configuración

Antes de usar los scripts, necesitas configurar las credenciales de acceso a la API de Zabbix.

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd zabbixApi
    ```

2.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Crea un archivo `.env`** en la raíz del proyecto. Puedes renombrar el archivo `.env.example` (si existiera) o crearlo desde cero con el siguiente contenido:

    ```env
    # URL del servidor Zabbix (sin /api_jsonrpc.php)
    ZABBIX_SERVER="192.168.1.100" 

    # Token de la API de Zabbix
    ZABBIX_API="tu_token_de_api_aqui"
    ```

    Asegúrate de reemplazar los valores con los de tu entorno Zabbix.

---

## 🚀 Scripts Disponibles

A continuación se describen los scripts y cómo utilizarlos.

### 1. `zabbix_host_group.py`

Este script obtiene y lista todos los grupos de hosts disponibles en tu Zabbix. Es útil para obtener los `groupid` que necesitas para crear o asignar hosts.

**Uso:**

```bash
python zabbix_host_group.py
```

**Salida de ejemplo:**

```
🔄 Connecting to the Zabbix API...
✅ Connected to Zabbix API version 6.4.8
📦 Grupos disponibles en Zabbix:
➡️  Linux servers (ID: 4)
➡️  Windows servers (ID: 2)
➡️  Network devices (ID: 13)
```

### 2. `zabbix_templates.py`

Lista todas las plantillas de monitoreo disponibles en Zabbix. Al igual que el script de grupos, te ayuda a encontrar los `templateid` necesarios para asignarlos a nuevos hosts.

**Uso:**

```bash
python zabbix_templates.py
```

**Salida de ejemplo:**

```
🔄 Connecting to the Zabbix API...
✅ Connected to Zabbix API version 6.4.8
🔍 Obteniendo plantillas desde Zabbix...
✅ Se encontraron 152 plantillas.
📦 Plantillas disponibles en Zabbix:
➡️  Template OS Linux by Zabbix agent (ID: 10186)
➡️  Template OS Windows by Zabbix agent (ID: 10192)
➡️  ICMP Ping (ID: 10001)
```

### 3. `zabbix_get_host_by_ip.py`

Busca y muestra información de hosts en Zabbix basándose en una o más direcciones IP que se pasan como argumento.

**Uso:**

Pasa las direcciones IP que quieres buscar como argumentos separados por espacios.

```bash
python zabbix_get_host_by_ip.py 192.168.1.50 10.0.0.25
```

**Salida de ejemplo:**

```
🔄 Connecting to the Zabbix API...
✅ Connected to Zabbix API version 6.4.8
🖥️ Hosts encontrados por IP:
➡️  web-server-01 (ID: 10591, IP: 192.168.1.50)
➡️  db-server-prod (ID: 10624, IP: 10.0.0.25)
```

### 4. `zabbix_create_host_csv.py`

Crea hosts en Zabbix de forma masiva a partir de un archivo `hosts_import.csv`.

**Preparación:**

Crea un archivo llamado `hosts_import.csv` en la misma carpeta con las siguientes columnas:

| hostname     | ip            | group_ids | visible_name      | description       | tags                      | templates         | ping_only | mac               |
|--------------|---------------|-----------|-------------------|-------------------|---------------------------|-------------------|-----------|-------------------|
| server-01    | 192.168.1.10  | 4,13      | Web Server 01     | Servidor web principal | `marca=HP;os=Linux`       | `10186`           | `false`   | `00:1A:2B:3C:4D:5E` |
| server-02    | 192.168.1.11  | 2         | DB Server         | Servidor de base de datos | `entorno=prod`            | `10192,10200`     | `false`   |                   |
| switch-core  | 192.168.0.1   | 13        | Core Switch       | Switch de red principal |                           |                   | `true`    |                   |

**Notas sobre las columnas:**
*   `group_ids` y `templates`: Deben ser los IDs numéricos, separados por comas.
*   `tags`: Pares `clave=valor` separados por punto y coma (`;`).
*   `ping_only`: Si es `true`, ignora la columna `templates` y asigna automáticamente una plantilla de ping.
*   `mac`: Si se proporciona, se añade como una tag `mac`.

**Uso:**

```bash
python zabbix_create_host_csv.py
```

El script leerá el archivo `hosts_import.csv` y comenzará a crear los hosts uno por uno, mostrando el progreso en la terminal.
