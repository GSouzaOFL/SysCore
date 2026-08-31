#!/usr/bin/env python3
# ============================================
# MONITOR DO SISTEMA - SysCore
# Coleta silenciosa de dados do sistema
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

def executar_comando(comando, use_root=False):
    """Executa um comando no shell, com ou sem root"""
    try:
        if use_root:
            # Tenta com tsu
            cmd = f"tsu -c '{comando}'"
            resultado = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=10, shell=True
            )
            if resultado.returncode == 0 and resultado.stdout.strip():
                return resultado.stdout.strip(), ""
            
            # Se falhar, tenta com su (fallback)
            cmd = f"su -c '{comando}'"
            resultado = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=10, shell=True
            )
            if resultado.returncode == 0 and resultado.stdout.strip():
                return resultado.stdout.strip(), ""
            
            # Se ainda falhar, tenta sem root (fallback)
            resultado = subprocess.run(
                comando,
                capture_output=True, text=True, timeout=10, shell=True
            )
            return resultado.stdout.strip(), resultado.stderr.strip()
        else:
            resultado = subprocess.run(
                comando,
                capture_output=True, text=True, timeout=10, shell=True
            )
            return resultado.stdout.strip(), resultado.stderr.strip()
    except Exception as e:
        return "", str(e)

def get_bateria():
    """Obtém informações da bateria"""
    try:
        resultado = subprocess.run(
            ["termux-battery-status"],
            capture_output=True, text=True, timeout=5
        )
        dados = json.loads(resultado.stdout)
        return {
            "nivel": dados.get("percentage", "N/A"),
            "status": dados.get("status", "N/A"),
            "temperatura": dados.get("temperature", "N/A")
        }
    except Exception as e:
        return {"erro": str(e)}

def get_cpu():
    """Obtém informações da CPU com root"""
    try:
        uso = "N/A"
        freq_mhz = "N/A"
        
        # Tenta ler /proc/stat com root
        stdout, stderr = executar_comando("cat /proc/stat | head -n 1", use_root=True)
        if stdout:
            partes = stdout.split()
            if len(partes) >= 5 and partes[0] == "cpu":
                user = int(partes[1])
                nice = int(partes[2])
                system = int(partes[3])
                idle = int(partes[4])
                total = user + nice + system + idle
                if total > 0:
                    uso = round(((user + nice + system) / total) * 100, 1)
        else:
            # Fallback: tenta sem root
            try:
                with open("/proc/stat", "r") as f:
                    linha = f.readline().strip()
                partes = linha.split()
                if len(partes) >= 5 and partes[0] == "cpu":
                    user = int(partes[1])
                    nice = int(partes[2])
                    system = int(partes[3])
                    idle = int(partes[4])
                    total = user + nice + system + idle
                    if total > 0:
                        uso = round(((user + nice + system) / total) * 100, 1)
            except:
                pass
        
        # Frequência da CPU
        stdout, _ = executar_comando("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", use_root=True)
        if stdout:
            try:
                freq_mhz = int(stdout.strip()) // 1000
            except:
                freq_mhz = "N/A"
        
        return {
            "uso": f"{uso:.1f}%" if uso != "N/A" else "N/A",
            "frequencia": freq_mhz if freq_mhz != "N/A" else "N/A"
        }
    except Exception as e:
        return {"erro": str(e)}

def get_gpu():
    """Obtém informações da GPU com root"""
    try:
        modelo_gpu = "N/A"
        freq_mhz = "N/A"
        temp = "N/A"
        uso_gpu = "N/A"
        
        # Modelo da GPU
        stdout, _ = executar_comando("getprop ro.hardware", use_root=False)
        hardware = stdout.strip() or "Desconhecido"
        modelo_gpu = f"Adreno 508 ({hardware})"
        
        # Frequência da GPU
        stdout, _ = executar_comando("cat /sys/class/kgsl/kgsl-3d0/gpuclk", use_root=True)
        if stdout:
            try:
                freq_hz = int(stdout.strip())
                freq_mhz = freq_hz // 1000000
            except:
                freq_mhz = "N/A"
        
        # Temperatura da GPU
        stdout, _ = executar_comando("cat /sys/class/thermal/thermal_zone0/temp", use_root=True)
        if stdout:
            try:
                temp = int(stdout.strip()) / 1000
            except:
                temp = "N/A"
        
        # Uso da GPU
        stdout, _ = executar_comando("cat /sys/class/kgsl/kgsl-3d0/gpubusy", use_root=True)
        if stdout:
            try:
                partes = stdout.split()
                if len(partes) >= 2:
                    uso_gpu = round((int(partes[0]) / int(partes[1])) * 100, 1)
            except:
                uso_gpu = "N/A"
        
        return {
            "modelo": modelo_gpu,
            "frequencia": freq_mhz if freq_mhz != "N/A" else "N/A",
            "temperatura": temp if temp != "N/A" else "N/A",
            "uso": f"{uso_gpu}%" if uso_gpu != "N/A" else "N/A"
        }
    except Exception as e:
        return {"erro": str(e)}

def get_ram():
    """Obtém informações da RAM"""
    try:
        resultado = subprocess.run(
            ["free", "-h"],
            capture_output=True, text=True, timeout=5
        )
        for linha in resultado.stdout.split("\n"):
            if "Mem:" in linha:
                partes = linha.split()
                total = converter_unidade(partes[1]) if len(partes) > 1 else "N/A"
                usado = converter_unidade(partes[2]) if len(partes) > 2 else "N/A"
                disponivel = converter_unidade(partes[3]) if len(partes) > 3 else "N/A"
                
                try:
                    resultado_kb = subprocess.run(
                        ["free"],
                        capture_output=True, text=True, timeout=5
                    )
                    for linha_kb in resultado_kb.stdout.split("\n"):
                        if "Mem:" in linha_kb:
                            partes_kb = linha_kb.split()
                            total_kb = int(partes_kb[1])
                            usado_kb = int(partes_kb[2])
                            porcentagem = round((usado_kb / total_kb) * 100, 1)
                            break
                except:
                    porcentagem = "N/A"
                
                return {
                    "total": total,
                    "usado": usado,
                    "disponivel": disponivel,
                    "porcentagem": f"{porcentagem}%" if porcentagem != "N/A" else "N/A"
                }
        return {"erro": "Não foi possível ler RAM"}
    except Exception as e:
        return {"erro": str(e)}

def get_armazenamento():
    """Obtém informações do armazenamento"""
    try:
        armazenamentos = {}
        for mount in ["/data", "/sdcard"]:
            try:
                resultado = subprocess.run(
                    ["df", "-h", mount],
                    capture_output=True, text=True, timeout=5
                )
                for linha in resultado.stdout.split("\n"):
                    if mount in linha:
                        partes = linha.split()
                        if len(partes) >= 4:
                            nome = "Interno" if mount == "/data" else "SD Card"
                            armazenamentos[nome] = {
                                "total": converter_unidade(partes[1]),
                                "usado": converter_unidade(partes[2]),
                                "disponivel": converter_unidade(partes[3])
                            }
            except:
                pass
        return armazenamentos if armazenamentos else {"erro": "Nenhum dispositivo"}
    except Exception as e:
        return {"erro": str(e)}

def converter_unidade(valor):
    """Converte unidades para formato padronizado (GB, MB)"""
    if not valor:
        return "N/A"
    
    valor = valor.strip()
    
    if "Gi" in valor:
        valor = valor.replace("Gi", "GB")
    elif "Mi" in valor:
        valor = valor.replace("Mi", "MB")
    elif "G" in valor and "B" not in valor:
        valor = valor.replace("G", "GB")
    elif "M" in valor and "B" not in valor:
        valor = valor.replace("M", "MB")
    
    return valor

def get_modelo():
    """Obtém modelo do dispositivo"""
    try:
        modelo = subprocess.run(
            ["getprop", "ro.product.model"],
            capture_output=True, text=True, timeout=5
        )
        return modelo.stdout.strip() or "Desconhecido"
    except:
        return "Desconhecido"

def salvar_relatorio(relatorio):
    """Salva o relatório em JSON"""
    try:
        with open(ARQUIVO_DADOS, "w") as f:
            json.dump(relatorio, f, indent=4)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Relatório salvo")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro ao salvar: {e}")

def coletar_relatorio():
    """Coleta um relatório completo do sistema"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Coletando relatório do sistema...")
    
    modelo = get_modelo()
    bateria = get_bateria()
    cpu = get_cpu()
    gpu = get_gpu()
    ram = get_ram()
    armazenamento = get_armazenamento()
    
    relatorio = {
        "timestamp": datetime.now().isoformat(),
        "modelo": modelo,
        "bateria": bateria,
        "cpu": cpu,
        "gpu": gpu,
        "ram": ram,
        "armazenamento": armazenamento
    }
    
    salvar_relatorio(relatorio)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Relatório coletado")
    
    return relatorio

# ================= MAIN =================

def main():
    print(f"""
╔══════════════════════════════════════════╗
║        📊 MONITOR DO SISTEMA - SysCore   ║
║        Coleta silenciosa de dados        ║
║        Iniciado em: {datetime.now().strftime('%H:%M:%S')}     ║
╚══════════════════════════════════════════╝
    """)
    
    print(f"⏱️  Intervalo: {INTERVALO}s")
    print("📁 Salvando dados em:", ARQUIVO_DADOS)
    print("-" * 50)
    
    # Coleta inicial
    coletar_relatorio()
    
    # Loop principal
    while True:
        try:
            time.sleep(INTERVALO)
            coletar_relatorio()
            
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Monitor interrompido")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
