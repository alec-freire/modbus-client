from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

from modbus.registers import REGISTERS  # 

# =========================
# CONFIG DE LEITURA
# =========================

# Alguns equipamentos enviam DWORD como HI,LO (word alta depois word baixa)
# Outros enviam LO,HI. Troque aqui se os valores DWORD vierem errados.
DWORD_ORDER = "HI_LO"  # "HI_LO" ou "LO_HI"


# =========================
# ERROS
# =========================

class ModbusReadError(RuntimeError):
    pass


# =========================
# FUNÇÕES AUXILIARES
# =========================

def resolve_address(offset: int, base_address: int) -> int:
    """Converte offset (+N do manual) para o address do pymodbus."""
    return base_address + offset


def apply_decimals(value: int | float, decimals: int) -> float:
    if decimals <= 0:
        return float(value)
    return float(value) / (10 ** decimals)


def decode_bits(word: int, bit_map: Dict[int, str]) -> Dict[str, bool]:
    """Retorna dict com nome_do_bit -> True/False"""
    out: Dict[str, bool] = {}
    for bit, name in bit_map.items():
        out[name] = bool((word >> bit) & 1)
    return out


def decode_u32(words: List[int], order: str) -> int:
    """Decodifica DWORD (2 WORDs) para uint32."""
    if len(words) != 2:
        raise ValueError("DWORD precisa de 2 WORDs")

    w0, w1 = words[0], words[1]

    if order.upper() == "HI_LO":
        hi, lo = w0, w1
    elif order.upper() == "LO_HI":
        lo, hi = w0, w1
    else:
        raise ValueError("DWORD_ORDER inválido. Use 'HI_LO' ou 'LO_HI'.")

    return (hi << 16) | lo


def _read_holding_registers(client, address: int, count: int, slave_id: int) -> List[int]:
    """Leitura crua (holding registers)."""
    return client.read_holding(address=address, count=count)


# =========================
# LEITURA POR VARIÁVEL
# =========================

def read_one(client, key: str, *, base_address: int = 0, slave_id: int = 1) -> Any:
    """Lê uma variável pelo key do REGISTERS."""
    spec = REGISTERS[key]
    offset = spec["offset"]
    rtype = spec["type"]

    address = resolve_address(offset, base_address)

    if rtype == "u16":
        words = _read_holding_registers(client, address, 1, slave_id)
        raw = words[0]
        if "bits" in spec:
            return decode_bits(raw, spec["bits"])
        decimals = int(spec.get("decimals", 0))
        return apply_decimals(raw, decimals)

    if rtype == "u32":
        words = _read_holding_registers(client, address, 2, slave_id)
        raw32 = decode_u32(words, DWORD_ORDER)
        decimals = int(spec.get("decimals", 0))
        return apply_decimals(raw32, decimals)

    raise ValueError(f"Tipo não suportado: {rtype!r} (key={key})")


# =========================
# LEITURA EM BLOCO (PERFORMANCE)
# =========================

def _calc_word_span(keys: List[str]) -> Tuple[int, int]:
    """
    Calcula a faixa mínima [min_offset, max_offset_inclusive] em WORDs,
    considerando u16 (1 word) e u32 (2 words).
    """
    min_off = None
    max_off = None

    for k in keys:
        s = REGISTERS[k]
        off = int(s["offset"])
        size = 2 if s["type"] == "u32" else 1

        if min_off is None or off < min_off:
            min_off = off
        end = off + size - 1
        if max_off is None or end > max_off:
            max_off = end

    if min_off is None or max_off is None:
        raise ValueError("keys vazio")
    return min_off, max_off


def read_many_block(client, keys: List[str], *, base_address: int = 0, slave_id: int = 1) -> Dict[str, Any]:
    """
    Lê várias variáveis individualmente (modo seguro).
    Equipamentos com endereços não-contíguos podem falhar em leitura de bloco.
    """
    out: Dict[str, Any] = {}
    
    for k in keys:
        try:
            out[k] = read_one(client, k, base_address=base_address, slave_id=slave_id)
        except Exception as e:
            # Se falhar, registra mas continua com as outras
            out[k] = None
            import logging
            logging.getLogger(__name__).warning(f"Falha lendo {k}: {e}")
    
    return out


# =========================
# PERFIS DE LEITURA
# =========================

PROFILES: Dict[str, List[str]] = {
    # básico pra validar comunicação e já ver algo útil
    "basic": [
        "actual_throughput_kgh",
        "mdw_status",
        "batch_value_g",
        "blend_weight_kg",
        "station_1_setpoint",
        "station_2_setpoint",
        "station_3_setpoint",
        "station_4_setpoint",
        "station_5_setpoint",
        "station_6_setpoint",
    ],

    # alarmes e I/O
    "alarms": [
        "mdw_status",
        "alarms_word_1",
        "alarms_word_2",
        "alarms_word_3",
        "digital_inputs",
        "digital_outputs",
    ],

    # produção (dosed)
    "production": [
        "actual_throughput_kgh",
        "station_1_dosed_g",
        "station_2_dosed_g",
        "station_3_dosed_g",
        "station_4_dosed_g",
        "station_5_dosed_g",
        "station_6_dosed_g",
    ],
}


def read_profile(client, profile: str, *, base_address: int = 0, slave_id: int = 1) -> Dict[str, Any]:
    keys = PROFILES.get(profile)
    if not keys:
        raise ValueError(f"Perfil inválido: {profile}. Disponíveis: {list(PROFILES)}")
    return read_many_block(client, keys, base_address=base_address, slave_id=slave_id)
