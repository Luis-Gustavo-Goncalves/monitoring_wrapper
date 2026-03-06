import time

from config.config_loader import carregar_lojas
from app.checks.ping_checker import ping_host
from app.checks.ssh_wrapper_checker import verificar_wrapper
from app.actions.wrapper_restarter import tentar_restart_wrapper
from app.core.logger import logger
from utils.cooldown import em_cooldown, registrar_start
from app.notifications.teams_notifier import enviar_alerta_teams


INTERVALO_ENTRE_LOJAS = 30
INTERVALO_CICLO_COMPLETO = 60

TEMPO_OFFLINE_ALERTA = 300  # 5 minutos

offline_control = {}


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

            identificador = f"{loja_id}_{host}"

            logger.info(
                "🏪 Iniciando verificação",
                extra={"loja": loja_id, "host": host},
            )

            # Ping
            ping = ping_host(host)

            agora = time.time()

            if not ping:

                logger.warning(
                    "📡 Sem resposta no ping",
                    extra={"loja": loja_id, "host": host},
                )

                if identificador not in offline_control:

                    offline_control[identificador] = {
                        "inicio": agora,
                        "alertado": False
                    }

                    logger.warning(
                        "⏳ Iniciando contagem de offline",
                        extra={"loja": loja_id, "host": host},
                    )

                tempo_offline = agora - offline_control[identificador]["inicio"]

                logger.info(
                    f"⏱️ Offline há {int(tempo_offline)} segundos",
                    extra={"loja": loja_id, "host": host},
                )

                if tempo_offline >= TEMPO_OFFLINE_ALERTA and not offline_control[identificador]["alertado"]:

                    logger.critical(
                        "🚨 Concentrador OFFLINE > 5 minutos",
                        extra={"loja": loja_id, "host": host},
                    )

                    enviar_alerta_teams(
                        loja_id,
                        host,
                        "Concentrador OFFLINE há mais de 5 minutos",
                        "CRITICAL"
                    )

                    offline_control[identificador]["alertado"] = True

                time.sleep(INTERVALO_ENTRE_LOJAS)
                continue

            # VOLTOU ONLINE
            if identificador in offline_control:

                tempo_offline = agora - offline_control[identificador]["inicio"]

                logger.info(
                    f"🌐 Loja voltou online após {int(tempo_offline)} segundos",
                    extra={"loja": loja_id, "host": host},
                )

                enviar_alerta_teams(
                    loja_id,
                    host,
                    f"Concentrador voltou online após {int(tempo_offline)} segundos",
                    "INFO"
                )

                del offline_control[identificador]

            # VERIFICAR WRAPPER
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

                time.sleep(INTERVALO_ENTRE_LOJAS)
                continue

            if status == "DESCONHECIDO":

                logger.warning(
                    "🚧 Estado desconhecido",
                    extra={"loja": loja_id, "host": host},
                )

                time.sleep(INTERVALO_ENTRE_LOJAS)
                continue

            # WRAPPER PARADO
            if status == "PARADO":

                if em_cooldown(identificador):

                    logger.warning(
                        "⏱️ Em cooldown. Restart bloqueado",
                        extra={"loja": loja_id, "host": host},
                    )

                    enviar_alerta_teams(
                        loja_id,
                        host,
                        "Wrapper parado detectado (cooldown ativo)",
                        "WARNING"
                    )

                    time.sleep(INTERVALO_ENTRE_LOJAS)
                    continue

                logger.error(
                    "🛑 Wrapper parado. Reiniciando",
                    extra={"loja": loja_id, "host": host},
                )

                enviar_alerta_teams(
                    loja_id,
                    host,
                    "Wrapper parado detectado. Reiniciando automaticamente.",
                    "CRITICAL"
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
                        "✅ Restart realizado",
                        extra={"loja": loja_id, "host": host},
                    )

                    enviar_alerta_teams(
                        loja_id,
                        host,
                        "Wrapper reiniciado com sucesso",
                        "INFO"
                    )

                else:

                    logger.critical(
                        "🚨 Falha ao reiniciar wrapper",
                        extra={"loja": loja_id, "host": host},
                    )

                    enviar_alerta_teams(
                        loja_id,
                        host,
                        "Falha ao reiniciar wrapper automaticamente",
                        "CRITICAL"
                    )

            time.sleep(INTERVALO_ENTRE_LOJAS)

        logger.info(
            "🔄 Ciclo completo finalizado",
            extra={"intervalo": INTERVALO_CICLO_COMPLETO},
        )

        time.sleep(INTERVALO_CICLO_COMPLETO)


if __name__ == "__main__":
    monitorar_lojas()