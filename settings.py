from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class ModbusSerialSettings:
    port: str
    baudrate: int = 9600
    parity: str = "N"
    stopbits: int = 1
    bytesize: int = 8
    timeout: float = 1.0
    retries: int = 3
    slave_id: int = 1


@dataclass(frozen=True)
class ReadSettings:
    base_address: int = 0
    profile: str = "basic"
    interval_seconds: float = 1.0


@dataclass(frozen=True)
class ScanSettings:
    baudrates: List[int]
    parities: List[str]
    slave_ids: List[int]
    test_address: int = 1
    test_count: int = 1
    timeout: float = 0.2
    retries: int = 1


@dataclass(frozen=True)
class LoggingSettings:
    level: str = "INFO"


@dataclass(frozen=True)
class Settings:
    modbus: ModbusSerialSettings
    read: ReadSettings
    scan: ScanSettings
    logging: LoggingSettings


def _parse_csv_ints(value: str) -> List[int]:
    items = [v.strip() for v in value.split(",") if v.strip()]
    return [int(v) for v in items]


def _parse_csv_strs(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def _parse_range_expr(expr: str) -> List[int]:
    """Aceita: "1-10" (inclusivo) ou "5"."""
    expr = expr.strip()
    if not expr:
        return []
    if "-" in expr:
        start_s, end_s = expr.split("-", 1)
        start = int(start_s.strip())
        end = int(end_s.strip())
        step = 1 if end >= start else -1
        return list(range(start, end + step, step))
    return [int(expr)]


def _parse_ranges(value: str) -> List[int]:
    """Aceita: "1-10" ou "1-10, 20, 30-35"."""
    parts = [p.strip() for p in value.split(",") if p.strip()]
    out: List[int] = []
    for part in parts:
        out.extend(_parse_range_expr(part))
    return out


def _env_override_str(section: str, key: str) -> Optional[str]:
    # Ex: MODBUS__MODBUS__PORT ou MODBUS__READ__PROFILE
    env_key = f"MODBUS__{section.upper()}__{key.upper()}"
    return os.environ.get(env_key)


def load_settings(config_path: str | None = None) -> Settings:
    """Carrega configurações do arquivo INI.

    Ordem de resolução:
    1) argumento config_path
    2) env MODBUS_CONFIG
    3) ./config.ini

    Variáveis de ambiente por chave (opcional):
    MODBUS__MODBUS__PORT, MODBUS__MODBUS__BAUDRATE, ...
    """

    if not config_path:
        config_path = os.environ.get("MODBUS_CONFIG")

    if not config_path:
        config_path = "config.ini"

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {path.resolve()}. "
            "Crie um config.ini a partir do config.example.ini, ou passe --config <arquivo>."
        )

    cfg = configparser.ConfigParser()
    cfg.read(path, encoding="utf-8")

    def get_str(section: str, key: str, fallback: Optional[str] = None) -> str:
        env_v = _env_override_str(section, key)
        if env_v is not None:
            return env_v
        return cfg.get(section, key, fallback=fallback)

    def get_int(section: str, key: str, fallback: Optional[int] = None) -> int:
        env_v = _env_override_str(section, key)
        if env_v is not None:
            return int(env_v)
        return cfg.getint(section, key, fallback=fallback)

    def get_float(section: str, key: str, fallback: Optional[float] = None) -> float:
        env_v = _env_override_str(section, key)
        if env_v is not None:
            return float(env_v)
        return cfg.getfloat(section, key, fallback=fallback)

    modbus = ModbusSerialSettings(
        port=get_str("modbus", "port"),
        baudrate=get_int("modbus", "baudrate", 9600),
        parity=get_str("modbus", "parity", "N"),
        stopbits=get_int("modbus", "stopbits", 1),
        bytesize=get_int("modbus", "bytesize", 8),
        timeout=get_float("modbus", "timeout", 1.0),
        retries=get_int("modbus", "retries", 3),
        slave_id=get_int("modbus", "slave_id", 1),
    )

    read = ReadSettings(
        base_address=get_int("read", "base_address", 0),
        profile=get_str("read", "profile", "basic"),
        interval_seconds=get_float("read", "interval_seconds", 1.0),
    )

    scan_baudrates_raw = get_str("scan", "baudrates", str(modbus.baudrate))
    scan_parities_raw = get_str("scan", "parities", modbus.parity)
    scan_slave_ids_raw = get_str("scan", "slave_ids", "0-246")

    scan = ScanSettings(
        baudrates=_parse_csv_ints(scan_baudrates_raw),
        parities=_parse_csv_strs(scan_parities_raw),
        slave_ids=_parse_ranges(scan_slave_ids_raw),
        test_address=get_int("scan", "test_address", 1),
        test_count=get_int("scan", "test_count", 1),
        timeout=get_float("scan", "timeout", 0.2),
        retries=get_int("scan", "retries", 1),
    )

    logging_cfg = LoggingSettings(
        level=get_str("logging", "level", "INFO"),
    )

    return Settings(modbus=modbus, read=read, scan=scan, logging=logging_cfg)
