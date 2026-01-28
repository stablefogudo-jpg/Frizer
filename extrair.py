import time
import subprocess
from playwright.sync_api import sync_playwright

# DICIONÁRIO COMPLETO DE CANAIS
CANAIS = {
    "Premiere 1": "https://www2.embedtv.best/premiere",
    "Premiere 2": "https://www2.embedtv.best/premiere2",
    "Discovery ID": "https://www2.embedtv.best/discoveryid",
    "Premiere 4": "https://www2.embedtv.best/premiere4",
    "Premiere 5": "https://www2.embedtv.best/premiere5",
    "Sportv": "https://www2.embedtv.best/sportv",
    "Cartoon Network": "https://www2.embedtv.best/cartoonnetwork",
    "Discovery Channel": "https://www2.embedtv.best/discoverychannel",
    "History": "https://www2.embedtv.best/history",
    "History 2": "https://www2.embedtv.best/history2",
    "Globo RJ": "https://www2.embedtv.best/globorj",
    "Nickelodeon": "https://www2.embedtv.best/nickelodeon",
    "Record": "https://www2.embedtv.best/record",
    "SBT": "https://www2.embedtv.best/sbt",
    "Animal Planet": "https://www2.embedtv.best/animalplanet",
    "Todo Mundo Odeia o Chris 24h": "https://www2.embedtv.best/24h_odeiachris",
    "Simpsons 24h": "https://www2.embedtv.best/24h_simpsons"
}

NOME_ARQUIVO = "bielas.css"

def enviar_para_github():
    try:
        print(f"\n📤 Sincronizando {NOME_ARQUIVO} com o GitHub...")
        
        # 1. Prepara as mudanças locais
        subprocess.run(["git", "add", "."], check=True)
        
        # 2. Verifica se há algo novo para commitar
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        if status:
            print("✨ Mudanças detectadas. Realizando commit...")
            subprocess.run(["git", "commit", "-m", "System update: links atualizados"], check=True)
        else:
            print("ℹ️ Nenhuma mudança nova para commitar.")

        # 3. SINCRONIZAÇÃO (Puxa as mudanças do GitHub para evitar erro de 'rejected')
        print("🔄 Sincronizando com o servidor (git pull --rebase)...")
        subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=True)

        # 4. Envia os dados para o repositório
        print("🚀 Enviando para o repositório remoto...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ SUCESSO! Repositório atualizado e sincronizado.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro de comando Git: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado no GitHub: {e}")

def extrair_todos_canais():
    resultados = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        
        for nome, url in CANAIS.items():
            print(f"🚀 Verificando: {nome}...", end=" ", flush=True)
            page = context.new_page()
            link_encontrado = {"url": None}

            # Interceptador de tráfego para achar o arquivo de vídeo
            page.route("**/*", lambda route: (
                link_encontrado.update({"url": route.request.url}) 
                if ".m3u8" in route.request.url.lower() else None, 
                route.continue_()
            ))

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Aguarda o link ser disparado (clique simulado se demorar)
                for _ in range(15): 
                    if link_encontrado["url"]: break
                    if _ == 5: page.mouse.click(400, 300)
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

if __name__ == "__main__":
    start_time = time.time()
    
    print("🤖 Iniciando o extrator no seu IP...")
    lista_final = extrair_todos_canais()
    
    if lista_final:
        # Gera o arquivo M3U (com extensão .css para camuflar)
        with open(NOME_ARQUIVO, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for canal in lista_final:
                f.write(f"#EXTINF:-1, {canal['nome']}\n{canal['link']}\n")
        
        enviar_para_github()
    else:
        print("\n⚠️ Falha crítica: Nenhum link capturado. Abortando upload.")
        
    print(f"\n⏱️ Processo concluído em {int(time.time() - start_time)}s.")