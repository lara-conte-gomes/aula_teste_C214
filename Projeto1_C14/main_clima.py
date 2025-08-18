import requests
from dotenv import load_dotenv
import os
from rich.console import Console
from urllib.parse import quote_plus  # Codificar a cidade pesquisada

#Carregar variáveis de ambiente
load_dotenv()

#Obter chave da API do arquivo .env
API_KEY = os.getenv("OPENWEATHER_API_KEY")

#Verificando a chave da API
print(f"Chave da API: {API_KEY}")

#URL da API do OpenWeather
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

#Consultando o clima
def obter_clima(cidade):
    cidade_codificada = quote_plus(cidade)  #Codificando a cidade
    url = f"{BASE_URL}q={cidade_codificada}&appid={API_KEY}&units=metric&lang=pt_br"

    #Print para verificar a URL gerada
    print(f"URL gerada: {url}")

    resposta = requests.get(url)

    #Saída de dados
    print(f"Código de status: {resposta.status_code}")  # Imprime o código de status
    print(f"Conteúdo da resposta: {resposta.text}")  # Imprime a resposta completa

    #Função padrão para coletar os dados da saída
    if resposta.status_code == 200:
        dados = resposta.json()
        temperatura = dados['main']['temp']
        descricao = dados['weather'][0]['description']
        return temperatura, descricao
    else:
        return None, None

def main():
    console = Console()
    cidade = input("Digite o nome da cidade: ")

    console.print("Consultando clima...", style="bold yellow")
    temperatura, descricao = obter_clima(cidade)

    if temperatura is not None:
        console.print(f"O clima em {cidade} é {descricao} com uma temperatura de {temperatura}°C.", style="bold green")
    else:
        console.print(f"Não foi possível obter as informações de clima para {cidade}.", style="bold red")

if __name__ == "__main__":
    main()
