import time

from config.config_loader import carregar_lojas
from app.checks.ping_checker import ping_host
from app.checks.ssh_wrapper_checker import verificar_wrapper
from app.actions.wrapper_restarter import tentar_restart_wrapper
from app.core.logger import logger
from utils.cooldown import em_cooldown, registrar_start


INTERVALO_ENTRE_LOJAS = 30
INTERVALO_CICLO_COMPLETO = 60


def monitorar_lojas():
    logger.info("🚀 Monitor iniciado")

    lojas = carregar_lojas()

    while True:
        for loja in lojas:
            loja_id = loja["loja"]
            host = loja["ip"]
            usuario = loja["usuario"]
            senha = loja["senha"]
            caminho_bin = loja["caminho_bin"]

            identificador = f"loja_{loja_id}_{host}"

            logger.info(
                "🏪 Iniciando verificação",
                extra={"loja": loja_id, "host": host},
            )

            # 1️⃣ Ping
            if not ping_host(host):
                logger.warning(
                    "📡 Loja offline (ping)",
                    extra={"loja": loja_id, "host": host},
                )
                continue

            # 2️⃣ Status real
            status = verificar_wrapper(
                host=host,
                usuario=usuario,
                senha=senha,
                caminho_bin=caminho_bin,
            )

            logger.info(
                "⚙️ Status do wrapper",
                extra={"loja": loja_id, "host": host, "status": status},
            )

            if status == "RODANDO":
                logger.info(
                    "✅ Wrapper rodando normalmente",
                    extra={"loja": loja_id, "host": host},
                )
                continue

            if status == "DESCONHECIDO":
                logger.warning(
                    "🚧 Estado inseguro. Nenhuma ação tomada.",
                    extra={"loja": loja_id, "host": host},
                )
                continue

            if status == "PARADO":

                if em_cooldown(identificador):
                    logger.warning(
                        "⏱️ Em cooldown. Restart bloqueado.",
                        extra={"loja": loja_id, "host": host},
                    )
                    continue

                logger.error(
                    "🛑 Wrapper parado. Executando RESTART forçado",
                    extra={"loja": loja_id, "host": host},
                )

                sucesso = tentar_restart_wrapper(
                    host=host,
                    usuario=usuario,
                    senha=senha,
                    caminho_bin=caminho_bin,
                    loja=loja_id,
                )

                if sucesso:
                    registrar_start(identificador)
                    logger.info(
                        "✅ Restart confirmado e cooldown registrado",
                        extra={"loja": loja_id, "host": host},
                    )
                else:
                    logger.critical(
                        "🚨 Restart falhou. Wrapper permanece instável",
                        extra={"loja": loja_id, "host": host},
                    )

            time.sleep(INTERVALO_ENTRE_LOJAS)

        logger.info(
            "🔄 Ciclo completo finalizado",
            extra={"intervalo": INTERVALO_CICLO_COMPLETO},
        )

        time.sleep(INTERVALO_CICLO_COMPLETO)


if __name__ == "__main__":
    monitorar_lojas()