#!/usr/bin/env python3
"""
Corte Pronto - editor de cortes de live.

Comandos:
  transcrever  VIDEO                 -> cria VIDEO.transcricao.json (fala com o tempo de cada palavra)
  listar       TRANSCRICAO.json      -> mostra a fala com minutagem, para escolher os momentos
  cortar       VIDEO --inicio --fim  -> gera o corte em pe (1080x1920) com legenda e zoom

Exemplos:
  python cortepronto.py transcrever live.mp4
  python cortepronto.py listar live.mp4.transcricao.json
  python cortepronto.py cortar live.mp4 --inicio 01:42:10 --fim 01:42:48 --saida corte01.mp4 \
      --transcricao live.mp4.transcricao.json --estilo ../estilos/viral.json --zooms 01:42:15,01:42:31 \
      --titulo "NINGUEM ESPERAVA ISSO"

Requisitos: Python 3.9+, ffmpeg instalado no computador e, para transcrever: pip install faster-whisper
"""
import argparse, json, os, shutil, subprocess, sys, tempfile

ESTILO_PADRAO = {
    "fonte": "Arial Black",
    "tamanho": 78,
    "cor_texto": "#FFFFFF",
    "cor_destaque": "#FFE14D",
    "cor_contorno": "#000000",
    "contorno": 6,
    "sombra": 2,
    "maiusculas": True,
    "palavras_por_bloco": 3,
    "posicao_legenda": 0.30,
    "enquadramento": "borrado",
    "zoom": 0.12,
    "duracao_zoom": 1.2,
    "titulo_cor": "#FFFFFF",
    "titulo_fundo": "#FF6A3D",
    "titulo_segundos": 3.0
}


def tempo(s):
    """Aceita 95.5, 01:35.5 ou 00:01:35.5 e devolve segundos."""
    if s is None:
        return None
    s = str(s).strip().replace(",", ".")
    partes = [float(p) for p in s.split(":")]
    total = 0.0
    for p in partes:
        total = total * 60 + p
    return total


def fmt(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:05.2f}" if h else f"{m:02d}:{s:05.2f}"


def ass_tempo(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_cor(hexa, alpha=0):
    hexa = hexa.lstrip("#")
    r, g, b = hexa[0:2], hexa[2:4], hexa[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def precisa(prog):
    if not shutil.which(prog):
        sys.exit(f"[erro] '{prog}' nao encontrado. Instale o ffmpeg e tente de novo (veja o guia do bonus).")


# ---------------------------------------------------------------- transcrever
def cmd_transcrever(a):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("[erro] Falta o transcritor. Rode: pip install faster-whisper")
    print(f"Transcrevendo {a.video} (modelo {a.modelo}). Isso pode levar alguns minutos...")
    modelo = WhisperModel(a.modelo, device="auto", compute_type="auto")
    segs, info = modelo.transcribe(a.video, language=a.idioma, word_timestamps=True, vad_filter=True)
    saida = {"video": os.path.abspath(a.video), "idioma": info.language, "segmentos": []}
    for s in segs:
        palavras = [{"inicio": round(w.start, 2), "fim": round(w.end, 2), "palavra": w.word.strip()} for w in (s.words or [])]
        saida["segmentos"].append({"inicio": round(s.start, 2), "fim": round(s.end, 2), "texto": s.text.strip(), "palavras": palavras})
        print(f"[{fmt(s.start)}] {s.text.strip()}")
    destino = a.saida or (a.video + ".transcricao.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print(f"\nPronto: {destino}")


# ---------------------------------------------------------------- listar
def cmd_listar(a):
    with open(a.transcricao, encoding="utf-8") as f:
        d = json.load(f)
    for s in d["segmentos"]:
        print(f"[{fmt(s['inicio'])} -> {fmt(s['fim'])}] {s['texto']}")


# ---------------------------------------------------------------- legenda (ASS)
def gerar_ass(transcricao, ini, fim, e, titulo):
    palavras = []
    if transcricao:
        with open(transcricao, encoding="utf-8") as f:
            d = json.load(f)
        for s in d["segmentos"]:
            for w in s.get("palavras", []):
                if w["fim"] > ini and w["inicio"] < fim and w["palavra"]:
                    palavras.append({"i": max(0.0, w["inicio"] - ini), "f": min(fim, w["fim"]) - ini, "p": w["palavra"]})
    margem = int(1920 * e["posicao_legenda"])
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,{e['fonte']},{e['tamanho']},{ass_cor(e['cor_texto'])},{ass_cor(e['cor_destaque'])},{ass_cor(e['cor_contorno'])},&H80000000,-1,0,0,0,100,100,0,0,1,{e['contorno']},{e['sombra']},2,70,70,{margem},1
Style: Tit,{e['fonte']},64,{ass_cor(e['titulo_cor'])},{ass_cor(e['titulo_cor'])},{ass_cor(e['titulo_fundo'])},{ass_cor(e['titulo_fundo'])},-1,0,0,0,100,100,0,0,3,18,0,8,80,80,170,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    linhas = []
    if titulo:
        linhas.append(f"Dialogue: 1,{ass_tempo(0)},{ass_tempo(e['titulo_segundos'])},Tit,,0,0,0,,{titulo}")
    n = max(1, int(e["palavras_por_bloco"]))
    destaque = ass_cor(e["cor_destaque"])
    for b in range(0, len(palavras), n):
        bloco = palavras[b:b + n]
        for k, w in enumerate(bloco):
            fim_w = bloco[k + 1]["i"] if k + 1 < len(bloco) else w["f"] + 0.25
            txt = []
            for j, x in enumerate(bloco):
                p = x["p"].upper() if e["maiusculas"] else x["p"]
                txt.append("{\\c" + destaque + "}" + p + "{\\r}" if j == k else p)
            linhas.append(f"Dialogue: 0,{ass_tempo(w['i'])},{ass_tempo(fim_w)},Leg,,0,0,0,,{' '.join(txt)}")
    return cab + "\n".join(linhas) + "\n"


# ---------------------------------------------------------------- cortar
def cmd_cortar(a):
    precisa("ffmpeg")
    e = dict(ESTILO_PADRAO)
    if a.estilo:
        with open(a.estilo, encoding="utf-8") as f:
            e.update(json.load(f))
    ini, fim = tempo(a.inicio), tempo(a.fim)
    if fim <= ini:
        sys.exit("[erro] --fim precisa ser depois de --inicio")
    dur = fim - ini
    zooms = [tempo(z) - ini for z in a.zooms.split(",")] if a.zooms else []
    zooms = [z for z in zooms if 0 <= z < dur]

    tmp = tempfile.mkdtemp(prefix="cortepronto_")
    ass = os.path.join(tmp, "legenda.ass")
    with open(ass, "w", encoding="utf-8") as f:
        f.write(gerar_ass(a.transcricao, ini, fim, e, a.titulo))

    Z, D = float(e["zoom"]), float(e["duracao_zoom"])
    if zooms and Z > 0:
        termos = "+".join(f"clip((it-{z:.2f})/0.15,0,1)*clip(({z + D:.2f}-it)/0.15,0,1)" for z in zooms)
        zexpr = f"1+{Z}*min(1,{termos})"
    else:
        zexpr = "1"
    zoom = f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30"

    ass_ff = ass.replace("\\", "/").replace(":", "\\:")
    if e["enquadramento"] == "centro":
        base = "[0:v]scale=-2:1920,crop=1080:1920,setsar=1[v0]"
    else:
        base = ("[0:v]split[a][b];"
                "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.12[bg];"
                "[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v0]")
    filtro = f"{base};[v0]{zoom},ass='{ass_ff}'[v]"
    saida = a.saida or f"corte_{int(ini)}.mp4"
    cmd = ["ffmpeg", "-y", "-ss", str(ini), "-t", str(dur), "-i", a.video,
           "-filter_complex", filtro, "-map", "[v]", "-map", "0:a?",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", saida]
    print("Gerando corte...")
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode != 0:
        sys.exit("[erro] ffmpeg falhou:\n" + r.stderr[-1500:])
    print(f"Pronto: {saida}  ({dur:.1f}s, 1080x1920)")


def main():
    p = argparse.ArgumentParser(description="Corte Pronto - editor de cortes de live")
    sp = p.add_subparsers(dest="cmd", required=True)
    t = sp.add_parser("transcrever"); t.add_argument("video"); t.add_argument("--modelo", default="small"); t.add_argument("--idioma", default="pt"); t.add_argument("--saida")
    l = sp.add_parser("listar"); l.add_argument("transcricao")
    c = sp.add_parser("cortar"); c.add_argument("video"); c.add_argument("--inicio", required=True); c.add_argument("--fim", required=True)
    c.add_argument("--saida"); c.add_argument("--transcricao"); c.add_argument("--estilo"); c.add_argument("--zooms"); c.add_argument("--titulo")
    a = p.parse_args()
    {"transcrever": cmd_transcrever, "listar": cmd_listar, "cortar": cmd_cortar}[a.cmd](a)


if __name__ == "__main__":
    main()
