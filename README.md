# Modbus Client - Piovan MDW

Cliente Modbus RTU para leitura de variáveis do equipamento Piovan MDW.

## 📁 Estrutura

```
modbus-client/
├── modbus/              # Package principal
│   ├── client.py        # Cliente Modbus RTU (comunicação)
│   ├── reader.py        # Lógica de leitura e decodificação
│   └── registers.py     # Mapa de registradores
├── process.py           # Script principal
├── test_server.py       # Servidor simulado para testes
└── requirements.txt     # Dependências
```

## 🚀 Instalação

```bash
pip install -r requirements.txt
```

## 🔧 Uso

### Modo Produção (Hardware Real)

1. Conecte o conversor RS-485/USB
2. Crie seu arquivo de configuração (fora do código):
   - Copie `config.example.ini` para `config.ini`
   - Ajuste a porta em `[modbus] port` (ex.: `COM3`, `COM12`, `/dev/ttyUSB0`)
3. Execute:
   ```bash
   python process.py
   ```

Opcional:
- Usar outro arquivo: `python process.py --config .\meu_modbus.ini`
- Usar variável de ambiente: `set MODBUS_CONFIG=C:\caminho\config.ini`

### Modo Teste (Servidor Simulado)

**Windows - Requer par de portas virtuais:**

1. Instale [com0com](https://sourceforge.net/projects/com0com/) ou similar
2. Crie par virtual: `COM3 ↔ COM4`
3. Terminal 1 - Inicie o servidor:
   ```bash
   python test_server.py
   ```
4. Terminal 2 - Inicie o client:
   ```bash
   python process.py
   ```

**Linux/Mac:**

```bash
# Terminal 1 - criar PTYs virtuais
socat -d -d pty,raw,echo=0 pty,raw,echo=0
# Anote os PTYs criados (ex: /dev/pts/2 e /dev/pts/3)

# Terminal 2 - servidor
python test_server.py

# Terminal 3 - client
python process.py
```

## 📊 Perfis de Leitura

Disponíveis em `reader.py`:

- **`basic`** - Setpoints, throughput, status, batch/blend
- **`alarms`** - Status, alarmes, I/O digitais
- **`production`** - Throughput e material dosado por estação

## 🔌 Configuração Modbus

- **Baudrate**: 9600
- **Paridade**: N (None)
- **Stop bits**: 1
- **Byte size**: 8
- **Timeout**: 1.0s
- **Retries**: 3

As configurações ficam no arquivo `config.ini` (copie de `config.example.ini`).

## 📝 Exemplo de Uso Programático

```python
from modbus.client import ModbusClientRS485
from modbus.reader import read_profile, read_one

client = ModbusClientRS485(port="COM3", slave_id=1)
client.connect()

# Lê perfil completo
data = read_profile(client, "basic", base_address=0, slave_id=1)
print(data)

# Lê variável individual
throughput = read_one(client, "actual_throughput_kgh", base_address=0, slave_id=1)
print(f"Vazão: {throughput} kg/h")

client.close()
```

## 🐛 Troubleshooting

### Erro de conexão
- Verifique a porta COM no Gerenciador de Dispositivos (Windows)
- Teste com `python -m serial.tools.list_ports`
- Confirme baudrate e parâmetros seriais

### Valores DWORD errados
- Ajuste `DWORD_ORDER` em `reader.py` ("HI_LO" ou "LO_HI")

### Timeout frequente
- Aumente `timeout` no `ModbusClientRS485`
- Verifique cabeamento RS-485 (A, B, GND)
- Confirme `slave_id` correto

## 📄 Licença

MIT
