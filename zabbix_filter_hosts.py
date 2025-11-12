import csv

def filter_hosts_from_csv(input_csv, output_csv="HOST_FILTRADOS.csv"):
    """
    Filtra hosts de input_csv donde Host o Name contengan 'PE' y ('SW' o 'Switch').
    Guarda los resultados en output_csv con toda la información.
    """
    try:
        filtered_hosts = []
        with open(input_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                host = row.get('Host', '').upper()
                name = row.get('Name', '').upper()
                combined = host + ' ' + name  # Combinar para buscar en ambos
                if 'PE' in combined and ('SW' in combined or 'SWITCH' in combined):
                    filtered_hosts.append(row)

        if filtered_hosts:
            with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
                if filtered_hosts:
                    writer = csv.DictWriter(file, fieldnames=filtered_hosts[0].keys())
                    writer.writeheader()
                    writer.writerows(filtered_hosts)
            print(f"✅ Filtrado completado. {len(filtered_hosts)} hosts guardados en {output_csv}")
        else:
            print("⚠️ No se encontraron hosts que coincidan con los criterios.")
    except FileNotFoundError:
        print(f"❌ Error: Archivo {input_csv} no encontrado.")
    except Exception as e:
        print(f"❌ Error al filtrar hosts: {e}")

if __name__ == "__main__":
    input_csv = "zabbix_hosts.csv"
    output_csv = "HOST_FILTRADOS.csv"

    filter_hosts_from_csv(input_csv, output_csv)