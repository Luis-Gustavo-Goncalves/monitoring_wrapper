import requests
from datetime import datetime

WEBHOOK_URL = "https://lojasrede.webhook.office.com/webhookb2/58e28d90-4ca8-440a-aeb2-2c6b237ec8bd@f6c895c6-e8aa-427d-93b8-e885092bd61e/IncomingWebhook/9e936e32aea24c30ab0bab1b609e461b/5215d900-ba38-4b8b-bcae-15f665f27c3e/V2cNJ7hXHwlt8r7otLDkQU1PbmhdPkTaptRtAtimrXIHg1"


def enviar_alerta_teams(loja, host, mensagem, nivel="INFO"):

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    payload = {
        "text": f"""
🚨 MONITORAMENTO WRAPPER LOJAS

🏪 Loja: {loja}
🌐 Host: {host}
📊 Status: {mensagem}
⚠️ Nível: {nivel}
🕒 Hora: {agora}
"""
    }

    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=5)

    except Exception as erro:
        print("Falha ao enviar alerta Teams:", erro)