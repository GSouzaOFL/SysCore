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
git clone https://github.com/GSouzaOFL/SysCore.git
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
