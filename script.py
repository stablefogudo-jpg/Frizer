from playwright.sync_api import sync_playwright
import re
import time
from urllib.parse import urljoin
import requests
from datetime import datetime

URL_ALVO = "https://www2.embedtv.best/premiere"

def coletar_links_playwright():
    links_encontrados = []
    with sync_playwright() as p:
        print("🚀 Iniciando navegador...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        def interceptar_m3u8(route):
            url = route.request.url
            if '.m3u8' in url.lower() and 'chunklist' not in url.lower():
                if url not in links_encontrados:
                    print(f"🔗 Capturado: {url[:60]}...")
                    links_encontrados.append(url)
            route.continue_()

        page.route("**/*.m3u8*", interceptar_m3u8)

        try:
            print(f"🌐 Navegando para: {URL_ALVO}")
            page.goto(URL_ALVO, wait_until="domcontentloaded", timeout=60000)
            time.sleep(10)
            page.mouse.click(400, 300) # Clique para tentar ativar o player
            print("⏳ Aguardando tráfego (15s)...")
            time.sleep(15)
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            browser.close()
    return sorted(list(set(links_encontrados)))

def salvar_lista_completa(links):
    # Salva o arquivo principal
    with open("premiere_streams.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n# Playlist Premiere\n")
        f.write(f"# Gerada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        if not links:
            f.write("# Nenhum link encontrado nesta execucao\n")
        else:
            for i, link in enumerate(links, 1):
                f.write(f"#EXTINF:-1, Premiere HD {i}\n{link}\n")
    
    # Salva o arquivo TXT (importante para o log)
    with open("links_simples.txt", "w", encoding="utf-8") as f:
        for link in links:
            f.write(f"{link}\n")

if __name__ == "__main__":
    print("🎬 INICIANDO CAPTURA...")
    links = coletar_links_playwright()
    salvar_lista_completa(links)
    print(f"✅ Finalizado! Encontrados {len(links)} links.")
