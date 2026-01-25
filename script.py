from playwright.sync_api import sync_playwright
import time
from datetime import datetime

URL_ALVO = "https://www2.embedtv.best/premiere"

def coletar_fontes():
    fontes = []
    with sync_playwright() as p:
        print("🚀 Analisando estruturas de iframe...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        try:
            page.goto(URL_ALVO, wait_until="networkidle", timeout=60000)
            
            # 1. Procura por links m3u8 antes do token (tentativa de bypass)
            # 2. Captura o SRC de todos os iframes (fontes prováveis)
            iframes = page.query_selector_all('iframe')
            for iframe in iframes:
                src = iframe.get_attribute('src')
                if src and "embed" in src:
                    print(f"🎥 Fonte encontrada: {src}")
                    fontes.append(src)
            
            # Tenta capturar o tráfego também, mas filtrando a origem
            def interceptar(request):
                url = request.url
                if ".m3u8" in url and "cloudfront" not in url: # Evita o link com token do GitHub
                     fontes.append(url)
            
            page.on("request", interceptar)
            time.sleep(10)

        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            browser.close()

    return list(set(fontes))

def salvar(links):
    with open("premiere_streams.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        if not links:
            f.write("# Nenhum link de origem estatico encontrado\n")
        else:
            for i, link in enumerate(links, 1):
                f.write(f"#EXTINF:-1, Premiere Origem {i}\n{link}\n")

if __name__ == "__main__":
    links = coletar_fontes()
    salvar(links)
    print(f"✅ Processo finalizado. {len(links)} fontes salvas.")
