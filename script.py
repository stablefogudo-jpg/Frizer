import requests
import re

# URL do site que contém os links
URL_ALVO = "https://embedtv.best" 

def extrair_links():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(URL_ALVO, headers=headers, timeout=10)
        content = response.text
        
        # Busca links m3u8 usando Expressão Regular
        links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.m3u8', content)
        
        # Remove duplicados e organiza
        links_unicos = sorted(list(set(links)))
        
        return links_unicos
    except Exception as e:
        print(f"Erro ao coletar: {e}")
        return []

def salvar_lista(links):
    with open("minha_lista.m3u", "w") as f:
        f.write("#EXTM3U\n")
        for link in links:
            # Aqui você pode personalizar o nome do canal se quiser
            f.write(f"#EXTINF:-1, Canal Atualizado\n{link}\n")

if __name__ == "__main__":
    links = extrair_links()
    if links:
        salvar_lista(links)
        print(f"Sucesso! {len(links)} links encontrados.")
    else:
        print("Nenhum link encontrado.")
