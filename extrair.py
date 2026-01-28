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

NOME_ARQUIVO = "bielas.css" # Nome camuflado do arquivo

def enviar_para_github():
    try:
        print(f"\n📤 Sincronizando {NOME_ARQUIVO} com o GitHub...")
        
        # 1. Adiciona todos os arquivos alterados
        subprocess.run(["git", "add", "."], check=True)
        
        # 2. Verifica se há algo de fato para commitar (evita erro de status 1)
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        
        if status:
            print("✨ Mudanças detectadas. Realizando commit...")
            subprocess.run(["git", "commit", "-m", "System update: links atualizados"], check=True)
        else:
            print("ℹ️ Nenhuma mudança nova para commitar.")

        # 3. Sempre tenta dar o Push (limpa commits pendentes)
        print("🚀 Enviando para o repositório remoto...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ SUCESSO! Repositório sincronizado.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro de comando Git: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado no GitHub: {e}")

def extrair_todos_canais():
    resultados = []
    with sync_playwright() as p:
        # Launch com chromium
        browser = p.chromium.launch(headless=True)
        # Criamos um único contexto para a sessão inteira
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        
        for nome, url in CANAIS.items():
            print(f"🚀 Verificando: {nome}...", end=" ", flush=True)
            page = context.new_page()
            link_encontrado = {"url": None}

            # Interceptador de rede para capturar o .m3u8
            page.route("**/*", lambda route: (
                link_encontrado.update({"url": route.request.url}) 
                if ".m3u8" in route.request.url.lower() else None, 
                route.continue_()
            ))

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Loop de espera pelo link (máximo 15 segundos)
                for _ in range(15): 
                    if link_encontrado["url"]: break
                    # Simula clique no player para disparar o carregamento se necessário
                    if _ == 5: page.mouse.click(400, 300)
                    time.sleep(1)
                
                if link_encontrado["url"]:
                    resultados.append({"nome": nome, "link": link_encontrado["url"]})
                    print("✅")
                else: 
                    print("❌ (Link não capturado)")
            except Exception: 
                print("❌ (Timeout/Erro)")
            finally: 
                page.close() # Fecha apenas a aba para não sobrecarregar
                
        browser.close()
    return resultados

if __name__ == "__main__":
    start_time = time.time()
    
    print("🤖 Iniciando o extrator no seu IP...")
    lista_final = extrair_todos_canais()
    
    if lista_final:
        # Gravação do arquivo formatado
        with open(NOME_ARQUIVO, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for canal in lista_final:
                f.write(f"#EXTINF:-1, {canal['nome']}\n{canal['link']}\n")
        
        enviar_para_github()
    else:
        print("\n⚠️ Nenhum link foi extraído. O envio ao GitHub foi cancelado.")
        
    print(f"\n⏱️ Processo concluído em {int(time.time() - start_time)}s.")