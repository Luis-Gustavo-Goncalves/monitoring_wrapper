from app.checks.ping_checker import ping_host

hosts = [
    '8.8.8.8',
    '127.0.0.1',
    '192.0.2.1'
]

for host in hosts:
    status = ping_host(host)
    print(f'{host} -> {status}')