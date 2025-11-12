import csv

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

def create_comparison_csv(devices_csv, zabbix_csv, output_csv="comparison_result.csv"):
    """
    Crea un CSV con todos los hosts de devices_csv y su status respecto a Zabbix.
    Busca coincidencias parciales: si el hostname de devices está contenido en algún hostname de Zabbix.
    """
    try:
        devices_hosts = get_hosts_from_csv(devices_csv)
        zabbix_hosts = get_hosts_from_csv(zabbix_csv)

        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Hostname", "Status"])  # Encabezados
            for host in devices_hosts:
                # Verificar si el host está contenido en algún host de Zabbix
                status = "No en Zabbix"
                for z_host in zabbix_hosts:
                    if host in z_host:
                        status = "En Zabbix"
                        break
                writer.writerow([host, status])

        print(f"✅ Comparación completada. Resultado guardado en {output_csv}")
    except Exception as e:
        print(f"❌ Error al crear el CSV de comparación: {e}")

if __name__ == "__main__":
    devices_csv = "host.csv"
    zabbix_csv = "zabbix_hosts.csv"
    output_csv = "comparison_result.csv"

    create_comparison_csv(devices_csv, zabbix_csv, output_csv)