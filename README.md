# ⚙️ SysCore

**Sistema completo de monitoramento e automação para Termux**

---

## 📦 Funcionalidades

### 🌐 Monitor de Rede
- Diagnóstico completo: ping, velocidade, perda de pacotes
- Lista de dispositivos conectados
- Alertas de entrada/saída de dispositivos

### 📊 Monitor do Sistema
- Bateria (nível, status, temperatura)
- CPU (uso, frequência)
- RAM (total, usado, disponível)
- Armazenamento (interno, SD card)

### 🌍 Monitor de Navegação
- Registra sites acessados por IP
- Histórico de navegação
- Limpeza automática (5 dias)

### 🤖 Bot de Comandos
- Controle via Telegram
- Comandos categorizados com botões
- Diagnóstico sob demanda

---

## 🚀 Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/SysCore.git
cd SysCore

# 2. Execute o instalador
bash scripts/instalar.sh

# 3. Configure os tokens
nano monitores/rede/config.py
nano monitores/sistema/config.py
nano monitores/navegacao/config.py
nano bot/config.py

# 4. Execute o bot
python bot/bot.py
```

---

## 📋 Comandos do Bot

| Comando | Função |
|---------|--------|
| `/diagnostico` | Diagnóstico completo da rede |
| `/relatorio` | Relatório completo do sistema |
| `/scan` | Lista dispositivos na rede |
| `/velocidade` | Testa velocidade da internet |
| `/bateria` | Status da bateria |
| `/cpu` | Uso da CPU |
| `/ram` | Uso da RAM |
| `/armazenamento` | Espaço disponível |
| `/navegacao` | Últimos sites acessados |
| `/navegacao IP` | Sites acessados por IP |
| `/top` | Sites mais acessados |
| `/start` | Inicia os monitores |
| `/stop` | Para os monitores |
| `/restart` | Reinicia os monitores |
| `/status` | Status dos monitores |
| `/reboot` | Reinicia o aparelho |
| `/help` | Lista todos os comandos |

---

## 📁 Estrutura do Projeto

```
SysCore/
├── monitores/
│   ├── rede/
│   │   ├── monitor_rede.py
│   │   ├── config.py
│   │   └── dados/
│   ├── sistema/
│   │   ├── monitor_sistema.py
│   │   ├── config.py
│   │   └── dados/
│   └── navegacao/
│       ├── monitor_navegacao.py
│       ├── config.py
│       └── dados/
├── bot/
│   ├── bot.py
│   └── config.py
├── logs/
├── scripts/
│   └── instalar.sh
└── README.md
```

---

## 📋 Requisitos

- Termux (Android)
- App: Termux:API
- Python 3
- nmap

---

## 📄 Licença

MIT
