from flask import Flask, jsonify, request, Response
import cloudscraper
import re

app = Flask(__name__)

scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
HEADERS_ORIGEM = {"Referer": "https://embedcanaisdetv.xyz/", "Origin": "https://embedcanaisdetv.xyz"}

CANAIS_DATABASE = {
    # Esportes
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
    "dazn": {"name": "Dazn", "slug": "dazn"},
    "espn": {"name": "ESPN", "slug": "espn"},
    "espn2": {"name": "ESPN 2", "slug": "espn2"},
    "espn3": {"name": "ESPN 3", "slug": "espn3"},
    "espn4": {"name": "ESPN 4", "slug": "espn4"},
    "espn5": {"name": "ESPN 5", "slug": "espn5"},
    "getv": {"name": "GE TV", "slug": "getv"},
    "nsports": {"name": "N Sports", "slug": "nsports"},
    "nossofutebol": {"name": "Nosso Futebol", "slug": "nossofutebol"},
    "bandsports": {"name": "Band Sports", "slug": "bandsports"},

    # Filmes, Séries e Streaming
    "tntnovelas": {"name": "TNT Novelas", "slug": "tntnovelas"},
    "tntseries": {"name": "TNT Séries", "slug": "tntseries"},
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
    "max": {"name": "Max", "slug": "max"},
    "max02": {"name": "Max 2", "slug": "max02"},
    "max03": {"name": "Max 3", "slug": "max03"},
    "max04": {"name": "Max 4", "slug": "max04"},
    "max05": {"name": "Max 5", "slug": "max05"},
    "amazonprimevideo": {"name": "Prime Video", "slug": "amazonprimevideo"},
    "amazonprimevideo02": {"name": "Prime Video 2", "slug": "amazonprimevideo02"},
    "amazonprimevideo03": {"name": "Prime Video 3", "slug": "amazonprimevideo03"},
    "appletv01": {"name": "Apple TV 1", "slug": "appletv01"},
    "appletv02": {"name": "Apple TV 2", "slug": "appletv02"},
    "appletv03": {"name": "Apple TV 3", "slug": "appletv03"},
    "appletv04": {"name": "Apple TV 4", "slug": "appletv04"},
    "appletv05": {"name": "Apple TV 5", "slug": "appletv05"},

    # Infantis e Animações
    "cartoonnetwork": {"name": "Cartoon Network", "slug": "cartoonnetwork"},
    "discoverykids": {"name": "Discovery Kids", "slug": "discoverykids"},
    "gloob": {"name": "Gloob", "slug": "gloob"},
    "gloobinho": {"name": "Gloobinho", "slug": "gloobinho"},
    "nickjr": {"name": "Nick Jr", "slug": "nickjr"},
    "nickelodeon": {"name": "Nickelodeon", "slug": "nickelodeon"},
    "disneyplus": {"name": "Disney+", "slug": "disneyplus"},
    "disneyplus02": {"name": "Disney 2", "slug": "disneyplus02"},
    "disneyplus03": {"name": "Disney 3", "slug": "disneyplus03"},
    "disneyplus04": {"name": "Disney 4", "slug": "disneyplus04"},
    "disneyplus05": {"name": "Disney 5", "slug": "disneyplus05"},
    "disneyplus07": {"name": "Disney +7", "slug": "disneyplus07"},
    "disneyplus08": {"name": "Disney +8", "slug": "disneyplus08"},
    "disneyplus09": {"name": "Disney +9", "slug": "disneyplus09"},

    # Notícias e Variedades
    "bandnews": {"name": "Band News", "slug": "bandnews"},
    "cnnbrasil": {"name": "CNN Brasil", "slug": "cnnbrasil"},
    "globonews": {"name": "GloboNews", "slug": "globonews"},
    "jovempannews": {"name": "Jovem Pan News", "slug": "jovempannews"},
    "recordnews": {"name": "Record News", "slug": "recordnews"},
    "globodf": {"name": "Globo DF", "slug": "globodf"},
    "globoplaynovelas": {"name": "Globoplay Novelas", "slug": "globoplaynovelas"}
}

def extrair_m3u8_do_embed(embed_url):
    try:
        resposta = scraper.get(embed_url, timeout=10)
        html = resposta.text
        padrao_m3u8 = r'(https?://[^\s"\',\?<>#]+\.m3u8[^\s"\',<>]*)'
        links = re.findall(padrao_m3u8, html)
        if links:
            return links[0].replace('\\/', '/')
    except Exception as e:
        print(f"Erro Cloudflare no Scraper: {e}")
    return None

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
            "url": f"{request.url_root}resolver_video?canal={canal['slug']}"
        }
    })

@app.route('/resolver_video', methods=['GET'])
def resolver_video():
    slug = request.args.get('canal', '')
    canal_identificado = slug.split("canal=")[-1].split("/")[-1].replace('"', '').replace("'", "").strip()
    
    b, q = chr(47), chr(63)
    url_completa_embed = "https:" + b + b + "embedcanaisdetv.xyz" + b + "e" + b + "index.php" + q + "canal=" + canal_identificado
    
    link_m3u8_real = extrair_m3u8_do_embed(url_completa_embed)
    
    if link_m3u8_real:
        try:
            req_m3u8 = scraper.get(link_m3u8_real, headers=HEADERS_ORIGEM, timeout=10)
            conteudo = req_m3u8.text
            url_base_ts = link_m3u8_real.rsplit('/', 1)[0] + '/'
            
            linhas = []
            for linha in conteudo.splitlines():
                if '.ts' in linha and not linha.startswith('http'):
                    url_segmento_real = url_base_ts + linha
                    linhas.append(f"{request.url_root}ts_proxy?url={url_segmento_real}")
                elif '.ts' in linha and linha.startswith('http'):
                    linhas.append(f"{request.url_root}ts_proxy?url={linha}")
                else:
                    linhas.append(linha)
            
            conteudo_final = "\n".join(linhas)
            return Response(conteudo_final, mimetype='application/x-mpegURL')
            
        except Exception as err:
            print(f"Erro ao processar Playlist M3U8: {err}")
            return "Erro Interno no Proxy", 500
    return "Sinal indisponivel", 404

@app.route('/ts_proxy', methods=['GET'])
def ts_proxy():
    url_ts = request.args.get('url')
    if not url_ts:
        return "URL invalida", 400
        
    try:
        resposta_ts = scraper.get(url_ts, headers=HEADERS_ORIGEM, stream=True, timeout=15)
        def gerar_stream():
            for chunk in resposta_ts.iter_content(chunk_size=4096):
                yield chunk
        return Response(gerar_stream(), content_type='video/MP2T')
    except Exception as ts_err:
        print(f"Erro ao tunelar segmento TS: {ts_err}")
        return "Erro de transmissao", 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
