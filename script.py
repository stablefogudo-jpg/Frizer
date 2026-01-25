import requests
import re

URL_ALVO = "https://embedtv.best" 

def extrair_links():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    }
    try:
        print(f"Conectando a {URL_ALVO}...")
        # Definimos um timeout de 15 segundos para não travar
        response = requests.get(URL_ALVO, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print("Site acessado com sucesso! Buscando links...")
            content = response.text
            # Busca links m3u8
            links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.m3u8', content)
            return sorted(list(set(links)))
        else:
            print(f"O site bloqueou o acesso. Código: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro na conexão (o site pode estar protegendo contra bots): {e}")
        return []

def salvar_lista(links):
    with open("minha_lista.m3u", "w") as f:
        f.write("#EXTM3U\n")
        if not links:
            f.write("# AVISO: Nenhum link foi encontrado hoje. O site pode ter mudado a estrutura.\n")
        for i, link in enumerate(links):
            f.write(f"#EXTINF:-1, Canal Atualizado {i+1}\n{link}\n")

if __name__ == "__main__":
    links = extrair_links()
    salvar_lista(links)
    print(f"Fim do processo. Links encontrados: {len(links)}")
