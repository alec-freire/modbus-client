import argparse
import logging
import time

from modbus.client import ModbusClientRS485
from modbus.reader import read_profile
from settings import load_settings


# =========================
# MAIN
# =========================

def main():
    parser = argparse.ArgumentParser(description="Modbus client - leitura de perfis")
    parser.add_argument(
        "--config",
        help="Caminho do arquivo INI (padrão: ./config.ini ou env MODBUS_CONFIG)",
    )
    args = parser.parse_args()

    cfg = load_settings(args.config)

    logging.basicConfig(
        level=getattr(logging, cfg.logging.level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    log = logging.getLogger("main")

    client = ModbusClientRS485(
        port=cfg.modbus.port,
        baudrate=cfg.modbus.baudrate,
        parity=cfg.modbus.parity,
        stopbits=cfg.modbus.stopbits,
        bytesize=cfg.modbus.bytesize,
        timeout=cfg.modbus.timeout,
        retries=cfg.modbus.retries,
        slave_id=cfg.modbus.slave_id,
    )

    while True:
        try:
            log.info("Conectando ao Modbus...")
            client.connect()

            while True:
                data = read_profile(
                    client,
                    profile=cfg.read.profile,
                    base_address=cfg.read.base_address,
                    slave_id=cfg.modbus.slave_id,
                )

                log.info("Dados lidos: %s", data)
                time.sleep(cfg.read.interval_seconds)

        except Exception as e:
            log.error("Erro: %s", e)
            time.sleep(3)

        finally:
            try:
                client.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
