from playwright.sync_api import sync_playwright
import time
from datetime import datetime

# URL Alvo
URL_ALVO = "https://www2.embedtv.best/premiere"

# PROXY BRASILEIRO (Se parar de funcionar, troque por um novo IP do Brasil)
# Formato: http://IP:PORTA
PROXY_BR = "http://168.205.234.18:8080" 

def coletar_com_proxy():
    links_encontrados = []
    with sync_playwright() as p:
        print(f"🇧🇷 Tentando capturar via Proxy Brasil: {PROXY_BR}")
        try:
            # Lança o navegador configurado com o Proxy
            browser = p.chromium.launch(
                headless=True,
                proxy={"server": PROXY_BR}
            )
            # Define o idioma para PT-BR para reforçar a localização
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                locale="pt-BR"
            )
            page = context.new_page()

            # Escuta o tráfego de rede em busca do m3u8
            def interceptar(request):
                url = request.url
                if ".m3u8" in url and "chunklist" not in url:
                    if url not in links_encontrados:
                        print(f"🔗 Link capturado: {url[:60]}...")
                        links_encontrados.append(url)

            page.on("request", interceptar)

            # Timeout alto (90s) porque o proxy pode ser lento
            page.goto(URL_ALVO, wait_until="networkidle", timeout=90000)
            
            # Simula um clique no centro para disparar o player
            page.mouse.click(400, 300)
            time.sleep(20) 

            browser.close()
        except Exception as e:
            print(f"❌ Erro durante a conexão: {e}")
            
    return list(set(links_encontrados))

def salvar_lista(links):
    with open("premiere_streams.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Gerada via Proxy BR em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        
        if not links:
            f.write("# Nenhum link encontrado. Verifique se o proxy está online.\n")
        else:
            for i, link in enumerate(links, 1):
                # Adiciona o Referer necessário para abrir o link
                f.write(f"#EXTINF:-1, Premiere HD BR {i}\n")
                f.write(f"{link}|Referer=https://embedtv.best/\n\n")

if __name__ == "__main__":
    links = coletar_com_proxy()
    salvar_lista(links)
    print(f"✅ Processo finalizado. {len(links)} links salvos em premiere_streams.m3u")
