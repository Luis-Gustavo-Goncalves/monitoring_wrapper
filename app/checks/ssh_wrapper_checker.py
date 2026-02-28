import paramiko
from app.core.logger import logger


def verificar_wrapper(
    host: str,
    usuario: str,
    senha: str,
    caminho_bin: str,
    timeout: int = 8,
) -> str:
    """
    Verifica o status REAL do wrapper via SSH.

    Retorna:
    - 'RODANDO'      → confirmação explícita
    - 'PARADO'       → confirmação explícita
    - 'DESCONHECIDO' → qualquer falha ou saída ambígua
    """

    try:
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        cliente.connect(
            hostname=host,
            username=usuario,
            password=senha,
            timeout=timeout,
        )

        comando = f"cd {caminho_bin} && ./concentradorwrapper status"
        _, stdout, stderr = cliente.exec_command(comando)

        saida = stdout.read().decode(errors="ignore").lower().strip()
        erro = stderr.read().decode(errors="ignore").lower().strip()

        cliente.close()

        # 🔍 DEBUG CRÍTICO (para auditoria)
        logger.debug(
            "📄 Saída bruta do status do wrapper",
            extra={
                "host": host,
                "saida": saida,
                "erro": erro,
            }
        )

        # Qualquer erro explícito → estado inseguro
        if erro:
            return "DESCONHECIDO"

        # 🚫 PROVA DE PARADO
        if any(palavra in saida for palavra in [
            "not running",
            "stopped",
            "parado",
            "não está em execução",
        ]):
            return "PARADO"

        # ✅ PROVA DE RODANDO
        if any(palavra in saida for palavra in [
            "is running",
            "running",
            "ativo",
            "started",
        ]):
            return "RODANDO"

        # ⚠️ Qualquer outra coisa = inseguro
        return "DESCONHECIDO"

    except (
        paramiko.AuthenticationException,
        paramiko.SSHException,
        TimeoutError,
    ):
        return "DESCONHECIDO"

    except Exception as erro:
        logger.error(
            "❌ Erro inesperado ao verificar wrapper",
            extra={"host": host, "erro": str(erro)},
        )
        return "DESCONHECIDO"