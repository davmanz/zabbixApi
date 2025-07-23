from dotenv import load_dotenv
import os
import sys
from zabbix_connector import ZabbixManager

load_dotenv()

ZP_KEY = os.getenv("ZABBIX_API")
ZB_SERVER = os.getenv("ZABBIX_SERVER")

def find_hosts_by_ip(zb, ip_list):
    """
    Busca hosts en Zabbix que coincidan con una lista de IPs.
    """
    if not ip_list:
        print("⚠️ No se proporcionaron IPs para buscar.")
        return []

    # Prepara el filtro para la API de Zabbix
    search_filter = {"ip": ip_list}
    
    try:
        # Llama a la API con el filtro
        hosts = zb.zapi.host.get(
            output=["hostid", "host", "name"],
            selectInterfaces=["ip"],
            filter=search_filter
        )
        return hosts
    except Exception as e:
        print(f"❌ Error al buscar hosts por IP: {e}")
        return []

if __name__ == "__main__":
    # Verifica si se pasaron IPs como argumentos
    if len(sys.argv) < 2:
        print("Uso: python zabbix_get_host_by_ip.py <ip1> <ip2> ... <ipN>")
        sys.exit(1)

    # Extrae las IPs de los argumentos de la línea de comandos
    ip_list_to_find = sys.argv[1:]

    # Conecta con Zabbix
    zb = ZabbixManager(url=f"http://{ZB_SERVER}/api_jsonrpc.php", token=ZP_KEY)
    zb.connect()

    # Busca los hosts
    matching_hosts = find_hosts_by_ip(zb, ip_list_to_find)

    if matching_hosts:
        print("🖥️ Hosts encontrados por IP:")
        for host in matching_hosts:
            # Extrae la IP de la interfaz para mostrarla
            ip_found = "N/A"
            if host.get("interfaces"):
                ip_found = host["interfaces"][0]["ip"]
            
            print(f"➡️ {host['host']} (ID: {host['hostid']}, IP: {ip_found})")
    else:
        print("🤷 No se encontraron hosts para las IPs proporcionadas.")