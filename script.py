import requests
import re
from urllib.parse import urljoin
import time
import os

URL_ALVO = "https://embedtv.best"
TIMEOUT = 20

def extrair_links_avancado():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://google.com/'
    }
    
    try:
        print(f"🔍 Conectando a {URL_ALVO}...")
        response = requests.get(URL_ALVO, headers=headers, timeout=TIMEOUT)
        
        if response.status_code == 200:
            print("✅ Site acessado com sucesso!")
            content = response.text
            
            # Padrões de busca aprimorados (Regex)
            padroes = [
                r'(https?://[^\s"\'\<\>]+\.m3u8[^\s"\'\<\>]*)',
                r'["\'](/[^"\']+\.m3u8[^"\']*)["\']',
                r'["\'](file|source|src|url)["\']\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']'
            ]
            
            todos_links = []
            for padrao in padroes:
                matches = re.findall(padrao, content, re.IGNORECASE)
                for m in matches:
                    link = m[1] if isinstance(m, tuple) else m
                    if link.startswith('//'): link = 'https:' + link
                    elif link.startswith('/'): link = urljoin(URL_ALVO, link)
                    
                    if '.m3u8' in link and not any(x in link for x in ['.css', '.js', '.png']):
                        todos_links.append(link)
            
            return sorted(list(set(todos_links)))
        return []
    except Exception as e:
        print(f"💥 Erro: {e}")
        return []

def salvar_lista(links):
    # Força o salvamento no diretório atual
    caminho = os.path.join(os.getcwd(), "lista_streams.m3u")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# Playlist Automatizada\n")
        f.write(f"# Gerada em: {time.strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        for i, link in enumerate(links, 1):
            f.write(f"#EXTINF:-1, Canal {i}\n{link}\n")
    print(f"💾 Arquivo salvo em: {caminho}")

if __name__ == "__main__":
    links = extrair_links_avancado()
    salvar_lista(links)
    print(f"🚀 Finalizado! {len(links)} links capturados.")
