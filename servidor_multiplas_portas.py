import socket
import http.server
import socketserver
import threading
import os

# ==== CONFIGURE AQUI: cada porta abre um arquivo diferente ====
PORTAS_ARQUIVOS = {
    "8000": "index.html",
}
# =================================================================


def obter_ip_local():
    """Descobre o IP local da máquina na rede."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def criar_handler(arquivo):
    """Cria uma classe de handler que sempre serve o mesmo arquivo, não importa o caminho pedido."""

    class HandlerArquivoUnico(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            # Redireciona qualquer requisição para o arquivo configurado
            self.path = "/" + arquivo
            return super().do_GET()

        def log_message(self, format, *args):
            # Log mais limpo mostrando qual arquivo está sendo servido
            print(f"[{arquivo}] {self.address_string()} - {format % args}")

    return HandlerArquivoUnico


def subir_servidor(porta, arquivo):
    if not os.path.isfile(arquivo):
        print(f"[AVISO] Arquivo '{arquivo}' não encontrado na pasta atual (porta {porta} vai falhar ao abrir).")

    handler = criar_handler(arquivo)
    try:
        with socketserver.TCPServer(("0.0.0.0", int(porta)), handler) as httpd:
            print(f"[OK] Porta {porta} servindo o arquivo: {arquivo}")
            httpd.serve_forever()
    except OSError as e:
        print(f"[ERRO] Não consegui abrir a porta {porta}: {e}")


if __name__ == "__main__":
    ip = obter_ip_local()

    print("=" * 60)
    print(f"IP da máquina na rede: {ip}")
    print("Acesse de qualquer dispositivo na mesma rede com:")
    for porta, arquivo in PORTAS_ARQUIVOS.items():
        print(f"  http://{ip}:{porta}  ->  {arquivo}")
    print("Ou localmente com:")
    for porta, arquivo in PORTAS_ARQUIVOS.items():
        print(f"  http://localhost:{porta}  ->  {arquivo}")
    print("=" * 60)
    print("Pressione CTRL+C para encerrar.\n")

    threads = []
    for porta, arquivo in PORTAS_ARQUIVOS.items():
        t = threading.Thread(target=subir_servidor, args=(porta, arquivo), daemon=True)
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nEncerrando servidores...")
