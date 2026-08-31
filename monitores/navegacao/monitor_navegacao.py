#!/usr/bin/env python3
# ============================================
# MONITOR DE NAVEGAÇÃO - SysCore
# Registra dispositivos ativos na rede
# ============================================

import subprocess
import time
import requests
import re
import os
import sys
import json
from datetime import datetime, timedelta

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa configurações
try:
    from config import *
except ImportError:
    print("❌ Arquivo config.py não encontrado!")
    sys.exit(1)

# ================= FUNÇÕES =================

def executar_comando(comando, use_root=False):
    """Executa um comando no shell, com ou sem root"""
    try:
        if use_root:
            cmd = f"tsu -c '{comando}'"
        else:
            cmd = comando
        
        resultado = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=10, shell=True
        )
        return resultado.stdout.strip(), resultado.stderr.strip()
    except Exception as e:
        return "", str(e)

def get_dispositivos():
    """Obtém lista de dispositivos na rede"""
    try:
        resultado = subprocess.run(
            ["nmap", "-sn", REDE],
            capture_output=True, text=True, timeout=60
        )
        ips = re.findall(r"Nmap scan report for ([\d.]+)", resultado.stdout)
        return ips
    except:
        return []

def get_ssid():
    """Obtém o SSID da rede Wi-Fi"""
    try:
        resultado = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True, text=True, timeout=5
        )
        if resultado.stdout:
            try:
                dados = json.loads(resultado.stdout)
                ssid = dados.get("ssid", "")
                if ssid and ssid != "N/A" and ssid != "<unknown ssid>" and ssid != "":
                    return ssid
            except:
                pass
        return "Desconhecido"
    except:
        return "Desconhecido"

def ping_dispositivos(ips):
    """Faz ping em dispositivos para verificar conectividade"""
    ativos = []
    for ip in ips:
        try:
            resultado = subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                capture_output=True, text=True, timeout=3
            )
            if resultado.returncode == 0:
                ativos.append(ip)
        except:
            pass
    return ativos

def salvar_historico(dispositivos_ativos):
    """Salva o histórico de dispositivos ativos"""
    try:
        # Carrega histórico existente
        if os.path.exists(ARQUIVO_HISTORICO):
            with open(ARQUIVO_HISTORICO, "r") as f:
                dados = json.load(f)
        else:
            dados = {"historico": [], "dispositivos": {}}
        
        # Adiciona registro atual
        timestamp = datetime.now().isoformat()
        
        # Atualiza dispositivos
        for ip in dispositivos_ativos:
            if ip not in dados["dispositivos"]:
                dados["dispositivos"][ip] = {
                    "primeira_vez": timestamp,
                    "ultima_vez": timestamp,
                    "contador": 1
                }
            else:
                dados["dispositivos"][ip]["ultima_vez"] = timestamp
                dados["dispositivos"][ip]["contador"] += 1
        
        # Adiciona ao histórico (apenas se houver mudança)
        if dados["historico"] and dados["historico"][-1].get("dispositivos") == dispositivos_ativos:
            pass  # Não adiciona se não mudou
        else:
            dados["historico"].append({
                "timestamp": timestamp,
                "dispositivos": dispositivos_ativos,
                "total": len(dispositivos_ativos)
            })
        
        # Limpeza automática (manter apenas últimos 5 dias)
        if LIMPEZA_AUTOMATICA:
            limite = datetime.now() - timedelta(days=DIAS_PARA_MANTER)
            dados["historico"] = [
                h for h in dados["historico"]
                if datetime.fromisoformat(h["timestamp"]) >= limite
            ]
        
        # Salva
        with open(ARQUIVO_HISTORICO, "w") as f:
            json.dump(dados, f, indent=4)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Histórico salvo: {len(dispositivos_ativos)} dispositivos ativos")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro ao salvar histórico: {e}")

def coletar_navegacao():
    """Coleta dados de navegação (dispositivos ativos)"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Coletando dispositivos da rede...")
    
    # Obtém SSID
    ssid = get_ssid()
    
    # Obtém dispositivos
    dispositivos = get_dispositivos()
    
    if not dispositivos:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ℹ️ Nenhum dispositivo encontrado")
        return
    
    # Testa conectividade
    ativos = ping_dispositivos(dispositivos)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Dispositivos ativos: {len(ativos)}")
    
    # Salva
    salvar_historico(ativos)

# ================= MAIN =================

def main():
    print(f"""
╔══════════════════════════════════════════╗
║        🌐 MONITOR DE NAVEGAÇÃO - SysCore  ║
║        Registra dispositivos ativos      ║
║        Iniciado em: {datetime.now().strftime('%H:%M:%S')}     ║
╚══════════════════════════════════════════╝
    """)
    
    print(f"⏱️  Intervalo: {INTERVALO}s")
    print(f"🗑️  Limpeza automática: {LIMPEZA_AUTOMATICA}")
    print(f"📅  Manter últimos {DIAS_PARA_MANTER} dias")
    print("📁 Salvando dados em:", ARQUIVO_HISTORICO)
    print("-" * 50)
    
    # Coleta inicial
    coletar_navegacao()
    
    # Loop principal
    while True:
        try:
            time.sleep(INTERVALO)
            coletar_navegacao()
            
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Monitor interrompido")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
