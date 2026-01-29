from __future__ import annotations

import time
import logging
from typing import List

from pymodbus.client import ModbusSerialClient


# =========================
# CONFIGURAÇÕES PADRÃO
# =========================

DEFAULT_TIMEOUT = 1.0
DEFAULT_RETRIES = 3


# =========================
# CLIENTE MODBUS
# =========================

class ModbusClientRS485:
    """
    Cliente Modbus RTU (RS-485) simples e confiável.
    Responsável SOMENTE pela comunicação.
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        parity: str = "N",
        stopbits: int = 1,
        bytesize: int = 8,
        timeout: float = DEFAULT_TIMEOUT,
        slave_id: int = 0,
        retries: int = DEFAULT_RETRIES,
        logger: logging.Logger | None = None,
    ):
        self.port = port
        self.slave_id = slave_id
        self.retries = retries

        self.logger = logger or logging.getLogger("modbus-client")

        self.client = ModbusSerialClient(
            method="rtu",
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            timeout=timeout,
        )

    # =========================
    # CONEXÃO
    # =========================

    def connect(self) -> None:
        if not self.client.connect():
            raise ConnectionError(f"Falha ao conectar na porta {self.port}")
        self.logger.info("Conectado ao Modbus RTU (%s)", self.port)

    def close(self) -> None:
        self.client.close()
        self.logger.info("Conexão Modbus encerrada")

    # =========================
    # LEITURA
    # =========================

    def read_holding(self, address: int, count: int) -> List[int]:
        """
        Leitura crua de holding registers.
        Retorna lista de WORDs (int).
        """
        last_error = None

        for attempt in range(1, self.retries + 1):
            try:
                resp = self.client.read_holding_registers(
                    address=address,
                    count=count,
                    slave=self.slave_id,
                )

                if resp and not resp.isError():
                    return list(resp.registers)

                last_error = resp

            except Exception as e:
                last_error = e

            self.logger.warning(
                "Erro Modbus (tentativa %d/%d) addr=%d count=%d",
                attempt,
                self.retries,
                address,
                count,
            )
            time.sleep(0.1)

        raise RuntimeError(
            f"Falha lendo holding registers addr={address} count={count}: {last_error}"
        )

    # =========================
    # ESCRITA
    # =========================

    def write_single(self, address: int, value: int) -> None:
        """
        Escrita de um único WORD (FC06).
        """
        resp = self.client.write_register(
            address=address,
            value=value,
            slave=self.slave_id,
        )

        if resp is None or resp.isError():
            raise RuntimeError(f"Erro escrevendo register addr={address}")

        self.logger.debug("Write single addr=%d value=%d", address, value)

    def write_multiple(self, address: int, values: List[int]) -> None:
        """
        Escrita de múltiplos WORDs (FC16).
        """
        resp = self.client.write_registers(
            address=address,
            values=values,
            slave=self.slave_id,
        )

        if resp is None or resp.isError():
            raise RuntimeError(f"Erro escrevendo registers addr={address}")

        self.logger.debug(
            "Write multiple addr=%d count=%d", address, len(values)
        )
