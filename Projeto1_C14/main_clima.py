import os
from urllib.parse import quote_plus
import requests
from typing import Tuple, Optional

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def obter_clima_atual(cidade: str, *, timeout: int = 10) -> Tuple[Optional[float], Optional[str]]:
    """
    Retorna (temperatura_em_celsius, descricao) ou (None, None) em caso de erro.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return (None, None)

    try:
        q = quote_plus(cidade)  # codifica acentos e espaços
        url = f"{BASE_URL}?q={q}&appid={api_key}&units=metric&lang=pt_br"

        resp = requests.get(url, timeout=timeout)

        # Qualquer 4xx/5xx -> erro
        if resp.status_code >= 400:
            return (None, None)

        data = resp.json()

        main = data.get("main") or {}
        weather = data.get("weather") or []

        if "temp" not in main or not weather:
            return (None, None)

        temp = float(main["temp"])
        desc = str(weather[0].get("description", ""))

        return (temp, desc)
    except Exception:
        # Inclui: Timeout, ConnectionError, JSON inválido, etc.
        return (None, None)
