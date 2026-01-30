import time
import subprocess
from playwright.sync_api import sync_playwright
import playwright_stealth

# --- CONFIGURAÇÕES ---
CANAIS = {
    "Premiere 1": "https://embedtvonline.com/globorj/",
}

NOME_ARQUIVO = "bielas.css"

# --- FUNÇÃO DE SINCRONIZAÇÃO ---
def enviar_para_github():
    try:
        print(f"\n📤 Sincronizando {NOME_ARQUIVO} com o GitHub...")
        subprocess.run(["git", "rebase", "--abort"], capture_output=True)
        subprocess.run(["git", "add", "."], check=True)
        
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        if status:
            print("✨ Mudanças detectadas. Realizando commit...")
            subprocess.run(["git", "commit", "-m", "System update: Master Playlist Fixed"], check=True)
            print("🔄 Sincronizando com o servidor...")
            subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=True)
            print("🚀 Enviando para o repositório remoto...")
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("✅ SUCESSO! Repositório atualizado.")
        else:
            print("ℹ️ Nenhuma mudança nova para atualizar.")
    except Exception as e:
        print(f"❌ Erro no GitHub: {e}")

# --- FUNÇÃO DE CAPTURA ---
def extrair_todos_canais():
    resultados = []
    
    with sync_playwright() as p:
        # Usamos headless=True para rodar no servidor, mas headless=False ajuda a debugar localmente
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        for nome, url in CANAIS.items():
            print(f"🚀 Verificando: {nome}...", end=" ", flush=True)
            page = context.new_page()
            
            # Camuflagem anti-bot
            if hasattr(playwright_stealth, 'stealth_sync'):
                playwright_stealth.stealth_sync(page)
            elif hasattr(playwright_stealth, 'stealth_page_sync'):
                playwright_stealth.stealth_page_sync(page)
            
            links_encontrados = []

            def interceptar(request):
                u = request.url.lower()
                # Captura m3u8 filtrando segmentos irrelevantes (.ts)
                if ".m3u8" in u and "chunk" not in u:
                    # Lista de prioridade: preferimos links que NÃO tenham 'index', 'mono' ou 'tracks'
                    lixo = ["mono", "tracks", "v1", "v2", "ts.m3u8"]
                    if not any(x in u for x in lixo):
                        links_encontrados.append(request.url)

            page.on("request", interceptar)

            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Interação agressiva para disparar o stream
                time.sleep(5)
                page.mouse.click(640, 360) # Clique no centro (Play)
                time.sleep(2)
                page.mouse.click(640, 360) # Segundo clique caso o primeiro abra um pop-up
                
                # Espera o link aparecer
                for _ in range(10):
                    if links_encontrados: break
                    time.sleep(1)
                
                if links_encontrados:
                    # Seleciona o link mais provável de ser o MASTER (geralmente não contém 'index')
                    master = [l for l in links_encontrados if "index" not in l.lower()]
                    link_final = master[0] if master else links_encontrados[0]
                    
                    resultados.append({"nome": nome, "link": link_final})
                    print("✅")
                else:
                    print("❌ (Sem links)")
                    
            except Exception:
                print("❌ (Erro)")
            finally:
                page.close()
                
        browser.close()
    return resultados

# --- BLOCO PRINCIPAL ---
if __name__ == "__main__":
    start_time = time.time()
    print("🤖 Iniciando o extrator...")
    
    lista_final = extrair_todos_canais()
    
    if lista_final:
        with open(NOME_ARQUIVO, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for canal in lista_final:
                f.write(f"#EXTINF:-1, {canal['nome']}\n")
                # Referer Ajustado: usamos o domínio base do embed para passar pelo bloqueio
                f.write(f"{canal['link']}|Referer=https://embedtvonline.com/&User-Agent=Mozilla/5.0\n")
        enviar_para_github()
    else:
        print("\n⚠️ Falha crítica: Nenhum link mestre capturado.")
        
    print(f"\n⏱️ Concluído em {int(time.time() - start_time)}s.")