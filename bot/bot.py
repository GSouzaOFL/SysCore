#!/usr/bin/env python3
# ============================================
# BOT DE COMANDOS - SysCore
# Menu categorizado com botões
# ============================================

import subprocess
import time
import requests
import json
import re
import os
import sys
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa configurações
try:
    from config import *
except ImportError:
    print("❌ Arquivo config.py não encontrado!")
    sys.exit(1)

# ================= CONFIGURAÇÕES =================

URL = f"https://api.telegram.org/bot{TOKEN}"
ultimo_update = 0

# ================= MENUS =================

def menu_principal():
    """Menu principal com categorias"""
    keyboard = [
        [
            {"text": "📊 Monitoramento", "callback_data": "categoria_monitoramento"},
            {"text": "⚙️ Sistema", "callback_data": "categoria_sistema"}
        ],
        [
            {"text": "🎮 Controle", "callback_data": "categoria_controle"},
            {"text": "❓ Ajuda", "callback_data": "categoria_ajuda"}
        ]
    ]
    return keyboard

def menu_monitoramento():
    """Menu da categoria Monitoramento"""
    keyboard = [
        [
            {"text": "🌐 Diagnóstico de Rede", "callback_data": "diagnostico"},
            {"text": "📊 Relatório do Sistema", "callback_data": "relatorio"}
        ],
        [
            {"text": "📡 Dispositivos na Rede", "callback_data": "scan"},
            {"text": "🌐 Histórico de Navegação", "callback_data": "navegacao"}
        ],
        [
            {"text": "⚡ Teste de Velocidade", "callback_data": "velocidade"}
        ],
        [
            {"text": "🔙 Voltar ao Menu Principal", "callback_data": "voltar"}
        ]
    ]
    return keyboard

def menu_sistema():
    """Menu da categoria Sistema"""
    keyboard = [
        [
            {"text": "🔋 Status da Bateria", "callback_data": "bateria"},
            {"text": "💻 Status da CPU", "callback_data": "cpu"}
        ],
        [
            {"text": "🎮 Status da GPU", "callback_data": "gpu"},
            {"text": "🧠 Status da RAM", "callback_data": "ram"}
        ],
        [
            {"text": "💾 Status do Armazenamento", "callback_data": "armazenamento"}
        ],
        [
            {"text": "🔙 Voltar ao Menu Principal", "callback_data": "voltar"}
        ]
    ]
    return keyboard

def menu_controle():
    """Menu da categoria Controle"""
    keyboard = [
        [
            {"text": "▶️ Iniciar Monitores", "callback_data": "start"},
            {"text": "⏹️ Parar Monitores", "callback_data": "stop"}
        ],
        [
            {"text": "🔄 Reiniciar Monitores", "callback_data": "restart"},
            {"text": "🔄 Reiniciar Aparelho", "callback_data": "reboot"}
        ],
        [
            {"text": "📋 Status dos Monitores", "callback_data": "status"}
        ],
        [
            {"text": "🔙 Voltar ao Menu Principal", "callback_data": "voltar"}
        ]
    ]
    return keyboard

def menu_ajuda():
    """Menu da categoria Ajuda"""
    keyboard = [
        [
            {"text": "📋 Lista de Comandos", "callback_data": "help"}
        ],
        [
            {"text": "🔙 Voltar ao Menu Principal", "callback_data": "voltar"}
        ]
    ]
    return keyboard

# ================= FUNÇÕES DO BOT =================

def enviar_mensagem(chat_id, texto, keyboard=None):
    """Envia uma mensagem para o Telegram com ou sem botões"""
    try:
        dados = {
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": "Markdown"
        }
        if keyboard:
            dados["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
        
        requests.post(f"{URL}/sendMessage", data=dados, timeout=10)
    except Exception as e:
        print(f"[ERRO] Falha ao enviar: {e}")

def enviar_menu(chat_id, titulo, keyboard):
    """Envia um menu com botões"""
    mensagem = f"🤖 *SysCore - {titulo}*\n\nSelecione uma opção abaixo:"
    enviar_mensagem(chat_id, mensagem, keyboard)

def editar_mensagem(chat_id, message_id, texto, keyboard=None):
    """Edita uma mensagem existente"""
    try:
        dados = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": texto,
            "parse_mode": "Markdown"
        }
        if keyboard:
            dados["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
        
        requests.post(f"{URL}/editMessageText", data=dados, timeout=10)
    except Exception as e:
        print(f"[ERRO] Falha ao editar: {e}")

def obter_atualizacoes(offset=None):
    """Obtém novas mensagens do Telegram"""
    url = f"{URL}/getUpdates"
    params = {"timeout": 30, "allowed_updates": ["message", "callback_query"]}
    if offset:
        params["offset"] = offset
    try:
        resposta = requests.get(url, params=params, timeout=35)
        return resposta.json().get("result", [])
    except:
        return []

def usuario_autorizado(chat_id):
    """Verifica se o usuário tem permissão para usar o bot"""
    if not AUTHORIZED_USERS:
        return True
    return str(chat_id) in [str(u) for u in AUTHORIZED_USERS]

# ================= LEITURA DE DADOS =================

def ler_json(caminho):
    """Lê um arquivo JSON e retorna os dados"""
    try:
        with open(caminho, "r") as f:
            return json.load(f)
    except:
        return None

# ================= COMANDOS =================

def cmd_diagnostico(chat_id, message_id=None):
    """Envia o diagnóstico de rede"""
    dados = ler_json(CAMINHO_REDE)
    if not dados:
        msg = "❌ *Diagnóstico não disponível*\nAguardando coleta de dados..."
        if message_id:
            editar_mensagem(chat_id, message_id, msg)
        else:
            enviar_mensagem(chat_id, msg)
        return
    
    # Formata a mensagem
    msg = "🌐 *DIAGNÓSTICO DE REDE*\n\n"
    msg += f"📡 {dados.get('ssid', 'N/A')}\n"
    msg += f"📱 IP Local: `{dados.get('ip_local', 'N/A')}`\n\n"
    
    msg += "📊 *LATÊNCIA:*\n"
    pings = dados.get("pings", {})
    for nome, info in pings.items():
        if info.get("tempo"):
            msg += f"  {info.get('status', '')} {nome}: `{info['tempo']:.1f}ms`\n"
        else:
            msg += f"  🔴 {nome}: `Falha`\n"
    
    perda = dados.get("perda_pacotes", 0)
    if perda == 0:
        msg += f"\n📦 *Perda de pacotes:* ✅ `0%`"
    elif perda < 5:
        msg += f"\n📦 *Perda de pacotes:* 🟢 `{perda}%`"
    else:
        msg += f"\n📦 *Perda de pacotes:* 🔴 `{perda}%`"
    
    vel = dados.get("velocidade", {})
    msg += f"\n📥 *Download:* `{vel.get('download', 0)} Mbps`"
    msg += f"\n📤 *Upload:* `{vel.get('upload', 0)} Mbps`"
    
    dispositivos = dados.get("dispositivos", [])
    msg += f"\n\n💻 *CONEXÕES ATUAIS*\n"
    for d in dispositivos[:10]:
        msg += f"  • {d}\n"
    if len(dispositivos) > 10:
        msg += f"  ... e mais {len(dispositivos) - 10} dispositivos"
    
    msg += f"\n\n🕐 *Atualizado:* {dados.get('timestamp', 'N/A')[:19]}"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_relatorio(chat_id, message_id=None):
    """Envia o relatório do sistema"""
    dados = ler_json(CAMINHO_SISTEMA)
    if not dados:
        msg = "❌ *Relatório não disponível*\nAguardando coleta de dados..."
        if message_id:
            editar_mensagem(chat_id, message_id, msg)
        else:
            enviar_mensagem(chat_id, msg)
        return
    
    msg = "📊 *RELATÓRIO DO SISTEMA*\n\n"
    msg += f"📱 Modelo: {dados.get('modelo', 'N/A')}\n\n"
    
    # Bateria
    bat = dados.get("bateria", {})
    if "erro" not in bat:
        msg += "🔋 *BATERIA:*\n"
        msg += f"  Nível: {bat.get('nivel', 'N/A')}%\n"
        msg += f"  Status: {bat.get('status', 'N/A')}\n"
        if bat.get('temperatura'):
            msg += f"  Temperatura: {bat.get('temperatura')}°C\n"
    else:
        msg += f"🔋 *BATERIA:* ⚠️ {bat.get('erro')}\n"
    
    # CPU
    cpu = dados.get("cpu", {})
    if "erro" not in cpu:
        msg += f"\n💻 *CPU:*\n"
        msg += f"  Uso: {cpu.get('uso', 'N/A')}\n"
        if cpu.get('frequencia'):
            msg += f"  Frequência: {cpu.get('frequencia')} MHz\n"
    else:
        msg += f"\n💻 *CPU:* ⚠️ {cpu.get('erro')}\n"
    
    # GPU
    gpu = dados.get("gpu", {})
    if "erro" not in gpu:
        msg += f"\n🎮 *GPU:*\n"
        msg += f"  Modelo: {gpu.get('modelo', 'N/A')}\n"
        if gpu.get('frequencia'):
            msg += f"  Frequência: {gpu.get('frequencia')} MHz\n"
        if gpu.get('uso'):
            msg += f"  Uso: {gpu.get('uso')}\n"
        if gpu.get('temperatura'):
            msg += f"  Temperatura: {gpu.get('temperatura')}°C\n"
    else:
        msg += f"\n🎮 *GPU:* ⚠️ {gpu.get('erro')}\n"
    
    # RAM
    ram = dados.get("ram", {})
    if "erro" not in ram:
        msg += f"\n🧠 *RAM:*\n"
        msg += f"  Total: {ram.get('total', 'N/A')}\n"
        msg += f"  Usado: {ram.get('usado', 'N/A')}\n"
        msg += f"  Disponível: {ram.get('disponivel', 'N/A')}\n"
        msg += f"  Uso: {ram.get('porcentagem', 'N/A')}\n"
    else:
        msg += f"\n🧠 *RAM:* ⚠️ {ram.get('erro')}\n"
    
    # Armazenamento
    arm = dados.get("armazenamento", {})
    if "erro" not in arm:
        msg += f"\n💾 *ARMAZENAMENTO:*\n"
        for nome, info in arm.items():
            msg += f"  📁 {nome}:\n"
            msg += f"    Total: {info.get('total', 'N/A')}\n"
            msg += f"    Usado: {info.get('usado', 'N/A')}\n"
            msg += f"    Disponível: {info.get('disponivel', 'N/A')}\n"
    else:
        msg += f"\n💾 *ARMAZENAMENTO:* ⚠️ {arm.get('erro')}\n"
    
    msg += f"\n🕐 *Atualizado:* {dados.get('timestamp', 'N/A')[:19]}"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_scan(chat_id, message_id=None):
    """Lista dispositivos na rede"""
    dados = ler_json(CAMINHO_REDE)
    if not dados:
        msg = "❌ *Dados não disponíveis*"
        if message_id:
            editar_mensagem(chat_id, message_id, msg)
        else:
            enviar_mensagem(chat_id, msg)
        return
    
    dispositivos = dados.get("dispositivos", [])
    if not dispositivos:
        msg = "📡 *Nenhum dispositivo encontrado*"
    else:
        msg = "📡 *DISPOSITIVOS NA REDE*\n\n"
        for i, d in enumerate(dispositivos, 1):
            msg += f"{i}. {d}\n"
        msg += f"\n📊 *Total:* {len(dispositivos)} dispositivos"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_navegacao(chat_id, message_id=None):
    """Mostra histórico de navegação"""
    dados = ler_json(CAMINHO_NAVEGACAO)
    if not dados:
        msg = "❌ *Histórico não disponível*"
        if message_id:
            editar_mensagem(chat_id, message_id, msg)
        else:
            enviar_mensagem(chat_id, msg)
        return
    
    historico = dados.get("historico", [])
    if not historico:
        msg = "🌐 *Nenhum registro de navegação*"
    else:
        msg = "🌐 *HISTÓRICO DE NAVEGAÇÃO*\n\n"
        ultimo = historico[-1]
        msg += f"📡 *Último scan:* {ultimo.get('timestamp', 'N/A')[:19]}\n"
        msg += f"📊 *Dispositivos ativos:* {ultimo.get('total', 0)}\n\n"
        
        dispositivos = ultimo.get("dispositivos", [])
        for d in dispositivos:
            msg += f"  • {d}\n"
        
        msg += f"\n📈 *Histórico de mudanças:*\n"
        for h in historico[-5:]:
            msg += f"  {h.get('timestamp', 'N/A')[:16]} → {h.get('total', 0)} dispositivos\n"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_velocidade(chat_id, message_id=None):
    """Mostra velocidade da internet"""
    dados = ler_json(CAMINHO_REDE)
    if not dados:
        msg = "❌ *Dados não disponíveis*"
        if message_id:
            editar_mensagem(chat_id, message_id, msg)
        else:
            enviar_mensagem(chat_id, msg)
        return
    
    vel = dados.get("velocidade", {})
    msg = "⚡ *TESTE DE VELOCIDADE*\n\n"
    msg += f"📥 *Download:* `{vel.get('download', 0)} Mbps`\n"
    msg += f"📤 *Upload:* `{vel.get('upload', 0)} Mbps`\n"
    msg += f"\n🕐 *Atualizado:* {dados.get('timestamp', 'N/A')[:19]}"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_bateria(chat_id, message_id=None):
    """Mostra status da bateria"""
    dados = ler_json(CAMINHO_SISTEMA)
    if not dados:
        msg = "❌ *Dados não disponíveis*"
        if message_id:
            editar_mensagem(chat_id, message_id, msg)
        else:
            enviar_mensagem(chat_id, msg)
        return
    
    bat = dados.get("bateria", {})
    if "erro" in bat:
        msg = f"🔋 *BATERIA:* ⚠️ {bat.get('erro')}"
    else:
        msg = "🔋 *STATUS DA BATERIA*\n\n"
        msg += f"Nível: {bat.get('nivel', 'N/A')}%\n"
        msg += f"Status: {bat.get('status', 'N/A')}\n"
        if bat.get('temperatura'):
            msg += f"Temperatura: {bat.get('temperatura')}°C"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_cpu(chat_id, message_id=None):
    """Mostra status da CPU"""
    dados = ler_json(CAMINHO_SISTEMA)
    if not dados:
        msg = "❌ *Dados não disponíveis*"
        if message_id:
            editar_mensagem(chat_id, message_id, msg)
        else:
            enviar_mensagem(chat_id, msg)
        return
    
    cpu = dados.get("cpu", {})
    if "erro" in cpu:
        msg = f"💻 *CPU:* ⚠️ {cpu.get('erro')}"
    else:
        msg = "💻 *STATUS DA CPU*\n\n"
        msg += f"Uso: {cpu.get('uso', 'N/A')}\n"
        if cpu.get('frequencia'):
            msg += f"Frequência: {cpu.get('frequencia')} MHz"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_gpu(chat_id, message_id=None):
    """Mostra status da GPU"""
    dados = ler_json(CAMINHO_SISTEMA)
    if not dados:
        msg = "❌ *Dados não disponíveis*"
        if message_id:
            editar_mensagem(chat_id, message_id, msg)
        else:
            enviar_mensagem(chat_id, msg)
        return
    
    gpu = dados.get("gpu", {})
    if "erro" in gpu:
        msg = f"🎮 *GPU:* ⚠️ {gpu.get('erro')}"
    else:
        msg = "🎮 *STATUS DA GPU*\n\n"
        msg += f"Modelo: {gpu.get('modelo', 'N/A')}\n"
        if gpu.get('frequencia'):
            msg += f"Frequência: {gpu.get('frequencia')} MHz\n"
        if gpu.get('uso'):
            msg += f"Uso: {gpu.get('uso')}\n"
        if gpu.get('temperatura'):
            msg += f"Temperatura: {gpu.get('temperatura')}°C"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_ram(chat_id, message_id=None):
    """Mostra status da RAM"""
    dados = ler_json(CAMINHO_SISTEMA)
    if not dados:
        msg = "❌ *Dados não disponíveis*"
        if message_id:
            editar_mensagem(chat_id, message_id, msg)
        else:
            enviar_mensagem(chat_id, msg)
        return
    
    ram = dados.get("ram", {})
    if "erro" in ram:
        msg = f"🧠 *RAM:* ⚠️ {ram.get('erro')}"
    else:
        msg = "🧠 *STATUS DA RAM*\n\n"
        msg += f"Total: {ram.get('total', 'N/A')}\n"
        msg += f"Usado: {ram.get('usado', 'N/A')}\n"
        msg += f"Disponível: {ram.get('disponivel', 'N/A')}\n"
        msg += f"Uso: {ram.get('porcentagem', 'N/A')}"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_armazenamento(chat_id, message_id=None):
    """Mostra status do armazenamento"""
    dados = ler_json(CAMINHO_SISTEMA)
    if not dados:
        msg = "❌ *Dados não disponíveis*"
        if message_id:
            editar_mensagem(chat_id, message_id, msg)
        else:
            enviar_mensagem(chat_id, msg)
        return
    
    arm = dados.get("armazenamento", {})
    if "erro" in arm:
        msg = f"💾 *ARMAZENAMENTO:* ⚠️ {arm.get('erro')}"
    else:
        msg = "💾 *STATUS DO ARMAZENAMENTO*\n\n"
        for nome, info in arm.items():
            msg += f"📁 *{nome}*\n"
            msg += f"  Total: {info.get('total', 'N/A')}\n"
            msg += f"  Usado: {info.get('usado', 'N/A')}\n"
            msg += f"  Disponível: {info.get('disponivel', 'N/A')}\n\n"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_start(chat_id, message_id=None):
    """Inicia os monitores"""
    msg = "▶️ *Iniciando monitores...*\n\n"
    
    try:
        subprocess.run(f"nohup python {SCRIPT_MONITOR_REDE} > /dev/null 2>&1 &", shell=True)
        msg += "✅ Monitor de Rede iniciado\n"
    except:
        msg += "❌ Erro ao iniciar Monitor de Rede\n"
    
    try:
        subprocess.run(f"nohup python {SCRIPT_MONITOR_SISTEMA} > /dev/null 2>&1 &", shell=True)
        msg += "✅ Monitor do Sistema iniciado\n"
    except:
        msg += "❌ Erro ao iniciar Monitor do Sistema\n"
    
    try:
        subprocess.run(f"nohup python {SCRIPT_MONITOR_NAVEGACAO} > /dev/null 2>&1 &", shell=True)
        msg += "✅ Monitor de Navegação iniciado\n"
    except:
        msg += "❌ Erro ao iniciar Monitor de Navegação\n"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_stop(chat_id, message_id=None):
    """Para os monitores"""
    msg = "⏹️ *Parando monitores...*\n\n"
    
    try:
        subprocess.run(f"pkill -f {SCRIPT_MONITOR_REDE}", shell=True)
        msg += "✅ Monitor de Rede parado\n"
    except:
        msg += "❌ Erro ao parar Monitor de Rede\n"
    
    try:
        subprocess.run(f"pkill -f {SCRIPT_MONITOR_SISTEMA}", shell=True)
        msg += "✅ Monitor do Sistema parado\n"
    except:
        msg += "❌ Erro ao parar Monitor do Sistema\n"
    
    try:
        subprocess.run(f"pkill -f {SCRIPT_MONITOR_NAVEGACAO}", shell=True)
        msg += "✅ Monitor de Navegação parado\n"
    except:
        msg += "❌ Erro ao parar Monitor de Navegação\n"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_status(chat_id, message_id=None):
    """Mostra status dos monitores"""
    msg = "📋 *STATUS DOS MONITORES*\n\n"
    
    # Verifica Monitor de Rede
    try:
        resultado = subprocess.run(["pgrep", "-f", SCRIPT_MONITOR_REDE], capture_output=True, text=True)
        if resultado.stdout.strip():
            msg += "✅ Monitor de Rede: Rodando\n"
        else:
            msg += "❌ Monitor de Rede: Parado\n"
    except:
        msg += "❌ Monitor de Rede: Desconhecido\n"
    
    # Verifica Monitor do Sistema
    try:
        resultado = subprocess.run(["pgrep", "-f", SCRIPT_MONITOR_SISTEMA], capture_output=True, text=True)
        if resultado.stdout.strip():
            msg += "✅ Monitor do Sistema: Rodando\n"
        else:
            msg += "❌ Monitor do Sistema: Parado\n"
    except:
        msg += "❌ Monitor do Sistema: Desconhecido\n"

    # Verifica Monitor de Navegação
    try:
        resultado = subprocess.run(["pgrep", "-f", SCRIPT_MONITOR_NAVEGACAO], capture_output=True, text=True)
        if resultado.stdout.strip():
            msg += "✅ Monitor de Navegação: Rodando\n"
        else:
            msg += "❌ Monitor de Navegação: Parado\n"
    except:
        msg += "❌ Monitor de Navegação: Desconhecido\n"
    
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_restart(chat_id, message_id=None):
    """Reinicia os monitores"""
    cmd_stop(chat_id)
    time.sleep(2)
    cmd_start(chat_id)

def cmd_reboot(chat_id, message_id=None):
    """Reinicia o aparelho"""
    if message_id:
        editar_mensagem(chat_id, message_id, "🔄 *Reiniciando aparelho em 5 segundos...*")
    else:
        enviar_mensagem(chat_id, "🔄 *Reiniciando aparelho em 5 segundos...*")
    time.sleep(5)
    os.system("reboot")

def cmd_help(chat_id, message_id=None):
    """Mostra ajuda"""
    msg = """
📋 *LISTA DE COMANDOS - SysCore*

📊 *Monitoramento:*
  /diagnostico - Diagnóstico completo da rede
  /relatorio - Relatório do sistema
  /scan - Dispositivos na rede
  /navegacao - Histórico de navegação
  /velocidade - Teste de velocidade

⚙️ *Sistema:*
  /bateria - Status da bateria
  /cpu - Status da CPU
  /gpu - Status da GPU
  /ram - Status da RAM
  /armazenamento - Status do armazenamento

🎮 *Controle:*
  /start - Inicia os monitores
  /stop - Para os monitores
  /restart - Reinicia os monitores
  /reboot - Reinicia o aparelho
  /status - Status dos monitores

❓ *Ajuda:*
  /help - Mostra esta mensagem
  /menu - Mostra o menu principal
"""
    if message_id:
        editar_mensagem(chat_id, message_id, msg)
    else:
        enviar_mensagem(chat_id, msg)

def cmd_menu(chat_id):
    """Mostra o menu principal"""
    enviar_menu(chat_id, "Painel de Controle", menu_principal())

# ================= ROTEADOR =================

def processar_comando(chat_id, texto, message_id=None):
    """Processa os comandos recebidos"""
    if not usuario_autorizado(chat_id):
        enviar_mensagem(chat_id, "❌ *Você não tem permissão para usar este bot.*")
        return
    
    comando = texto.strip().lower()
    
    if comando == "/start" or comando == "/menu":
        cmd_menu(chat_id)
    elif comando == "/diagnostico":
        cmd_diagnostico(chat_id, message_id)
    elif comando == "/relatorio":
        cmd_relatorio(chat_id, message_id)
    elif comando == "/scan":
        cmd_scan(chat_id, message_id)
    elif comando == "/navegacao":
        cmd_navegacao(chat_id, message_id)
    elif comando == "/velocidade":
        cmd_velocidade(chat_id, message_id)
    elif comando == "/bateria":
        cmd_bateria(chat_id, message_id)
    elif comando == "/cpu":
        cmd_cpu(chat_id, message_id)
    elif comando == "/gpu":
        cmd_gpu(chat_id, message_id)
    elif comando == "/ram":
        cmd_ram(chat_id, message_id)
    elif comando == "/armazenamento":
        cmd_armazenamento(chat_id, message_id)
    elif comando == "/start":
        cmd_start(chat_id, message_id)
    elif comando == "/stop":
        cmd_stop(chat_id, message_id)
    elif comando == "/restart":
        cmd_restart(chat_id, message_id)
    elif comando == "/reboot":
        cmd_reboot(chat_id, message_id)
    elif comando == "/status":
        cmd_status(chat_id, message_id)
    elif comando == "/help":
        cmd_help(chat_id, message_id)
    else:
        enviar_mensagem(chat_id, f"❌ *Comando desconhecido:* {texto}\nUse /help para ver os comandos disponíveis.")

# ================= PROCESSAR CALLBACK =================

def processar_callback(chat_id, callback_data, message_id):
    """Processa os botões clicados"""
    # Categorias
    if callback_data == "categoria_monitoramento":
        enviar_menu(chat_id, "Monitoramento", menu_monitoramento())
    elif callback_data == "categoria_sistema":
        enviar_menu(chat_id, "Sistema", menu_sistema())
    elif callback_data == "categoria_controle":
        enviar_menu(chat_id, "Controle", menu_controle())
    elif callback_data == "categoria_ajuda":
        enviar_menu(chat_id, "Ajuda", menu_ajuda())
    elif callback_data == "voltar":
        enviar_menu(chat_id, "Painel de Controle", menu_principal())
    
    # Comandos
    elif callback_data == "diagnostico":
        cmd_diagnostico(chat_id, message_id)
    elif callback_data == "relatorio":
        cmd_relatorio(chat_id, message_id)
    elif callback_data == "scan":
        cmd_scan(chat_id, message_id)
    elif callback_data == "navegacao":
        cmd_navegacao(chat_id, message_id)
    elif callback_data == "velocidade":
        cmd_velocidade(chat_id, message_id)
    elif callback_data == "bateria":
        cmd_bateria(chat_id, message_id)
    elif callback_data == "cpu":
        cmd_cpu(chat_id, message_id)
    elif callback_data == "gpu":
        cmd_gpu(chat_id, message_id)
    elif callback_data == "ram":
        cmd_ram(chat_id, message_id)
    elif callback_data == "armazenamento":
        cmd_armazenamento(chat_id, message_id)
    elif callback_data == "start":
        cmd_start(chat_id, message_id)
    elif callback_data == "stop":
        cmd_stop(chat_id, message_id)
    elif callback_data == "restart":
        cmd_restart(chat_id, message_id)
    elif callback_data == "reboot":
        cmd_reboot(chat_id, message_id)
    elif callback_data == "status":
        cmd_status(chat_id, message_id)
    elif callback_data == "help":
        cmd_help(chat_id, message_id)

# ================= MAIN =================

def main():
    print(f"""
╔══════════════════════════════════════════╗
║        🤖 BOT DE COMANDOS - SysCore      ║
║        Menu categorizado com botões     ║
║        Iniciado em: {datetime.now().strftime('%H:%M:%S')}     ║
╚══════════════════════════════════════════╝
    """)
    
    ultimo_update = 0
    
    while True:
        try:
            updates = obter_atualizacoes(ultimo_update)
            
            for update in updates:
                ultimo_update = update["update_id"] + 1
                
                # Mensagens de texto
                if "message" in update:
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    
                    if "text" in message:
                        texto = message["text"]
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📩 {texto}")
                        
                        if texto.startswith("/"):
                            processar_comando(chat_id, texto)
                        else:
                            enviar_mensagem(chat_id, f"❓ *Mensagem recebida:* {texto}\nUse /help para ver os comandos disponíveis.")
                
                # Callbacks (botões clicados)
                elif "callback_query" in update:
                    callback = update["callback_query"]
                    chat_id = callback["message"]["chat"]["id"]
                    message_id = callback["message"]["message_id"]
                    callback_data = callback["data"]
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔘 {callback_data}")
                    
                    # Responde ao callback
                    try:
                        requests.post(f"{URL}/answerCallbackQuery", data={"callback_query_id": callback["id"]})
                    except:
                        pass
                    
                    processar_callback(chat_id, callback_data, message_id)
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot interrompido")
            break
        except Exception as e:
            print(f"[ERRO] {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
