# Time fornece funções para trabalhar com o tempo, como medir o tempo da execução de um código e pausar a execução do programa
import time
import paramiko
from app.checks.ssh_wrapper_checker import verificar_wrapper
from app.core.state_manager import (
    pode_tentar_restart,
    registrar_tentativa,
    resetar_estado
)
from app.core.logger import logger


def tentar_restart_wrapper(
    loja,
    host,
    usuario,
    senha,
    caminho_bin="/usr/socin/econect/conc/bin",
    wait_seconds=10
):
    if not pode_tentar_restart(host):
        logger.critical(
            f"Wrapper instavel | host={host} | Wrapper instável — caiu novamente após restart automático"
        )
        return "FALHA_RESTART"

    registrar_tentativa(host)

    try:
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(
            hostname=host,
            username=usuario,
            password=senha,
            timeout=10
        )

        comandos = [
            f"cd {caminho_bin} && ./concentradorwrapper stop",
            f"cd {caminho_bin} && ./concentradorwrapper start"
        ]

        for cmd in comandos:
            stdin, stdout, stderr = cliente.exec_command(cmd)
            stdout.channel.recv_exit_status()

        cliente.close()

        time.sleep(wait_seconds)

        status = verificar_wrapper(
            host=host,
            usuario=usuario,
            senha=senha,
            caminho_bin=caminho_bin
        )

        if status == "RODANDO":
            logger.info(
                f"Wrapper recuperado | host={host} | resetando contador de falhas"
            )
            resetar_estado(host)
            return "RECUPERADO"

        logger.warning(
            f"Wrapper ainda parado | host={host} | tentativa registrada"
        )
        return "FALHA_RESTART"

    except Exception as e:
        logger.error(
            f"Erro ao tentar restart | host={host} | erro={e}"
        )
        return "ERRO_CONEXAO"
