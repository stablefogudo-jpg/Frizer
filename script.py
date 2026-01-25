from playwright.sync_api import sync_playwright
import re
import time

def coletar_com_navegador():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🌐 Abrindo o site com navegador real...")
        
        # Tenta carregar a páginafrom playwright.sync_api import sync_playwright
import re
import time

# Focando na URL que você passou
URL_ALVO = "https://www2.embedtv.best/premiere"

def coletar_link_especifico():
    with sync_playwright() as p:
        # Abre o navegador
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        links_encontrados = []

        try:
            print(f"🌐 Acessando Premiere: {URL_ALVO}")
            page.goto(URL_ALVO, wait_until="networkidle", timeout=60000)
            
            # 1. Tenta clicar no botão de Play se ele aparecer (comum em players bloqueados)
            try:
                # Procura por botões de play comuns
                page.click("button.vjs-big-play-button", timeout=5000)
                print("Ads/Play clicado!")
            except:
                pass

            # 2. Espera 15 segundos para o vídeo começar e o link .m3u8 ser gerado no código
            time.sleep(15)
            
            # 3. Analisa o HTML e os scripts carregados
            html_content = page.content()
            
            # Procura por links m3u8 (o link real do Premiere)
            matches = re.findall(r'https?://[^\s"\'<> ]+\.m3u8[^\s"\'<> ]*', html_content)
            
            for link in matches:
                # Filtra links inúteis (como imagens ou chunks pequenos)
                if ".m3u8" in link and "chunklist" not in link:
                    links_encontrados.append(link)
                    
        except Exception as e:
            print(f"❌ Erro ao acessar: {e}")
        finally:
            browser.close()
            
        return sorted(list(set(links_encontrados)))

def salvar_m3u(links):
    with open("lista_streams.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        if not links:
            f.write("# Nenhum link encontrado. O site pode estar usando tokens temporarios.\n")
        else:
            for i, link in enumerate(links, 1):
                f.write(f"#EXTINF:-1, Premiere HD {i}\n{link}\n")

if __name__ == "__main__":
    resultado = coletar_link_especifico()
    salvar_m3u(resultado)
    print(f"✅ Processo concluído. Encontrados: {len(resultado)}")
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
