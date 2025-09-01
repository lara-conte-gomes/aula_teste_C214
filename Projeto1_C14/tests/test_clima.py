import os
import types
import json
import builtins
import pytest
from urllib.parse import quote_plus

# Importa a função alvo
import importlib
main_mod = importlib.import_module("main_clima")
obter_clima_atual = main_mod.obter_clima_atual

# ---------- Helpers de mock ----------

class FakeResp:
    def __init__(self, status_code=200, json_data=None, text=None, raise_for_status=False):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text if text is not None else json.dumps(self._json)
        self._raise = raise_for_status

    def json(self):
        return self._json

    def raise_for_status(self):
        if self._raise:
            import requests
            raise requests.HTTPError(f"Status {self.status_code}")

def make_get_stub(payload=None, status_code=200, raises=None, capture_url=None):
    """
    Retorna uma função stub para substituir requests.get.
    - raises: exceção a lançar
    - capture_url: lista mutável onde o primeiro argumento (url) será gravado
    """
    def _stub(url, timeout=None):
        if capture_url is not None:
            capture_url.append(url)
        if raises:
            raise raises
        return FakeResp(status_code=status_code, json_data=payload,
                        text=json.dumps(payload or {}),
                        raise_for_status=(status_code >= 400))
    return _stub

# ---------- Fixtures ----------
@pytest.fixture(autouse=True)
def ensure_api_key(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "DUMMY_KEY")
    importlib.reload(main_mod)
    yield

# ========== TESTES POSITIVOS ==========

def test_ok_retorna_tupla(monkeypatch):
    payload = {"main": {"temp": 21.5}, "weather": [{"description": "céu limpo"}]}
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    temp, desc = obter_clima_atual("Santa Rita do Sapucaí")
    assert isinstance(temp, (int, float)) and isinstance(desc, str)

def test_ok_valores_corretos(monkeypatch):
    payload = {"main": {"temp": -3.2}, "weather": [{"description": "neve leve"}]}
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    temp, desc = obter_clima_atual("Gramado")
    assert temp == -3.2 and desc == "neve leve"

def test_ok_suporta_acentos_e_espacos(monkeypatch):
    payload = {"main": {"temp": 25.0}, "weather": [{"description": "nublado"}]}
    captured = []
    monkeypatch.setattr("requests.get", make_get_stub(payload, capture_url=captured))
    temp, desc = obter_clima_atual("São Paulo")
    expected = f"q={quote_plus('São Paulo')}"  # -> "q=S%C3%A3o+Paulo"
    assert expected in captured[0]
    assert temp == 25.0 and desc == "nublado"

def test_ok_temp_zero(monkeypatch):
    payload = {"main": {"temp": 0.0}, "weather": [{"description": "neblina"}]}
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    temp, _ = obter_clima_atual("Curitiba")
    assert temp == 0.0

def test_ok_temp_negativa(monkeypatch):
    payload = {"main": {"temp": -0.1}, "weather": [{"description": "frio"}]}
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    temp, _ = obter_clima_atual("Ushuaia")
    assert temp < 0

def test_ok_temp_alta(monkeypatch):
    payload = {"main": {"temp": 45.3}, "weather": [{"description": "calor extremo"}]}
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    temp, _ = obter_clima_atual("Cuiabá")
    assert temp > 45

def test_ok_ignora_campos_extras(monkeypatch):
    payload = {
        "coord": {"lon": 0, "lat": 0},
        "main": {"temp": 19.14, "humidity": 59},
        "weather": [{"id": 803, "main": "Clouds", "description": "nublado", "icon": "04n"}],
        "wind": {"speed": 3.08},
    }
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    temp, desc = obter_clima_atual("Teste")
    assert temp == 19.14 and desc == "nublado"

def test_ok_varias_condicoes_climaticas(monkeypatch):
    payload = {"main": {"temp": 10.0}, "weather": [{"description": "chuva"}, {"description": "vento"}]}
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    temp, desc = obter_clima_atual("Porto Alegre")
    assert desc == "chuva"

def test_ok_nao_explode_com_descricoes_longas(monkeypatch):
    long_desc = "muito " * 50 + "nublado"
    payload = {"main": {"temp": 22.2}, "weather": [{"description": long_desc}]}
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    temp, desc = obter_clima_atual("Rio")
    assert desc.endswith("nublado") and temp == 22.2

def test_ok_timeout_param_enviado(monkeypatch):
    seen = {"timeout": None}
    def spy(url, timeout=None):
        seen["timeout"] = timeout
        return FakeResp(json_data={"main": {"temp": 20}, "weather": [{"description": "ok"}]})
    monkeypatch.setattr("requests.get", spy)
    temp, _ = obter_clima_atual("BH")
    assert seen["timeout"] is not None and temp == 20

# ========== TESTES NEGATIVOS ==========

def test_erro_sem_api_key(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    importlib.reload(main_mod)
    assert main_mod.obter_clima_atual("Cidade") == (None, None)

def test_erro_401_na_api(monkeypatch):
    payload = {"cod": 401, "message": "Invalid API key"}
    monkeypatch.setattr("requests.get", make_get_stub(payload, status_code=401))
    assert obter_clima_atual("Cidade") == (None, None)

def test_erro_404_cidade_inexistente(monkeypatch):
    payload = {"cod": "404", "message": "city not found"}
    monkeypatch.setattr("requests.get", make_get_stub(payload, status_code=404))
    assert obter_clima_atual("Xyzzzy") == (None, None)

def test_erro_500_servidor(monkeypatch):
    payload = {"cod": 500, "message": "server error"}
    monkeypatch.setattr("requests.get", make_get_stub(payload, status_code=500))
    assert obter_clima_atual("Cidade") == (None, None)

def test_erro_timeout(monkeypatch):
    import requests
    monkeypatch.setattr("requests.get", make_get_stub(raises=requests.Timeout()))
    assert obter_clima_atual("Cidade") == (None, None)

def test_erro_conexao(monkeypatch):
    import requests
    monkeypatch.setattr("requests.get", make_get_stub(raises=requests.ConnectionError()))
    assert obter_clima_atual("Cidade") == (None, None)

def test_erro_json_malformado(monkeypatch):
    class BadResp(FakeResp):
        def json(self):
            raise ValueError("malformed")
    def bad_get(url, timeout=None):
        return BadResp(json_data=None)
    monkeypatch.setattr("requests.get", bad_get)
    assert obter_clima_atual("Cidade") == (None, None)

def test_erro_sem_main(monkeypatch):
    payload = {"weather": [{"description": "ok"}]}
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    assert obter_clima_atual("Cidade") == (None, None)

def test_erro_sem_weather(monkeypatch):
    payload = {"main": {"temp": 18.0}}
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    assert obter_clima_atual("Cidade") == (None, None)

def test_erro_lista_weather_vazia(monkeypatch):
    payload = {"main": {"temp": 18.0}, "weather": []}
    monkeypatch.setattr("requests.get", make_get_stub(payload))
    assert obter_clima_atual("Cidade") == (None, None)
