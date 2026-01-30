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
        # Resolve estados de erro do Git (rebases ou merges travados)
        subprocess.run(["git", "rebase", "--abort"], capture_output=True)
        subprocess.run(["git", "merge", "--abort"], capture_output=True)
        
        # Prepara os arquivos
        subprocess.run(["git", "add", "."], check=True)
        
        # Verifica se há algo para commitar
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        if status:
            print("✨ Mudanças detectadas. Realizando commit...")
            subprocess.run(["git", "commit", "-m", f"Update automático: {time.strftime('%H:%M:%S')}"], check=True)
            
            print("🔄 Sincronizando com o servidor (Pull)...")
            subprocess.run(["git", "pull", "origin", "main", "--no-rebase"], capture_output=True)

            print("🚀 Enviando para o repositório remoto (Push)...")
            push_result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print("✅ SUCESSO! O GitHub foi atualizado.")
            else:
                print(f"⚠️ Erro no Push: {push_result.stderr}")
        else:
            print("ℹ️ Nenhuma mudança detectada pelo Git.")
            
    except Exception as e:
        print(f"❌ Erro crítico no processo Git: {e}")

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
            
            # Fecha pop-ups de anúncios automaticamente
            page.on("popup", lambda p: p.close())
            
            # Aplica camuflagem anti-bot
            if hasattr(playwright_stealth, 'stealth_sync'):
                playwright_stealth.stealth_sync(page)
            
            link_master = {"url": None}

            def interceptar(request):
                u = request.url.lower()
                # Filtra apenas o Master Playlist, ignorando os fragmentos infinitos (mono/ts)
                if ".m3u8" in u and not any(x in u for x in ["mono", "tracks", "ts.m3u8", "chunk", "v1", "v2"]):
                    if not link_master["url"]:
                        link_master["url"] = request.url

            page.on("request", interceptar)

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)
                
                # Clique simulado no player para gerar o tráfego de vídeo
                page.mouse.click(640, 360) 
                
                # Aguarda a captura do link Master
                for _ in range(12):
                    if link_master["url"]: break
                    time.sleep(1)
                
                if link_master["url"]:
                    resultados.append({"nome": nome, "link": link_master["url"]})
                    print("✅")
                else:
                    print("❌")
                    
            except Exception:
                print("❌")
            finally:
                page.close()
                
        browser.close()
    return resultados

# --- EXECUÇÃO ---
if __name__ == "__main__":
    start_time = time.time()
    agora = time.strftime("%d/%m/%Y %H:%M:%S")
    
    print(f"🤖 Iniciando extrator às {agora}...")
    
    lista_canais = extrair_todos_canais()
    
    if lista_canais:
        print(f"📝 Gravando {NOME_ARQUIVO}...")
        with open(NOME_ARQUIVO, "w", encoding="utf-8") as f:
            # O Timestamp abaixo garante que o arquivo mude sempre, forçando o Git a atualizar
            f.write(f"# ULTIMA ATUALIZACAO: {agora}\n")
            f.write("#EXTM3U\n")
            for canal in lista_canais:
                f.write(f"#EXTINF:-1, {canal['nome']}\n")
                # Referer e User-Agent são fundamentais para rodar no VLC/IPTV
                f.write(f"{canal['link']}|Referer=https://embedtvonline.com/&User-Agent=Mozilla/5.0\n")
        
        enviar_para_github()
    else:
        print("\n⚠️ Nenhum link capturado. O GitHub não será atualizado.")
        
    print(f"\n⏱️ Processo finalizado em {int(time.time() - start_time)}s.")