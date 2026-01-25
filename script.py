from playwright.sync_api import sync_playwright
import re
import time

def coletar_com_navegador():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🌐 Abrindo o site com navegador real...")
        
        # Tenta carregar a página
        page.goto("https://embedtv.best", wait_until="networkidle", timeout=60000)
        
        # Espera um pouco para o JavaScript agir
        time.sleep(10)
        
        # Pega todo o conteúdo gerado após os scripts rodarem
        html = page.content()
        browser.close()
        
        # Busca links m3u8 no conteúdo final
        links = re.findall(r'https?://[^\s"\'<> ]+\.m3u8[^\s"\'<> ]*', html)
        return sorted(list(set(links)))

def salvar(links):
    with open("lista_streams.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        if not links:
            f.write("# Nenhum link encontrado - Site pode exigir interação humana\n")
        for i, link in enumerate(links, 1):
            f.write(f"#EXTINF:-1, Canal {i}\n{link}\n")

if __name__ == "__main__":
    links = coletar_com_navegador()
    salvar(links)
    print(f"✅ Fim! Encontrados {len(links)} links.")
