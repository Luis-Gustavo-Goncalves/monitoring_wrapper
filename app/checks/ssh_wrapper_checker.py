''' Paramiko uma biblioteca que implementa o protocolo sshv2 para conexão, automação de tarefas administrativas, executando comandos remotos e transferência
arquivos sftp
'''
import paramiko

def verificar_wrapper(
        host,
        usuario,
        senha,
        caminho_bin='/usr/socin/econect/conc/bin',
        comando_status='./concentradorwrapper status',
        timeout=5
):
    '''
    Verifica o status do wrapper via SSH:

    Retorna:
    - 'RODANDO'
    - 'PARADO'
    - 'ERRO_CONEXAO'
    - 'ERRO_COMANDO'
    '''

    try:
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        cliente.connect(
            hostname=host,
            username=usuario,
            password=senha,
            timeout=timeout
        )

        comando = f'cd {caminho_bin} && {comando_status}'
        stdin, stdout, stderr = cliente.exec_command(comando)

        saida = stdout.read().decode().lower()
        erro = stderr.read().decode().lower()

        cliente.close()

        if erro:
            return 'ERRO_COMANDO'
        
        # Ajuste conforme a saída real do comando
        if 'not running' in saida:
            return 'PARADO'
        
        if 'is running' in saida or 'ativo' in saida or 'started' in saida:
            return 'RODANDO'
        
        return 'PARADO'

    except paramiko.AuthenticationException:
        return 'ERRO_CONEXAO'
    except paramiko.SSHException:
        return 'ERRO_CONEXAO'
    except Exception:
        return 'ERRO_CONEXAO' 