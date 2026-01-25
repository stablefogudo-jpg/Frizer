from playwright.sync_api import sync_playwright
import re
import time

URL_ALVO = "https://www2.embedtv.best/premiere"

def coletar():
    links_encontrados = []
    with sync_playwright() as p:
        print("🚀 Iniciando navegador...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # Monitora o tráfego de rede para pegar o link m3u8 escondido
        def handle_route(route):
            url = route.request.url
            if ".m3u8" in url and "chunklist" not in url:
                links_encontrados.append(url)
            route.continue_()

        page.route("**/*", handle_route)

        try:
            print(f"📡 Acessando: {URL_ALVO}")
            page.goto(URL_ALVO, wait_until="networkidle", timeout=60000)
            
            # Espera o player carregar e tenta clicar no play se houver
            time.sleep(10)
            print("🎬 Tentando disparar o player...")
            page.mouse.click(500, 300) # Clique no centro da tela
            
            time.sleep(10) # Aguarda o link ser gerado no tráfego
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            browser.close()

    return sorted(list(set(links_encontrados)))

def salvar(links):
    with open("lista_streams.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        if not links:
            f.write("# Nenhum link encontrado nesta execucao\n")
        else:
            for i, link in enumerate(links, 1):
                f.write(f"#EXTINF:-1, Premiere HD {i}\n{link}\n")

if __name__ == "__main__":
    links = coletar()
    salvar(links)
    print(f"✅ Finalizado! Encontrados: {len(links)}")
