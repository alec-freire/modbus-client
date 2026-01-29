"""
Mapa de registradores Modbus – MDW (Piovan / CanBus Series)

IMPORTANTE
----------
• Os endereços aqui são OFFSETS conforme o manual (+N)
• O cálculo do endereço real é feito no reader.py:
      address = base_address + offset
• WORD  = 1 registrador (16 bits)
• DWORD = 2 registradores (32 bits)
• decimals = casas decimais (valor / 10**decimals)
"""

# =========================
# REGISTROS ANALÓGICOS
# =========================

REGISTERS = {

    # ---------- SETPOINTS (%)
    "station_1_setpoint": {
        "offset": 9,
        "type": "u16",
        "decimals": 1,
        "unit": "%",
        "rw": "R/W",
        "description": "Setpoint estação 1"
    },
    "station_2_setpoint": {
        "offset": 10,
        "type": "u16",
        "decimals": 1,
        "unit": "%",
        "rw": "R/W",
        "description": "Setpoint estação 2"
    },
    "station_3_setpoint": {
        "offset": 11,
        "type": "u16",
        "decimals": 1,
        "unit": "%",
        "rw": "R/W",
        "description": "Setpoint estação 3"
    },
    "station_4_setpoint": {
        "offset": 12,
        "type": "u16",
        "decimals": 1,
        "unit": "%",
        "rw": "R/W",
        "description": "Setpoint estação 4"
    },
    "station_5_setpoint": {
        "offset": 13,
        "type": "u16",
        "decimals": 1,
        "unit": "%",
        "rw": "R/W",
        "description": "Setpoint estação 5"
    },
    "station_6_setpoint": {
        "offset": 14,
        "type": "u16",
        "decimals": 1,
        "unit": "%",
        "rw": "R/W",
        "description": "Setpoint estação 6"
    },

    # ---------- BATCH / BLEND
    "batch_value_g": {
        "offset": 23,
        "type": "u16",
        "decimals": 0,
        "unit": "g",
        "rw": "R/W",
        "description": "Valor do batch"
    },
    "blend_weight_kg": {
        "offset": 24,  # +24 e +25
        "type": "u32",
        "decimals": 1,
        "unit": "kg",
        "rw": "R/W",
        "description": "Peso do blend"
    },

    # ---------- PRODUÇÃO
    "actual_throughput_kgh": {
        "offset": 28,
        "type": "u16",
        "decimals": 1,
        "unit": "kg/h",
        "rw": "R",
        "description": "Vazão atual"
    },

    # ---------- MATERIAL DOSADO POR ESTAÇÃO
    "station_1_dosed_g": {
        "offset": 63,
        "type": "u32",
        "decimals": 1,
        "unit": "g",
        "rw": "R",
        "description": "Material dosado estação 1"
    },
    "station_2_dosed_g": {
        "offset": 65,
        "type": "u32",
        "decimals": 1,
        "unit": "g",
        "rw": "R",
        "description": "Material dosado estação 2"
    },
    "station_3_dosed_g": {
        "offset": 67,
        "type": "u32",
        "decimals": 1,
        "unit": "g",
        "rw": "R",
        "description": "Material dosado estação 3"
    },
    "station_4_dosed_g": {
        "offset": 69,
        "type": "u32",
        "decimals": 1,
        "unit": "g",
        "rw": "R",
        "description": "Material dosado estação 4"
    },
    "station_5_dosed_g": {
        "offset": 71,
        "type": "u32",
        "decimals": 1,
        "unit": "g",
        "rw": "R",
        "description": "Material dosado estação 5"
    },
    "station_6_dosed_g": {
        "offset": 73,
        "type": "u32",
        "decimals": 1,
        "unit": "g",
        "rw": "R",
        "description": "Material dosado estação 6"
    },

    # =========================
    # STATUS / COMANDOS (BITS)
    # =========================

    "mdw_status": {
        "offset": 50,
        "type": "u16",
        "rw": "R",
        "description": "Status geral MDW",
        "bits": {
            0: "stop",
            1: "run",
            2: "pause",
            3: "auto_mode",
            4: "calibration",
            8: "calibration_step_active",
            9: "sensor_timeout",
            10: "recipe_changed",
            11: "recipe_changed_by_dip",
            12: "weighing_drift_detected",
            13: "pause_over_10h"
        }
    },

    "mdw_command": {
        "offset": 29,
        "type": "u16",
        "rw": "W",
        "description": "Comandos MDW",
        "bits": {
            0: "stop",
            1: "run",
            2: "pause",
            3: "auto",
            4: "calibration"
        }
    },

    # =========================
    # ALARMES
    # =========================

    "alarms_word_1": {
        "offset": 51,
        "type": "u16",
        "rw": "R",
        "description": "Alarmes A01–A16"
    },
    "alarms_word_2": {
        "offset": 52,
        "type": "u16",
        "rw": "R",
        "description": "Alarmes A17–A32"
    },
    "alarms_word_3": {
        "offset": 53,
        "type": "u16",
        "rw": "R",
        "description": "Alarmes A33–A48"
    },

    # =========================
    # I/O DIGITAIS
    # =========================

    "digital_inputs": {
        "offset": 54,
        "type": "u16",
        "rw": "R",
        "description": "Entradas digitais",
    },
    "digital_outputs": {
        "offset": 55,
        "type": "u16",
        "rw": "R",
        "description": "Saídas digitais",
    },
}
# =========================