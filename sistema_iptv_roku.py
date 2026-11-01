from flask import Flask, jsonify, request, Response
from werkzeug.middleware.proxy_fix import ProxyFix
import socket
import itertools
import cloudscraper
import re
import os

# ============================================================
# OVERRIDE DE DNS
# O Render (e o Enzonic) usam DNS padrao que falha em resolver
# estes dominios. Forcamos IPs fixos descobertos via 1.1.1.1.
# ============================================================
DNS_OVERRIDE = {
    "embedcanaisdetv.xyz": ["104.21.50.169", "172.67.164.103"],
    "playerembcanais.com": ["172.67.158.167", "104.21.14.108"],
}

_original_getaddrinfo = socket.getaddrinfo
_counter = itertools.cycle(range(1000))

def _patched_getaddrinfo(host, port, *args, **kwargs):
    if host:
        host_lower = host.lower()
        # Match exato ou subdominio (ex: 2910.playerembcanais.com)
        for domain, ips in DNS_OVERRIDE.items():
            if host_lower == domain or host_lower.endswith("." + domain):
                host = ips[next(_counter) % len(ips)]
                break
    return _original_getaddrinfo(host, port, *args, **kwargs)

socket.getaddrinfo = _patched_getaddrinfo
# ============================================================

app = Flask(__name__)

# x_host=0 e x_prefix=0: NAO confia no X-Forwarded-Host do proxy,
# que aponta para host interno. Usa o Host real da requisicao.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=0, x_prefix=0)

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)
HEADERS_ORIGEM = {
    "Referer": "https://embedcanaisdetv.xyz",
    "Origin": "https://embedcanaisdetv.xyz"
}

CANAIS_DATABASE = {
    "premiere2": {"name": "Premiere 2", "slug": "premiere2"},
    "premiere3": {"name": "Premiere 3", "slug": "premiere3"},
    "premiere4": {"name": "Premiere 4", "slug": "premiere4"},
    "premiere5": {"name": "Premiere 5", "slug": "premiere5"},
    "premiere7": {"name": "Premiere 7", "slug": "premiere7"},
    "premiere8": {"name": "Premiere 8", "slug": "premiere8"},
    "premiereclubes": {"name": "Premiere Clubes", "slug": "premiereclubes"},
    "sportv": {"name": "Sportv", "slug": "sportv"},
    "sportv2": {"name": "Sportv 2", "slug": "sportv2"},
    "sportv3": {"name": "Sportv 3", "slug": "sportv3"},
    "tnt": {"name": "TNT", "slug": "tnt"},
    "tnt1": {"name": "TNT 1", "slug": "tnt1"},
    "tntnovelas": {"name": "TNT Novelas", "slug": "tntnovelas"},
    "tntseries": {"name": "TNT Series", "slug": "tntseries"},
    "hbo": {"name": "HBO", "slug": "hbo"},
    "hbomundi": {"name": "HBO Mundi", "slug": "hbomundi"},
    "hboplus": {"name": "HBO Plus", "slug": "hboplus"},
    "megapix": {"name": "Megapix", "slug": "megapix"},
    "paramountnetwork": {"name": "Paramount Network", "slug": "paramountnetwork"},
    "space": {"name": "Space", "slug": "space"},
    "tcaction": {"name": "Telecine Action", "slug": "tcaction"},
    "tccult": {"name": "Telecine Cult", "slug": "tccult"},
    "tcfun": {"name": "Telecine Fun", "slug": "tcfun"},
    "tcpipoca": {"name": "Telecine Pipoca", "slug": "tcpipoca"},
    "tcpremium": {"name": "Telecine Premium", "slug": "tcpremium"},
    "tctouch": {"name": "Telecine Touch", "slug": "tctouch"},
    "cinemax": {"name": "Cinemax", "slug": "cinemax"},
    "cartoonnetwork": {"name": "Cartoon Network", "slug": "cartoonnetwork"},
    "discoverykids": {"name": "Discovery Kids", "slug": "discoverykids"},
    "gloob": {"name": "Gloob", "slug": "gloob"},
    "gloobinho": {"name": "Gloobinho", "slug": "gloobinho"},
    "nickjr": {"name": "Nick Jr", "slug": "nickjr"},
    "nickelodeon": {"name": "Nickelodeon", "slug": "nickelodeon"},
    "bandnews": {"name": "Band News", "slug": "bandnews"},
    "cnnbrasil": {"name": "CNN Brasil", "slug": "cnnbrasil"},
    "globonews": {"name": "GloboNews", "slug": "globonews"},
    "jovempannews": {"name": "Jovem Pan News", "slug": "jovempannews"},
    "recordnews": {"name": "Record News", "slug": "recordnews"},
    "globodf": {"name": "Globo DF", "slug": "globodf"},
    "globoplaynovelas": {"name": "Globoplay Novelas", "slug": "globoplaynovelas"},
    "dazn": {"name": "DAZN", "slug": "dazn"},
    "disneychannel": {"name": "Disney Channel", "slug": "disneychannel"},
    "disneyjunior": {"name": "Disney Junior", "slug": "disneyjunior"},
    "disneyxd": {"name": "Disney XD", "slug": "disneyxd"},
    "espn": {"name": "ESPN", "slug": "espn"},
    "espn2": {"name": "ESPN 2", "slug": "espn2"},
    "espn3": {"name": "ESPN 3", "slug": "espn3"},
    "espn4": {"name": "ESPN 4", "slug": "espn4"},
    "espn5": {"name": "ESPN 5", "slug": "espn5"},
    "espn6": {"name": "ESPN 6", "slug": "espn6"},
    "getv": {"name": "GE TV", "slug": "getv"},
    "max": {"name": "Max", "slug": "max"},
    "max2": {"name": "Max 2", "slug": "max2"},
    "max3": {"name": "Max 3", "slug": "max3"},
    "max4": {"name": "Max 4", "slug": "max4"},
    "nsports": {"name": "N Sports", "slug": "nsports"},
    "primevideo": {"name": "Prime Video", "slug": "primevideo"},
    "appletv01": {"name": "Apple TV 01", "slug": "appletv01"},
    "appletv02": {"name": "Apple TV 02", "slug": "appletv02"},
    "appletv03": {"name": "Apple TV 03", "slug": "appletv03"},
    "appletv04": {"name": "Apple TV 04", "slug": "appletv04"},
    "appletv05": {"name": "Apple TV 05", "slug": "appletv05"},
    "bandsports": {"name": "Band Sports", "slug": "bandsports"},
}


def extrair_m3u8_do_embed(embed_url):
    """Tenta extrair o link .m3u8 do HTML do embed. Loga detalhes no stdout."""
    try:
        print(f"[EXTRAIR] Acessando: {embed_url}", flush=True)
        resposta = scraper.get(embed_url, timeout=15)
        print(f"[EXTRAIR] Status HTTP: {resposta.status_code} | Tamanho HTML: {len(resposta.text)} bytes", flush=True)

        if resposta.status_code != 200:
            print(f"[EXTRAIR] FALHA - Status nao e 200. Body (primeiros 300 chars): {resposta.text[:300]}", flush=True)
            return None

        html = resposta.text

        if "cf-browser-verification" in html or "Just a moment" in html or "Checking your browser" in html:
            print("[EXTRAIR] FALHA - Cloudflare challenge detectado (bloqueio de bot).", flush=True)
            return None

        padrao_m3u8 = r'(https?://[^\s"\',\?<>#]+\.m3u8[^\s"\',<>]*)'
        links = re.findall(padrao_m3u8, html)
        print(f"[EXTRAIR] Links .m3u8 encontrados: {len(links)}", flush=True)

        if links:
            link_final = links[0].replace('\\/', '/')
            print(f"[EXTRAIR] OK - Link: {link_final[:120]}", flush=True)
            return link_final

        print(f"[EXTRAIR] FALHA - Nenhum .m3u8 no HTML. Primeiros 500 chars: {html[:500]}", flush=True)
        return None

    except Exception as e:
        print(f"[EXTRAIR] EXCECAO: {type(e).__name__}: {e}", flush=True)
        return None


def _base_url():
    """Retorna a URL publica do app, sem barra final."""
    return request.url_root.rstrip('/')


@app.route('/api/roku/sources', methods=['GET'])
def listar_fontes():
    fontes_lista = [{"id": k, "name": v["name"]} for k, v in CANAIS_DATABASE.items()]
    return jsonify({"sources": fontes_lista})


@app.route('/api/roku/sources/<source_id>', methods=['GET'])
def detalhar_fonte(source_id):
    canal = CANAIS_DATABASE.get(source_id)
    if not canal:
        return jsonify({"error": "Nao encontrado"}), 404
    return jsonify({
        "source": {
            "id": canal["slug"],
            "name": canal["name"],
            "format": "hls",
            "url": f"{_base_url()}/resolver_video?canal={canal['slug']}"
        }
    })


@app.route('/resolver_video', methods=['GET'])
def resolver_video():
    slug = request.args.get('canal', '').strip()
    print(f"[RESOLVER] Canal solicitado: '{slug}' | Host: {request.host}", flush=True)

    if not slug:
        return "Parametro 'canal' ausente", 400

    b, q = chr(47), chr(63)
    url_completa_embed = "https:" + b + b + "embedcanaisdetv.xyz" + b + "e" + b + "index.php" + q + "canal=" + slug

    link_m3u8_real = extrair_m3u8_do_embed(url_completa_embed)

    if not link_m3u8_real:
        print(f"[RESOLVER] Retornando 'Sinal indisponivel' para '{slug}'", flush=True)
        return "Sinal indisponivel", 404

    try:
        req_m3u8 = scraper.get(link_m3u8_real, headers=HEADERS_ORIGEM, timeout=15)
        conteudo = req_m3u8.text
        print(f"[RESOLVER] Playlist M3U8 baixada. Status: {req_m3u8.status_code} | Tamanho: {len(conteudo)} bytes", flush=True)

        url_base_ts = link_m3u8_real.rsplit('/', 1)[0] + '/'
        base = _base_url()

        linhas = []
        for linha in conteudo.splitlines():
            if '.ts' in linha and not linha.startswith('http'):
                url_segmento_real = url_base_ts + linha.strip()
                linhas.append(f"{base}/ts_proxy?url={url_segmento_real}")
            elif '.ts' in linha and linha.startswith('http'):
                linhas.append(f"{base}/ts_proxy?url={linha.strip()}")
            else:
                linhas.append(linha)

        conteudo_final = "\n".join(linhas)
        return Response(conteudo_final, mimetype='application/x-mpegURL')

    except Exception as err:
        print(f"[RESOLVER] ERRO ao processar Playlist: {type(err).__name__}: {err}", flush=True)
        return "Erro Interno no Proxy", 500


@app.route('/ts_proxy', methods=['GET'])
def ts_proxy():
    """Baixa o pedaco .ts da CDN (com Referer) e repassa pra RokuTV."""
    url_ts = request.args.get('url')
    if not url_ts:
        return "URL invalida", 400

    try:
        resposta_ts = scraper.get(url_ts, headers=HEADERS_ORIGEM, stream=True, timeout=20)

        def gerar_stream():
            for chunk in resposta_ts.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        headers_resposta = {
            'Content-Type': 'video/MP2T',
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*',
        }
        return Response(gerar_stream(), headers=headers_resposta, status=resposta_ts.status_code)

    except Exception as ts_err:
        print(f"[TS_PROXY] ERRO: {type(ts_err).__name__}: {ts_err}", flush=True)
        return "Erro de transmissao", 502


@app.route('/', methods=['GET'])
def healthcheck():
    return jsonify({
        "status": "ok",
        "app": "Nexoratv-Roku backend",
        "endpoints": [
            "/api/roku/sources",
            "/api/roku/sources/<id>",
            "/resolver_video?canal=<slug>",
            "/ts_proxy?url=<url_ts>"
        ]
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'

    # Dentro do Enzonic (tem $SERVER_PORT) -> sobe Gunicorn internamente
    if os.environ.get('SERVER_PORT'):
        import sys
        from gunicorn.app.wsgiapp import run as gunicorn_run
        sys.argv = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '1',
            '--threads', '6',
            '--timeout', '120',
            '--capture-output',
            '--access-logfile', '-',
            '--error-logfile', '-',
            'sistema_iptv_roku:app'
        ]
        gunicorn_run()
    else:
        # Local (seu PC) -> Flask dev
        app.run(host='0.0.0.0', port=port, debug=debug)