# WeatherCLI 🌦️

Aplicativo de linha de comando em **Python** que consulta, em **tempo real**, as condições do tempo para **qualquer cidade do mundo** usando a API do **OpenWeather**.  
A saída é formatada no terminal com [Rich](https://github.com/Textualize/rich), com suporte a nomes de cidades com espaços e acentos.

---

## ✨ Funcionalidades

- Consulta do clima atual por **nome da cidade**.
- Retorno da **descrição** (ex.: "céu limpo", "chuva leve") e **temperatura** em °C.
- Saída colorida e amigável no terminal.
- **Idioma PT-BR** e **unidades métricas** já configurados.
- Tratamento básico de erros (cidade inexistente, chave inválida, limite da API).

---

## 📦 Requisitos

- Python **3.10+**
- Chave da API do [OpenWeather](https://openweathermap.org/api)

Dependências Python:
- `requests`
- `python-dotenv`
- `rich`

Instalação:

```bash
# criar ambiente virtual (opcional)
python -m venv .venv
# ativar ambiente
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# instalar dependências
pip install -r requirements.txt



-Foi incluído um arquivo .env que contém a chave da API. Dessa forma, o código fica dinâmico utilizando uma chave ativa. Caso haja necessidade, é só alterar o arquivo;
-Sugestão: Validar o git.ignore, pois o mesmo pode estar ignorando o .env;
-Comentei o print que mostrava a chave da API, visando deixar a saída mais fluída e limpa;

---

## 🔎 Regressões simuladas e correções

Como parte da atividade da disciplina, foram introduzidas regressões intencionais via **Pull Request (PR)** para validar a cobertura da suíte de testes.  

### 🚨 Erros introduzidos

1. **Remoção do parâmetro `timeout` em `requests.get`**
   - **Alteração:**  
     ```diff
- resp = requests.get(url, timeout=10)
+ resp = requests.get(url)  # regressão proposital
     ```
   - **Efeito:** o teste `test_ok_timeout_param_enviado` falhou, pois esperava que o parâmetro `timeout` fosse usado.  
   - **Resultado:** falha registrada no relatório do `pytest`.

2. **Troca da chave `'temp'` por `'temperature'`**
   - **Alteração:**  
     ```diff
- temperatura = dados.get("main", {}).get("temp")
+ temperatura = dados.get("main", {}).get("temperature")
     ```
   - **Efeito:** vários testes quebraram (`test_ok_retorna_tupla`, `test_ok_valores_corretos`, etc.), pois a função passou a retornar `None` em vez da temperatura correta.  

---

### ✅ Correções aplicadas

- Reintroduzido o parâmetro `timeout=10` na chamada `requests.get`.  
- Restaurada a chave correta `'temp'` no dicionário retornado pela API.  

Após as correções, todos os testes passaram novamente:  

```bash
pytest -q
# saída esperada
....................   [20 passed]



