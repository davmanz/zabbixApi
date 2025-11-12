from dotenv import load_dotenv
import os
import csv
from zabbix_connector import ZabbixManager

load_dotenv()

ZP_KEY = os.getenv("ZABBIX_API")
ZB_SERVER = os.getenv("ZABBIX_SERVER")

def get_hosts_from_csv(csv_file):
    """
    Lee el archivo CSV y devuelve una lista de hostnames.
    """
    try:
        hosts = []
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hostname = row.get('Host')  # Cambiado de 'Hostname' a 'Host'
                if hostname:
                    hosts.append(hostname.strip())
        return hosts
    except FileNotFoundError:
        print(f"❌ Error: Archivo {csv_file} no encontrado.")
        return []
    except Exception as e:
        print(f"❌ Error al leer {csv_file}: {e}")
        return []

def export_zabbix_hosts_to_csv(zb, filename="zabbix_hosts.csv"):
    """
    Exporta todos los hosts de Zabbix con información completa a un archivo CSV.
    """
    try:
        hosts = zb.get_raw_hosts()  # Obtiene datos completos
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Host", "Name", "IP", "Groups", "Tags"])  # Encabezados
            for host in hosts:
                host_name = host.get('host', '')
                visible_name = host.get('name', '')
                # Extraer IP de interfaces
                ip = ''
                if host.get('interfaces'):
                    ip = host['interfaces'][0].get('ip', '') if host['interfaces'] else ''
                # Extraer grupos
                groups = ', '.join([g.get('name', '') for g in host.get('groups', [])])
                # Extraer tags
                tags = ', '.join([f"{t.get('tag', '')}:{t.get('value', '')}" for t in host.get('tags', [])])
                writer.writerow([host_name, visible_name, ip, groups, tags])
        print(f"✅ Hosts de Zabbix exportados con información completa a {filename}")
    except Exception as e:
        print(f"❌ Error al exportar hosts a {filename}: {e}")

def find_missing_hosts(devices_csv, zabbix_csv):
    """
    Compara dos CSVs: dispositivos y hosts de Zabbix, devuelve hosts faltantes en Zabbix.
    """
    devices_hosts = get_hosts_from_csv(devices_csv)
    zabbix_hosts = get_hosts_from_csv(zabbix_csv)
    zabbix_set = set(zabbix_hosts)
    missing = [host for host in devices_hosts if host not in zabbix_set]
    return missing

if __name__ == "__main__":
    try:
        devices_csv = "host.csv"
        zabbix_csv = "zabbix_hosts.csv"

        # Conectar a Zabbix
        zb = ZabbixManager(url=f"http://{ZB_SERVER}/api_jsonrpc.php", token=ZP_KEY)
        zb.connect()

        # Exportar hosts de Zabbix a CSV
        export_zabbix_hosts_to_csv(zb, zabbix_csv)

        # Leer hosts del CSV de dispositivos
        devices_hosts = get_hosts_from_csv(devices_csv)
        print(f"📄 Hosts en {devices_csv}: {len(devices_hosts)}")

        # Leer hosts del CSV de Zabbix
        zabbix_hosts = get_hosts_from_csv(zabbix_csv)
        print(f"🔍 Hosts en {zabbix_csv}: {len(zabbix_hosts)}")

        # Encontrar faltantes
        missing_hosts = find_missing_hosts(devices_csv, zabbix_csv)
        print(f"❓ Hosts faltantes en Zabbix: {len(missing_hosts)}")

        if missing_hosts:
            print("\nHosts que están en el CSV de dispositivos pero no en Zabbix:")
            for host in missing_hosts:
                print(f"- {host}")
        else:
            print("Todos los hosts del CSV están en Zabbix.")
    except Exception as e:
        print(f"❌ Error general en la ejecución: {e}")