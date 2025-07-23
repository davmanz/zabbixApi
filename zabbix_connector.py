import csv
from zabbix_utils import ZabbixAPI

class ZabbixManager:
    def __init__(self, url, token):

        self.url = url
        self.token = token
        self.zapi = None

    def connect(self):
        print("🔄 Connecting to the Zabbix API...")
        try:
            self.zapi = ZabbixAPI(url=self.url, token=self.token)
            version = self.zapi.apiinfo.version()
            print(f"✅ Connected to Zabbix API version {version}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Zabbix API: {e}")
            exit()
            return False

    def get_host_groups(self, group_names=None):

        try:
            params = {"output": ["groupid", "name"]}
            if group_names:
                params["filter"] = {"name": group_names}

            return self.zapi.hostgroup.get(**params)
        except Exception as e:
            print(f"❌ Failed to get host groups: {e}")
            return []

    def get_raw_hosts(self, group_ids=None):

        print("🔍 Fetching raw host data from Zabbix...")
        try:
            params = {
                "output": ["hostid", "host", "name"],
                "selectInterfaces": ["interfaceid", "ip"],
                "selectGroups": ["name"],
                "selectTags": ["tag", "value"],
            }
            if group_ids:
                params["groupids"] = group_ids

            return self.zapi.host.get(**params)
        except Exception as e:
            print(f"❌ Failed to get raw hosts: {e}")
            return []

    def get_processed_hosts(self, group_ids=None, tag_name="marca"):
        hosts = self.get_raw_hosts(group_ids)
        processed = []

        for host in hosts:
            host_id = host["hostid"]
            hostname = host["host"]
            visible_name = host["name"]
            ip = host["interfaces"][0]["ip"] if host.get("interfaces") else "No IP"
            groups = {g["name"] for g in host.get("groups", [])}  # ← set sin duplicados
            tag_value = self._extract_tag_value(host.get("tags", []), tag_name)

            processed.append(
                {
                    "hostid": host_id,
                    "hostname": hostname,
                    "name": visible_name,
                    "ip": ip,
                    "groups": groups,
                    "tags": tag_value,
                }
            )

        return processed

    def _extract_tag_value(self, tags, tag_name):

        for tag in tags:
            if tag["tag"] == tag_name:
                return tag["value"]
        return None

    def export_hosts_to_csv(self, hosts, filename="zabbix_hosts_export.csv"):

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(
                    ["hostid", "host", "name", "ip", "groups", "tag"]
                )  # Header
                writer.writerows(hosts)
            print(f"✅ Hosts exported successfully to '{filename}'")
        except Exception as e:
            print(f"❌ Failed to export CSV: {e}")

    def create_host(self, hostname, ip, group_ids, description=None, tags=None, templates=None, visible_name=None, ping_only=False):
        """
        Crea un nuevo host en Zabbix.

        :param hostname: Nombre técnico (único) del host
        :param ip: Dirección IP del host
        :param group_ids: Lista de IDs de grupo (como strings)
        :param description: Descripción del host (opcional)
        :param tags: Lista de diccionarios [{'tag': 'marca', 'value': 'HP'}]
        :param templates: Lista de plantillas [{'templateid': '10001'}]
        :param visible_name: Nombre visible del host (opcional)
        :param ping_only: Si True, asocia plantilla de ping automáticamente
        """
        if not self.zapi:
            print("❌ Not connected to Zabbix API")
            return None

        if not hostname or not ip or not group_ids:
            print("❌ hostname, ip y group_ids son requeridos")
            return None

        if not isinstance(group_ids, list):
            print("❌ group_ids debe ser una lista")
            return None

        try:
            host_data = {
                "host": hostname,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": ip,
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": [{"groupid": gid} for gid in group_ids],
                "description": description or None
            }

            if visible_name:
                host_data["name"] = visible_name

            if tags:
                if isinstance(tags, list):
                    host_data["tags"] = tags
                else:
                    print("⚠️ 'tags' debe ser una lista de diccionarios")
                    return None

            # Si ping_only, asociar plantilla ICMP automáticamente
            if ping_only:
                ping_template_id = self._get_ping_template_id()
                if not ping_template_id:
                    print("❌ Plantilla ICMP Ping no encontrada.")
                    return None
                host_data["templates"] = [{"templateid": ping_template_id}]
            elif templates:
                if isinstance(templates, list):
                    host_data["templates"] = templates
                else:
                    print("⚠️ 'templates' debe ser una lista de diccionarios con 'templateid'")
                    return None

            result = self.zapi.host.create(**host_data)

            if "hostids" in result and result["hostids"]:
                print(f"✅ Host '{hostname}' creado exitosamente con ID {result['hostids'][0]}")
                return result
            else:
                print("⚠️ Host creado, pero no se recibió ID de retorno")
                return result

        except Exception as e:
            print(f"❌ Error al crear el host '{hostname}': {e}")
            return None

    def _get_ping_template_id(self):
        """
        Busca el ID de la plantilla de ICMP Ping.
        Retorna: templateid como string o None si no se encuentra.
        """
        try:
            templates = self.zapi.template.get(output=["templateid", "name"])
            for t in templates:
                if "ICMP Ping 5 minutos" in t["name"]:
                    return t["templateid"]
            return None
        except Exception as e:
            print(f"❌ Error buscando plantilla de ping: {e}")
            return None

    def get_templates(self, template_names=None):
        """
        Obtiene una lista de todas las plantillas o filtra por nombre.

        :param template_names: Lista de nombres de plantillas para filtrar (opcional).
        :return: Lista de diccionarios de plantillas.
        """
        print("🔍 Obteniendo plantillas desde Zabbix...")
        try:
            params = {"output": ["templateid", "name"]}
            if template_names:
                params["filter"] = {"name": template_names}
            
            templates = self.zapi.template.get(**params)
            print(f"✅ Se encontraron {len(templates)} plantillas.")
            return templates
        except Exception as e:
            print(f"❌ Error al obtener las plantillas: {e}")
            return []

    def create_host_csv(self, filename="hosts_import.csv"):
        """
        Crea múltiples hosts a partir de un archivo CSV.
        Columnas esperadas:
            hostname, ip, group_ids, visible_name, tags, templates, ping_only, mac
        """
        import csv

        if not self.zapi:
            print("❌ Not connected to Zabbix API")
            return

        try:
            with open(filename, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    hostname = row["hostname"].strip()
                    ip = row["ip"].strip()
                    group_ids = [gid.strip() for gid in row["group_ids"].split(",") if gid.strip()]
                    visible_name = row.get("visible_name", "").strip() or None
                    description = row.get("description", "").strip() or None
                    ping_only = row.get("ping_only", "false").strip().lower() == "true"

                    # Construcción de tags
                    tags = []
                    if row.get("tags"):
                        for tag_pair in row["tags"].split(";"):
                            if "=" in tag_pair:
                                tag, val = tag_pair.split("=", 1)
                                tags.append({"tag": tag.strip(), "value": val.strip()})

                    # Agregar MAC como tag si existe
                    if row.get("mac"):
                        tags.append({"tag": "mac", "value": row["mac"].strip()})

                    # Construcción de templates (si no es ping_only)
                    templates = []
                    if not ping_only and row.get("templates"):
                        templates = [{"templateid": tid.strip()} for tid in row["templates"].split(",") if tid.strip()]

                    # Crear host
                    print(f"🚀 Creando host: {hostname}")
                    self.create_host(
                        hostname=hostname,
                        ip=ip,
                        group_ids=group_ids,
                        tags=tags,
                        templates=templates,
                        visible_name=visible_name,
                        description=description,
                        ping_only=ping_only
                    )

        except Exception as e:
            print(f"❌ Error leyendo CSV: {e}")
