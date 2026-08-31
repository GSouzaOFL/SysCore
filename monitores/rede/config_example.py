# ============================================
# CONFIGURAÇÕES DO MONITOR DE REDE
# ============================================

# Token do bot do Telegram (RedePrincipalBot)
TELEGRAM_TOKEN = "SEU_TOKEN_AQUI"

# Chat ID do seu Telegram
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"

# Intervalo entre scans (em segundos)
INTERVALO = 60

# Rede a ser monitorada
REDE = "192.168.18.0/24"

# Mapeamento de IPs para nomes
NOMES = {
    "192.168.18.1": "📡 Roteador",
    "192.168.18.39": "📺 TV",
    "192.168.18.53": "📱 Meu Celular",
}

# Arquivo para salvar o estado anterior
ARQUIVO_ESTADO = "/data/data/com.termux/files/home/SysCore/monitores/rede/dados/estado.txt"
