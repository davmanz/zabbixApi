from dotenv import load_dotenv
import os
from zabbix_connector import ZabbixManager

load_dotenv()

ZP_KEY = os.getenv("ZABBIX_API")
ZB_SERVER = os.getenv("ZABIX_SERVER")

if __name__ == "__main__":
    zb = ZabbixManager(url=f"http://{ZB_SERVER}/api_jsonrpc.php", token=ZP_KEY)
    zb.connect()

    try:
        templates = zb.zapi.template.get(output=["templateid", "name"])
        print("📦 Plantillas disponibles en Zabbix:")
        for tpl in templates:
            print(f"➡️  {tpl['name']} (ID: {tpl['templateid']})")
    except Exception as e:
        print(f"❌ Error al obtener templates: {e}")
