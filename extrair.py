import time
import subprocess
from playwright.sync_api import sync_playwright
import playwright_stealth  # Importação do módulo completo

# --- CONFIGURAÇÕES ---
CANAIS = {
    "Premiere 1": "https://embedtvonline.com/globorj/",
}

NOME_ARQUIVO = "bielas.css"

# --- FUNÇÃO DE SINCRONIZAÇÃO ---
def enviar_para_github():
    try:
        print(f"\n📤 Sincronizando {NOME_ARQUIVO} com o GitHub...")
        subprocess.run(["git", "add", "."], check=True)
        
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        if status:
            print("✨ Mudanças detectadas. Realizando commit...")
            subprocess.run(["git", "commit", "-m", "System update: links atualizados"], check=True)
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
        # Lançamos o navegador
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        for nome, url in CANAIS.items():
            print(f"🚀 Verificando: {nome}...", end=" ", flush=True)
            page = context.new_page()
            
            # --- SOLUÇÃO PARA O ERRO DE IMPORTAÇÃO ---
            # Tentamos os dois nomes possíveis que a biblioteca costuma usar
            if hasattr(playwright_stealth, 'stealth_sync'):
                playwright_stealth.stealth_sync(page)
            elif hasattr(playwright_stealth, 'stealth_page_sync'):
                playwright_stealth.stealth_page_sync(page)
            
            link_encontrado = {"url": None}

            def interceptar(request):
                u = request.url.lower()
                if ".m3u8" in u and "chunk" not in u:
                    link_encontrado["url"] = request.url

            page.on("request", interceptar)

            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Aguarda o player disparar o link
                for i in range(15):
                    if link_encontrado["url"]: break
                    if i == 5: page.mouse.click(640, 360) # Clique no player
                    time.sleep(1)
                
                if link_encontrado["url"]:
                    resultados.append({"nome": nome, "link": link_encontrado["url"]})
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
                f.write(f"#EXTINF:-1, {canal['nome']}\n{canal['link']}\n")
        enviar_para_github()
    else:
        print("\n⚠️ Falha crítica: Nenhum link capturado.")
        
    print(f"\n⏱️ Concluído em {int(time.time() - start_time)}s.")