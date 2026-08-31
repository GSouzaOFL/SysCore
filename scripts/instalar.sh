cat > ~/SysCore/scripts/instalar.sh << 'EOF'
#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║        🚀 SYS CORE - INSTALADOR         ║"
echo "╚══════════════════════════════════════════╝"
echo ""

echo "[1/5] Atualizando pacotes..."
pkg update -y && pkg upgrade -y

echo ""
echo "[2/5] Instalando dependências..."
pkg install -y python python-pip git nmap openssh tsu termux-api
pip install requests

echo ""
echo "[3/5] Configurando permissões..."
termux-setup-storage

echo ""
echo "[4/5] Criando estrutura de pastas..."
mkdir -p ~/SysCore/monitores/rede/dados
mkdir -p ~/SysCore/monitores/sistema/dados
mkdir -p ~/SysCore/monitores/navegacao/dados
mkdir -p ~/SysCore/bot
mkdir -p ~/SysCore/logs
mkdir -p ~/SysCore/docs

echo ""
echo "[5/5] Criando arquivos de configuração exemplo..."

cat > ~/SysCore/monitores/rede/config_example.py << 'EOR'
# CONFIGURAÇÕES DO MONITOR DE REDE
TELEGRAM_TOKEN = "SEU_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"
INTERVALO = 60
REDE = "192.168.18.0/24"
NOMES = {
    "192.168.18.1": "📡 Roteador",
}
ARQUIVO_ESTADO = "/data/data/com.termux/files/home/SysCore/monitores/rede/dados/estado.txt"
EOR

cat > ~/SysCore/monitores/sistema/config_example.py << 'EOS'
# CONFIGURAÇÕES DO MONITOR DO SISTEMA
TELEGRAM_TOKEN = "SEU_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"
INTERVALO = 3600
EOS

cat > ~/SysCore/monitores/navegacao/config_example.py << 'EON'
# CONFIGURAÇÕES DO MONITOR DE NAVEGAÇÃO
TELEGRAM_TOKEN = "SEU_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"
INTERVALO = 60
DIAS_PARA_MANTER = 5
HISTORICO_JSON = "/data/data/com.termux/files/home/SysCore/monitores/navegacao/dados/historico.json"
EON

cat > ~/SysCore/bot/config_example.py << 'EOB'
# CONFIGURAÇÕES DO BOT DE COMANDOS
TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID_AQUI"
CAMINHO_REDE = "/data/data/com.termux/files/home/SysCore/monitores/rede/dados/ultimo_diagnostico.json"
CAMINHO_SISTEMA = "/data/data/com.termux/files/home/SysCore/monitores/sistema/dados/ultimo_relatorio.json"
CAMINHO_NAVEGACAO = "/data/data/com.termux/files/home/SysCore/monitores/navegacao/dados/historico.json"
AUTHORIZED_USERS = ["SEU_CHAT_ID_AQUI"]
EOB

echo ""
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Edite os arquivos de configuração:"
echo "   nano ~/SysCore/monitores/rede/config.py"
echo "   nano ~/SysCore/monitores/sistema/config.py"
echo "   nano ~/SysCore/monitores/navegacao/config.py"
echo "   nano ~/SysCore/bot/config.py"
echo ""
echo "2. Execute o bot:"
echo "   cd ~/SysCore && python bot/bot.py"
EOF
