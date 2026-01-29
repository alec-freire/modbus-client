import logging
import time

from modbus.client import ModbusClientRS485
from modbus.reader import read_profile

# =========================
# CONFIGURAÇÕES
# =========================

PORT = "COM12"           # Windows -> COM3 | Linux -> /dev/ttyUSB0
SLAVE_ID = 1
BASE_ADDRESS = 0      # se não funcionar, teste 1

LOG_LEVEL = logging.INFO


# =========================
# MAIN
# =========================

def main():
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    log = logging.getLogger("main")

    client = ModbusClientRS485(
        port=PORT,
        baudrate=9600,
        slave_id=SLAVE_ID,
    )

    while True:
        try:
            log.info("Conectando ao Modbus...")
            client.connect()

            while True:
                data = read_profile(
                    client,
                    profile="basic",
                    base_address=BASE_ADDRESS,
                    slave_id=SLAVE_ID,
                )

                log.info("Dados lidos: %s", data)
                time.sleep(1)

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
