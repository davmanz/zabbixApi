from dotenv import load_dotenv
import os
from zabbix_connector import ZabbixManager

load_dotenv()

ZP_KEY=os.getenv("ZABBIX_API")
ZB_SERVER=os.getenv("ZABBIX_SERVER")

if __name__ == "__main__":
    zb = ZabbixManager(url=f"http://{ZB_SERVER}/api_jsonrpc.php", token=ZP_KEY)
    zb.connect()
    groups = zb.get_host_groups()

    print("📦 Grupos disponibles en Zabbix:")
    for group in groups:
        print(f"➡️  {group['name']} (ID: {group['groupid']})")  