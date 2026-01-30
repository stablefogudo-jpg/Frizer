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
            subprocess.run(["git", "commit", "-m", "System update: Master Link Fixed"], check=True)
            subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("✅ SUCESSO! Repositório atualizado.")
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
            
            # Fecha pop-ups automáticos
            page.on("popup", lambda p: p.close())
            
            # USO DIRETO DO STEALTH (Evita o erro de ImportError)
            try:
                playwright_stealth.stealth_sync(page)
            except Exception:
                pass # Se falhar, continua sem stealth para não travar o código
            
            link_master = {"url": None}

            def interceptar(request):
                u = request.url.lower()
                # Filtro para ignorar a lista infinita da sua imagem (mono, ts, chunk)
                if ".m3u8" in u and not any(x in u for x in ["mono", "tracks", "ts.m3u8", "chunk", "v1", "v2"]):
                    if not link_master["url"]:
                        link_master["url"] = request.url

            page.on("request", interceptar)

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)
                
                # Clique para disparar o player
                page.mouse.click(640, 360) 
                
                # Espera o Master Playlist aparecer (ignora os repetidos)
                for _ in range(12):
                    if link_master["url"]: break
                    time.sleep(1)
                
                if link_master["url"]:
                    resultados.append({"nome": nome, "link": link_master["url"]})
                    print("✅")
                else:
                    print("❌ (Master não capturado)")
                    
            except Exception:
                print("❌ (Erro na página)")
            finally:
                page.close()
                
        browser.close()
    return resultados

if __name__ == "__main__":
    print("🤖 Iniciando o extrator...")
    lista_final = extrair_todos_canais()
    
    if lista_final:
        with open(NOME_ARQUIVO, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for canal in lista_final:
                f.write(f"#EXTINF:-1, {canal['nome']}\n")
                # Referer essencial para o link não dar erro 403
                f.write(f"{canal['link']}|Referer=https://embedtvonline.com/&User-Agent=Mozilla/5.0\n")
        enviar_para_github()
    else:
        print("\n⚠️ Falha: Nenhum link mestre foi filtrado.")