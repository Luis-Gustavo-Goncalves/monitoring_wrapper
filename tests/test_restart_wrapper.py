from app.actions.wrapper_restarter import tentar_restart_wrapper

resultado = tentar_restart_wrapper(
    host='192.168.1.9',
    usuario='econect',
    senha='econect'
)

print(f'Resultado do restart: {resultado}')

