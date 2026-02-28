import json
import time
from pathlib import Path

# Diretório onde o estado de cooldown será salvo
COOLDOWN_DIR = Path(__file__).resolve().parent / "cooldown"
COOLDOWN_DIR.mkdir(exist_ok=True)

# Tempo mínimo entre tentativas de start (15 minutos)
# Evita loop de restart que pode impactar a subida de vendas
COOLDOWN_SEGUNDOS = 900


def em_cooldown(identificador: str) -> bool:
    """
    Retorna True se ainda estiver dentro do cooldown.
    Fail-safe: qualquer erro bloqueia novo start.
    """
    arquivo = COOLDOWN_DIR / f"{identificador}.json"

    if not arquivo.exists():
        return False

    try:
        dados = json.loads(arquivo.read_text())
        ultimo_start = dados.get("ultimo_start", 0)

        return (time.time() - ultimo_start) < COOLDOWN_SEGUNDOS

    except Exception:
        # Falha = comportamento seguro (não starta)
        return True


def registrar_start(identificador: str) -> None:
    """
    Registra o horário do último start realizado.
    """
    arquivo = COOLDOWN_DIR / f"{identificador}.json"

    dados = {
        "ultimo_start": time.time()
    }

    arquivo.write_text(json.dumps(dados, indent=2))