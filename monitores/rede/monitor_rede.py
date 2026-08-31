#!/usr/bin/env python3
# ============================================
# MONITOR DE REDE - SysCore
# Coleta silenciosa de dados da rede
# ============================================

import subprocess
import time
import requests
import re
import os
import sys
import json
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa configurações
try:
    from config import *
except ImportError:
    print("❌ Arquivo config.py não encontrado!")
    sys.exit(1)

# ================= FUNÇÕES =================

def enviar_telegram(mensagem):
    """Envia mensagem para o Telegram (apenas para notificações)"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    dados = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=dados, timeout=10)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Notificação enviada")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro: {e}")

def get_gateway():
    """Descobre o gateway da rede"""
    try:
        resultado = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True, text=True, timeout=5
        )
        for linha in resultado.stdout.split("\n"):
            if "default via" in linha:
                partes = linha.split()
                if len(partes) > 2:
                    return partes[2]
        return "192.168.18.1"
    except:
        return "192.168.18.1"

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
                    return f"📶 Wi-Fi: {ssid}"
            except:
                pass
        
        try:
            resultado2 = subprocess.run(
                ["dumpsys", "wifi"],
                capture_output=True, text=True, timeout=5
            )
            for linha in resultado2.stdout.split("\n"):
                if "SSID:" in linha:
                    ssid = linha.split("SSID:")[1].strip()
                    if ssid and ssid != "N/A" and ssid != "<unknown ssid>" and ssid != '""' and ssid != "":
                        return f"📶 Wi-Fi: {ssid}"
        except:
            pass
        
        try:
            resultado3 = subprocess.run(
                ["ip", "addr", "show", "wlan0"],
                capture_output=True, text=True, timeout=5
            )
            if "inet" in resultado3.stdout:
                return "📶 Wi-Fi: (SSID não disponível)"
        except:
            pass
        
        return "🔌 Cabo (Ethernet)"
    except:
        return "🔌 Cabo (Ethernet)"

def get_ip():
    """Obtém o IP local"""
    try:
        resultado = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True, text=True, timeout=5
        )
        if resultado.stdout:
            try:
                dados = json.loads(resultado.stdout)
                ip = dados.get("ip", "")
                if ip and ip != "N/A" and ip != "":
                    return ip
            except:
                pass
        
        resultado2 = subprocess.run(
            ["ip", "addr", "show", "wlan0"],
            capture_output=True, text=True, timeout=5
        )
        match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/\d+", resultado2.stdout)
        if match:
            return match.group(1)
        
        resultado3 = subprocess.run(
            ["ip", "addr", "show"],
            capture_output=True, text=True, timeout=5
        )
        match = re.search(r"inet (192\.168\.\d+\.\d+)/\d+", resultado3.stdout)
        if match:
            return match.group(1)
        
        return "N/A"
    except:
        return "N/A"

def ping_host(host, nome, count=4):
    """Faz ping em um host e retorna o tempo médio"""
    try:
        resultado = subprocess.run(
            ["ping", "-c", str(count), "-W", "2", host],
            capture_output=True, text=True, timeout=10
        )
        
        perda_match = re.search(r"(\d+)% packet loss", resultado.stdout)
        perda = int(perda_match.group(1)) if perda_match else 0
        
        avg_match = re.search(r"avg.*?([\d.]+)", resultado.stdout)
        if avg_match:
            tempo = float(avg_match.group(1))
            return {
                "host": nome,
                "ip": host,
                "tempo": tempo,
                "status": "🟢" if tempo < 50 else "🟡" if tempo < 150 else "🔴",
                "perda": perda
            }
        else:
            return {
                "host": nome,
                "ip": host,
                "tempo": None,
                "status": "🔴",
                "perda": 100
            }
    except:
        return {
            "host": nome,
            "ip": host,
            "tempo": None,
            "status": "🔴",
            "perda": 100
        }

def test_velocidade():
    """Testa velocidade de download e upload"""
    try:
        inicio = time.time()
        subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "--max-time", "10", "https://httpbin.org/bytes/1048576"],
            capture_output=True, timeout=15
        )
        tempo_download = time.time() - inicio
        download_mbps = (1048576 * 8) / (tempo_download * 1000000) if tempo_download > 0 else 0
        
        inicio = time.time()
        subprocess.run(
            ["curl", "-s", "-X", "POST", "--data-binary", "@/dev/zero", "--max-time", "10", "https://httpbin.org/post"],
            capture_output=True, timeout=15
        )
        tempo_upload = time.time() - inicio
        upload_mbps = (1048576 * 8) / (tempo_upload * 1000000) if tempo_upload > 0 else 0
        
        return {
            "download": round(download_mbps, 1),
            "upload": round(upload_mbps, 1)
        }
    except:
        return {"download": 0, "upload": 0}

def scan_dispositivos():
    """Escaneia dispositivos na rede"""
    try:
        resultado = subprocess.run(
            ["nmap", "-sn", REDE],
            capture_output=True, text=True, timeout=60
        )
        ips = re.findall(r"Nmap scan report for ([\d.]+)", resultado.stdout)
        
        dispositivos = []
        for ip in ips:
            nome = NOMES.get(ip, ip)
            dispositivos.append(nome)
        
        return dispositivos
    except:
        return ["N/A"]

def salvar_diagnostico(diagnostico):
    """Salva o diagnóstico em JSON"""
    try:
        with open(ARQUIVO_DADOS, "w") as f:
            json.dump(diagnostico, f, indent=4)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Diagnóstico salvo")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro ao salvar: {e}")

def coletar_diagnostico():
    """Coleta um diagnóstico completo da rede"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 Coletando diagnóstico...")
    
    gateway = get_gateway()
    ssid = get_ssid()
    ip_local = get_ip()
    
    ping_roteador = ping_host(gateway, "Roteador", 4)
    ping_dns = ping_host("8.8.8.8", "Google DNS", 4)
    ping_servidor = ping_host("1.1.1.1", "Cloudflare", 4)
    
    perda_media = round((ping_roteador["perda"] + ping_dns["perda"] + ping_servidor["perda"]) / 3, 1)
    velocidade = test_velocidade()
    dispositivos = scan_dispositivos()
    
    diagnostico = {
        "timestamp": datetime.now().isoformat(),
        "ssid": ssid,
        "ip_local": ip_local,
        "pings": {
            "roteador": {"tempo": ping_roteador["tempo"], "status": ping_roteador["status"]},
            "google_dns": {"tempo": ping_dns["tempo"], "status": ping_dns["status"]},
            "cloudflare": {"tempo": ping_servidor["tempo"], "status": ping_servidor["status"]}
        },
        "perda_pacotes": perda_media,
        "velocidade": velocidade,
        "dispositivos": dispositivos
    }
    
    salvar_diagnostico(diagnostico)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Diagnóstico coletado")
    
    return diagnostico

# ================= MAIN =================

def main():
    print(f"""
╔══════════════════════════════════════════╗
║        🌐 MONITOR DE REDE - SysCore      ║
║        Coleta silenciosa de dados        ║
║        Iniciado em: {datetime.now().strftime('%H:%M:%S')}     ║
╚══════════════════════════════════════════╝
    """)
    
    print(f"📡 Monitorando: {REDE}")
    print(f"⏱️  Intervalo: {INTERVALO}s")
    print("📁 Salvando dados em:", ARQUIVO_DADOS)
    print("-" * 50)
    
    # Coleta inicial
    coletar_diagnostico()
    
    # Loop principal
    while True:
        try:
            time.sleep(INTERVALO)
            coletar_diagnostico()
            
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Monitor interrompido")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
