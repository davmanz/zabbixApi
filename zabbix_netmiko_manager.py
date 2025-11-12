import csv
from ping3 import ping
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException
import os
from dotenv import load_dotenv

load_dotenv()

class NetmikoManager:
    def __init__(self):
        self.usuario_no_radius = os.getenv("USUARIO_NO_RADIUS")
        self.clave = os.getenv("CLAVE")
        self.usuario_radius = os.getenv("USUARIO_RADIUS")
        self.clave_radius = os.getenv("CLAVE_RADIUS", self.clave)  # Usa CLAVE si no hay CLAVE_RADIUS

    def ping_host(self, ip, timeout=1):
        """
        Hace ping a una IP usando ping3 y devuelve True si responde, False si no.
        """
        try:
            result = ping(ip, timeout=timeout)
            return result is not None and result is not False
        except Exception:
            return False

    def test_ssh_connection(self, ip, username, password):
        """
        Intenta conectar via SSH primero con Huawei, si falla con Cisco.
        Devuelve el device_type exitoso o None.
        """
        device_types = ['huawei', 'cisco_ios']
        for device_type in device_types:
            try:
                device = {
                    'device_type': device_type,
                    'host': ip,
                    'username': username,
                    'password': password,
                    'timeout': 10,
                }
                with ConnectHandler(**device):
                    return device_type  # Devolver el tipo que funcionó
            except (NetMikoTimeoutException, NetMikoAuthenticationException, Exception):
                continue  # Intentar el siguiente
        return None

    def process_hosts_from_csv(self, csv_file, output_csv="netmiko_results.csv"):
        """
        Procesa hosts de csv_file: ping y SSH con ambos usuarios, guarda en output_csv.
        """
        try:
            results = []
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    ip = row.get('IP', '').strip()
                    host = row.get('Host', '').strip()
                    if ip:
                        ping_ok = self.ping_host(ip)
                        ssh_no_radius = self.test_ssh_connection(ip, self.usuario_no_radius, self.clave)
                        ssh_radius = self.test_ssh_connection(ip, self.usuario_radius, self.clave_radius)
                        ssh_ok = ssh_no_radius is not None or ssh_radius is not None
                        device_type = ssh_no_radius if ssh_no_radius else ssh_radius  # Tomar el primero que funcionó
                    else:
                        ping_ok = False
                        ssh_ok = False
                        ssh_no_radius = None
                        ssh_radius = None
                        device_type = None

                    results.append({
                        "Hostname": host,
                        "IP": ip,
                        "Ping_OK": ping_ok,
                        "SSH": ssh_ok,
                        "NO_RADIUS": ssh_no_radius is not None,
                        "RADIUS": ssh_radius is not None,
                        "Device_Type": device_type
                    })

            # Guardar en CSV
            with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["Hostname", "IP", "Ping_OK", "SSH", "NO_RADIUS", "RADIUS", "Device_Type"])
                writer.writeheader()
                writer.writerows(results)

        except FileNotFoundError:
            print(f"❌ Error: Archivo {csv_file} no encontrado.")
        except Exception as e:
            print(f"❌ Error al procesar {csv_file}: {e}")

if __name__ == "__main__":
    manager = NetmikoManager()
    csv_file = "HOST_FILTRADOS.csv"
    output_csv = "netmiko_results.csv"
    manager.process_hosts_from_csv(csv_file, output_csv)