from dotenv import load_dotenv
import os
from zabbix_connector import ZabbixManager

load_dotenv()

ZP_KEY = os.getenv("ZABBIX_API")
ZB_SERVER = os.getenv("ZABBIX_SERVER")

if __name__ == "__main__":
    zb = ZabbixManager(url=f"http://{ZB_SERVER}/api_jsonrpc.php", token=ZP_KEY)
    zb.connect()

    # Obtenemos las plantillas usando el nuevo método del conector
    templates = zb.get_templates()

    if templates:
        print("📦 Plantillas disponibles en Zabbix:")
        for tpl in templates:
            print(f"➡️  {tpl['name']} (ID: {tpl['templateid']})")
    else:
        print("🤷 No se encontraron plantillas o hubo un error.")