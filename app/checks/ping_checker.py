# Subprocess, permite executar comandos do sistema operacional, ex: ping.
import subprocess
# Platform usado para acessar dados subjacentes em nivel de sistema, como sistema operacional, ex: nome do sitema 'Windows ou linux'
import platform

# Função ping
def ping_host(host, timeout=1, tentativas=2):
    """
    Testa conectividade com um host usando ping no linux.

    param host: IP ou hostname do concentrador
    param timeout:  tempo máximo de espera por resposta (segundos)
    param tentativas: quantidade de tentativas de ping
    return: 'ONLINE', 'OFFLENE', ou 'ERRO'
    """

    sistema = platform.system()

    for _ in range(tentativas):
        try:
            if sistema == 'Windows':
                # -n 1 = 1 pacote
                # -w timeout em milissegundos
                comando = ['ping', '-n', '1', '-w', str(timeout * 1000), host]
            else:
                # Linux / Unix
                comando = ['ping', 'c', '1', '-w', str(timeout), host]            
            
            resultado = subprocess.run(
                comando,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Código de retorno 0 significa que o host respondeu
            if resultado.returncode == 0:
                return 'ONLINE'
        
        except Exception:
            return 'ERRO'
    
    # Se nehuma tentativa respondeu
    return 'OFFLINE'

