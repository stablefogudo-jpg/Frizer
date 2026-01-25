import time
import json
from playwright.sync_api import sync_playwright

# URL do canal
BASE_URL = "https://www2.embedtv.best/premiere"

def extrair_no_meu_ip():
    links_encontrados = []
    
    with sync_playwright() as p:
        # headless=False para você ver o navegador trabalhando
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # Captura os links .m3u8 que passarem pela rede
        def monitorar_rede(route):
            url = route.request.url
            if ".m3u8" in url.lower():
                print(f"✅ Link encontrado: {url}")
                links_encontrados.append(url)
            route.continue_()

        page.route("**/*", monitorar_rede)

        try:
            print(f"Abrindo: {BASE_URL}")
            page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
            
            # Clique para iniciar o player (ajuste as coordenadas se necessário)
            time.sleep(5)
            page.mouse.click(400, 300) 
            
            print("Capturando tráfego por 30 segundos...")
            time.sleep(30)
            
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        finally:
            browser.close()
            
    return list(set(links_encontrados))

if __name__ == "__main__":
    links = extrair_no_meu_ip()
    if links:
        with open("meus_links.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for link in links:
                f.write(f"#EXTINF:-1, Canal Local\n{link}\n")
        print(f"\n🔥 SUCESSO! {len(links)} link(s) salvo(s) em 'meus_links.m3u'")
    else:
        print("\n❌ Nenhum link foi capturado. Verifique se o vídeo chegou a carregar.")