import time
import paramiko
from app.core.logger import logger


def tentar_restart_wrapper(
    host: str,
    usuario: str,
    senha: str,
    caminho_bin: str,
    loja: str,
    timeout: int = 10,
) -> bool:
    """
    Executa restart REAL do wrapper:
    - Login como econect
    - sudo su (vira root)
    - executa ./concentradorwrapper restart
    """

    try:
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        cliente.connect(
            hostname=host,
            username=usuario,   # econect
            password=senha,     # econect
            timeout=timeout,
        )

        # 🔑 Shell interativo com PTY
        shell = cliente.invoke_shell()
        time.sleep(1)

        def enviar(cmd, espera=1.5):
            shell.send(cmd + "\n")
            time.sleep(espera)
            return shell.recv(65535).decode(errors="ignore")

        # 1️⃣ sudo su
        saida = enviar("sudo su", 1)

        if "password" in saida.lower():
            saida += enviar(senha, 2)

        logger.debug(
            "🔐 Elevação para root",
            extra={"loja": loja, "host": host, "saida": saida},
        )

        # 2️⃣ cd no bin
        enviar(f"cd {caminho_bin}", 1)

        # 3️⃣ restart REAL
        saida_restart = enviar("./concentradorwrapper restart", 6)

        logger.debug(
            "📄 Saída bruta do restart",
            extra={
                "loja": loja,
                "host": host,
                "saida": saida_restart,
            },
        )

        cliente.close()

        # ✅ Confirmação REALISTA (igual terminal)
        if (
            "stopping" in saida_restart.lower()
            and "starting" in saida_restart.lower()
            and "pid" in saida_restart.lower()
        ):
            logger.info(
                "♻️ Restart completo executado como ROOT",
                extra={"loja": loja, "host": host},
            )
            return True

        logger.critical(
            "⚠️ Restart executado, mas saída não confirma ciclo completo",
            extra={"loja": loja, "host": host, "saida": saida_restart},
        )
        return False

    except Exception as erro:
        logger.critical(
            "❌ Falha crítica ao executar restart como root",
            extra={"loja": loja, "host": host, "erro": str(erro)},
        )
        return False