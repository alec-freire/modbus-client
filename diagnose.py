"""
Script de diagnóstico Modbus.
Testa diferentes configurações para encontrar o endereço correto.
"""

import argparse
import logging
from modbus.client import ModbusClientRS485

from settings import load_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =========================
# TESTES
# =========================

def test_base_addresses(client):
    """Testa diferentes base addresses comuns."""
    
    print("\n" + "="*60)
    print("TESTANDO DIFERENTES BASE ADDRESSES")
    print("="*60)
    
    # Offsets comuns em Modbus:
    # 0 = endereço direto
    # 1 = alguns equipamentos começam em 1
    # 40001 = protocolo Modicon (40001-49999 para holding registers)
    # 400000 = variação do protocolo Modicon
    
    test_configs = [
        (0, "Endereço direto (0-based)"),
        (1, "Endereço 1-based"),
        (40001, "Protocolo Modicon 40001+"),
        (400000, "Protocolo Modicon 400000+"),
    ]
    
    # Vamos tentar ler o primeiro registrador do perfil basic (offset 9)
    test_offset = 9
    
    for base, description in test_configs:
        address = base + test_offset
        print(f"\n[TEST] {description}")
        print(f"       Base: {base} | Offset: {test_offset} | Address: {address}")
        
        try:
            result = client.read_holding(address=address, count=1)
            print(f"       ✓ SUCESSO! Valor lido: {result}")
            print(f"       >>> Use BASE_ADDRESS = {base} no process.py")
            return base
        except Exception as e:
            print(f"       ✗ Falhou: {e}")
    
    return None


def test_individual_addresses(client):
    """Testa endereços individuais para encontrar quais existem."""
    
    print("\n" + "="*60)
    print("TESTANDO ENDEREÇOS INDIVIDUAIS (0-100)")
    print("="*60)
    
    found = []
    
    for addr in range(0, 101):
        try:
            result = client.read_holding(address=addr, count=1)
            found.append((addr, result[0]))
            print(f"✓ Addr {addr:3d}: {result[0]:5d} (0x{result[0]:04X})")
        except:
            pass  # endereço não existe
    
    if found:
        print(f"\n✓ Encontrados {len(found)} endereços válidos:")
        print(f"   Intervalo: {found[0][0]} - {found[-1][0]}")
    else:
        print("\n✗ Nenhum endereço válido encontrado!")
    
    return found


def test_slave_ids(client):
    """Testa diferentes slave IDs."""
    
    print("\n" + "="*60)
    print("TESTANDO DIFERENTES SLAVE IDs (1-10)")
    print("="*60)
    
    original_slave = client.slave_id
    test_address = 0  # tenta ler endereço 0
    
    for slave_id in range(1, 11):
        client.slave_id = slave_id
        print(f"\n[TEST] Slave ID: {slave_id}")
        
        try:
            result = client.read_holding(address=test_address, count=1)
            print(f"       ✓ SUCESSO! Dispositivo respondeu")
            print(f"       >>> Use SLAVE_ID = {slave_id} no process.py")
            client.slave_id = original_slave
            return slave_id
        except Exception as e:
            print(f"       ✗ Sem resposta")
    
    client.slave_id = original_slave
    return None


# =========================
# MAIN
# =========================

def main():
    parser = argparse.ArgumentParser(description="Diagnóstico Modbus")
    parser.add_argument(
        "--config",
        help="Caminho do arquivo INI (padrão: ./config.ini ou env MODBUS_CONFIG)",
    )
    args = parser.parse_args()

    cfg = load_settings(args.config)

    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "DIAGNÓSTICO MODBUS" + " "*25 + "║")
    print("╚" + "="*58 + "╝")
    print(f"\nPorta: {cfg.modbus.port}")
    print(f"Slave ID inicial: {cfg.modbus.slave_id}")
    print("\n")
    
    client = ModbusClientRS485(
        port=cfg.modbus.port,
        baudrate=cfg.modbus.baudrate,
        parity=cfg.modbus.parity,
        stopbits=cfg.modbus.stopbits,
        bytesize=cfg.modbus.bytesize,
        timeout=cfg.modbus.timeout,
        slave_id=cfg.modbus.slave_id,
        retries=1,  # apenas 1 tentativa para diagnóstico rápido
    )
    
    try:
        print("Conectando...")
        client.connect()
        print("✓ Conectado!\n")
        
        # Teste 1: Slave ID correto?
        print("\n>>> ETAPA 1: Verificar Slave ID")
        found_slave = test_slave_ids(client)
        
        if found_slave and found_slave != cfg.modbus.slave_id:
            print(f"\n⚠️  ATENÇÃO: Slave ID correto é {found_slave}, não {cfg.modbus.slave_id}")
            client.slave_id = found_slave
        
        # Teste 2: Base address correto?
        print("\n>>> ETAPA 2: Verificar Base Address")
        found_base = test_base_addresses(client)
        
        # Teste 3: Mapear endereços disponíveis
        print("\n>>> ETAPA 3: Mapear Registros Disponíveis")
        found_addresses = test_individual_addresses(client)
        
        # Resumo
        print("\n" + "="*60)
        print("RESUMO DO DIAGNÓSTICO")
        print("="*60)
        
        if found_slave:
            print(f"✓ Slave ID: {found_slave}")
        else:
            print(f"✗ Slave ID: Não detectado automaticamente")
        
        if found_base is not None:
            print(f"✓ Base Address: {found_base}")
        else:
            print(f"✗ Base Address: Não detectado automaticamente")
        
        if found_addresses:
            print(f"✓ Registros disponíveis: {len(found_addresses)}")
        else:
            print(f"✗ Nenhum registro encontrado")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
    
    finally:
        client.close()
        print("\nConexão encerrada.")


if __name__ == "__main__":
    main()
