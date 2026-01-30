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
        # Limpa rebases travados antes de começar
        subprocess.run(["git", "rebase", "--abort"], capture_output=True)
        subprocess.run(["git", "add", "."], check=True)
        
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        if status:
            print("✨ Mudanças detectadas. Realizando commit...")
            subprocess.run(["git", "commit", "-m", "System update: Master link atualizado"], check=True)
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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        for nome, url in CANAIS.items():
            print(f"🚀 Verificando: {nome}...", end=" ", flush=True)
            page = context.new_page()
            
            # Aplica o stealth (camuflagem anti-bot)
            if hasattr(playwright_stealth, 'stealth_sync'):
                playwright_stealth.stealth_sync(page)
            elif hasattr(playwright_stealth, 'stealth_page_sync'):
                playwright_stealth.stealth_page_sync(page)
            
            links_m3u8 = []

            def interceptar(request):
                u = request.url.lower()
                # FILTRO MASTER: Ignora lixo e foca no manifesto principal
                if ".m3u8" in u:
                    lixo = ["chunk", "mono", "tracks", "v1", "v2", "index-", "ts.m3u8"]
                    if not any(x in u for x in lixo):
                        links_m3u8.append(request.url)

            page.on("request", interceptar)

            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Aguarda até 15 segundos pelo link master
                for i in range(15):
                    if links_m3u8: break
                    if i == 5: page.mouse.click(640, 360) # Clique simulado
                    time.sleep(1)
                
                if links_m3u8:
                    # Seleciona o link que tem maior probabilidade de ser o Master (geralmente o mais curto)
                    master_link = min(links_m3u8, key=len)
                    resultados.append({"nome": nome, "link": master_link})
                    print("✅")
                else:
                    print("❌")
                    
            except Exception:
                print("❌")
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
                # Inclui o Referer para que o player de IPTV consiga abrir o vídeo
                f.write(f"{canal['link']}|Referer=https://embedtvonline.com/&User-Agent=Mozilla/5.0\n")
        enviar_para_github()
    else:
        print("\n⚠️ Falha crítica: Nenhum link mestre capturado.")
        
    print(f"\n⏱️ Concluído em {int(time.time() - start_time)}s.")