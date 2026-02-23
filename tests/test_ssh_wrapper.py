from app.actions.wrapper_restarter import verificar_wrapper

status = verificar_wrapper(
    host='192.168.87.21',
    usuario = 'econect',
    senha = 'econect'
)

print(f'Status do wrapper: {status}')