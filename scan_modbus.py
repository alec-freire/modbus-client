import time
import logging
# Substitua 'seu_arquivo_cliente' pelo nome do arquivo onde está a classe ModbusClientRS485
from modbus.client import ModbusClientRS485 

# Configurações para testar
PORTA = 'COM12'  # Verifique se é USB0 ou USB1
BAUDRATES = [9600]
PARIDADES = ['N', 'E']  # N = None (Haitian/Piovan), E = Even (Padrão Modbus)
IDS_PARA_TESTAR = range(0,247) # IDs comuns

# Configura logger simples para não sujar a tela
logging.basicConfig(level=logging.ERROR)

print(f"--- INICIANDO SCAN NA PORTA {PORTA} ---")

encontrou = False

for baud in BAUDRATES:
    for paridade in PARIDADES:
        for slave_id in IDS_PARA_TESTAR:
            print(f"Tentando: Baud={baud} | Paridade={paridade} | ID={slave_id} ... ", end="")
            
            # Instancia sua classe com os parametros do loop
            client = ModbusClientRS485(
                port=PORTA,
                baudrate=baud,
                parity=paridade,
                stopbits=1,
                slave_id=slave_id,
                timeout=0.2,    # Timeout curto para ser rápido
                retries=1       # Sem retry para ser rápido
            )
            
            try:
                client.connect()
                
                # Tenta ler o registro 0 ou 1 (quase toda máquina tem algo aqui)
                # Se falhar aqui, vai pro except
                val = client.read_holding(address=1, count=1)
                
                print(f"✅ SUCESSO! Valor lido: {val}")
                print(f"\n>>> CONFIGURAÇÃO CORRETA ENCONTRADA: <<<")
                print(f"   Baudrate: {baud}")
                print(f"   Paridade: '{paridade}'")
                print(f"   Slave ID: {slave_id}")
                
                encontrou = True
                client.close()
                break # Sai do loop de IDs
                
            except Exception as e:
                print("❌") # Falhou
                client.close()
        
        if encontrou: break # Sai do loop de Paridade
    if encontrou: break # Sai do loop de Baudrate

if not encontrou:
    print("\n--- NENHUMA MÁQUINA ENCONTRADA ---")
    print("Dicas:")
    print("1. Inverta os fios A e B (Data+ e Data-).")
    print("2. Verifique se o ID na tela da máquina não é o mesmo da outra (se estiverem juntas).")