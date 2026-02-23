import time

from config.config_loader import carregar_lojas
from app.checks.ping_checker import ping_host
from app.checks.ssh_wrapper_checker import verificar_wrapper
from app.actions.wrapper_restarter import tentar_restart_wrapper
from app.core.logger import logger


INTERVALO_ENTRE_LOJAS = 5      # segundos
INTERVALO_CICLO_COMPLETO = 60 # segundos


def monitorar_lojas():
    logger.info("Monitor iniciado")

    lojas = carregar_lojas()

    while True:
        for loja in lojas:
            loja_id = loja["loja"]
            host = loja["ip"]
            usuario = loja["usuario"]
            senha = loja["senha"]
            caminho_bin = loja["caminho_bin"]

            logger.info(
                "Iniciando verificacao",
                extra={"loja": loja_id, "host": host}
            )

            # 1️⃣ Ping
            if not ping_host(host):
                logger.warning(
                    "Loja offline (ping)",
                    extra={"loja": loja_id, "host": host}
                )
                continue

            # 2️⃣ Status do wrapper
            status = verificar_wrapper(
                host=host,
                usuario=usuario,
                senha=senha,
                caminho_bin=caminho_bin
            )

            logger.info(
                "Status wrapper",
                extra={"loja": loja_id, "host": host, "status": status}
            )

            # 3️⃣ Se não estiver rodando → tentar restart
            if status != "RODANDO":
                logger.warning(
                    "Wrapper parado",
                    extra={"loja": loja_id, "host": host}
                )

                resultado = tentar_restart_wrapper(
                    host=host,
                    usuario=usuario,
                    senha=senha,
                    caminho_bin=caminho_bin,
                    loja=loja_id
                )

                logger.warning(
                    "Resultado do restart",
                    extra={"loja": loja_id, "host": host, "resultado": resultado}
                )

            time.sleep(INTERVALO_ENTRE_LOJAS)

        logger.info(
            "Ciclo completo finalizado, aguardando proximo ciclo",
            extra={"intervalo": INTERVALO_CICLO_COMPLETO}
        )
        time.sleep(INTERVALO_CICLO_COMPLETO)


if __name__ == "__main__":
    monitorar_lojas()
