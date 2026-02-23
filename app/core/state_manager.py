import json
import os
from datetime import datetime, timedelta

STATE_DIR = "state"
STATE_FILE = os.path.join(STATE_DIR, "wrappers.json")

MAX_TENTATIVAS = 3
COOLDOWN_MINUTOS = 5

os.makedirs(STATE_DIR, exist_ok=True)


def _carregar_estado():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar_estado(estado):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2)


def pode_tentar_restart(host):
    estado = _carregar_estado()
    agora = datetime.now()

    info = estado.get(host)

    if not info:
        return True

    tentativas = info["tentativas"]
    ultima_tentativa = datetime.fromisoformat(info["ultima_tentativa"])

    if tentativas >= MAX_TENTATIVAS:
        return False

    if agora - ultima_tentativa < timedelta(minutes=COOLDOWN_MINUTOS):
        return False

    return True


def registrar_tentativa(host):
    estado = _carregar_estado()
    agora = datetime.now()

    if host not in estado:
        estado[host] = {
            "tentativas": 1,
            "ultima_tentativa": agora.isoformat()
        }
    else:
        estado[host]["tentativas"] += 1
        estado[host]["ultima_tentativa"] = agora.isoformat()

    _salvar_estado(estado)


def resetar_estado(host):
    estado = _carregar_estado()
    if host in estado:
        del estado[host]
        _salvar_estado(estado)
