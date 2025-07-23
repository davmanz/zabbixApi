from dotenv import load_dotenv
import os
from zabbix_connector import ZabbixManager

load_dotenv()

ZP_KEY=os.getenv("ZABBIX_API")
ZB_SERVER=os.getenv("ZABBIX_SERVER")

if __name__ == "__main__":
    zb = ZabbixManager(url=f"http://{ZB_SERVER}/api_jsonrpc.php", token=ZP_KEY)
    zb.connect()

    zb.create_host_csv (filename="hosts_import.csv")