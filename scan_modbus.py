import argparse
import logging

from modbus.client import ModbusClientRS485
from settings import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan Modbus (baud/paridade/slave_id)")
    parser.add_argument(
        "--config",
        help="Caminho do arquivo INI (padrão: ./config.ini ou env MODBUS_CONFIG)",
    )
    args = parser.parse_args()

    cfg = load_settings(args.config)

    # Configura logger simples para não sujar a tela
    logging.basicConfig(level=logging.ERROR)

    print(f"--- INICIANDO SCAN NA PORTA {cfg.modbus.port} ---")

    encontrou = False

    for baud in cfg.scan.baudrates:
        for paridade in cfg.scan.parities:
            for slave_id in cfg.scan.slave_ids:
                print(
                    f"Tentando: Baud={baud} | Paridade={paridade} | ID={slave_id} ... ",
                    end="",
                )

                client = ModbusClientRS485(
                    port=cfg.modbus.port,
                    baudrate=baud,
                    parity=paridade,
                    stopbits=cfg.modbus.stopbits,
                    bytesize=cfg.modbus.bytesize,
                    slave_id=slave_id,
                    timeout=cfg.scan.timeout,
                    retries=cfg.scan.retries,
                )

                try:
                    client.connect()
                    val = client.read_holding(
                        address=cfg.scan.test_address,
                        count=cfg.scan.test_count,
                    )

                    print(f"✅ SUCESSO! Valor lido: {val}")
                    print(f"\n>>> CONFIGURAÇÃO CORRETA ENCONTRADA: <<<")
                    print(f"   Baudrate: {baud}")
                    print(f"   Paridade: '{paridade}'")
                    print(f"   Slave ID: {slave_id}")

                    encontrou = True
                    client.close()
                    break  # Sai do loop de IDs

                except Exception:
                    print("❌")
                    client.close()

            if encontrou:
                break  # Sai do loop de Paridade
        if encontrou:
            break  # Sai do loop de Baudrate

    if not encontrou:
        print("\n--- NENHUMA MÁQUINA ENCONTRADA ---")
        print("Dicas:")
        print("1. Inverta os fios A e B (Data+ e Data-).")
        print("2. Verifique se o ID na tela da máquina não é o mesmo da outra (se estiverem juntas).")


if __name__ == "__main__":
    main()