from config.config_loader import carregar_lojas

if __name__ == "__main__":
    lojas = carregar_lojas()
    print(f"{len(lojas)} lojas carregadas com sucesso")
    print(lojas[0])
