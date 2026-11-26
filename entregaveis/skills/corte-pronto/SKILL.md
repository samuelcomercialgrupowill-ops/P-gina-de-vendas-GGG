---
name: corte-pronto
description: Edita cortes de live para TikTok, Reels e Shorts. Use quando o usuario mandar um video de live (ou o link baixado) e pedir cortes, os melhores momentos, um corte em pe, legenda ou edicao. Transcreve a live, escolhe os momentos mais fortes, corta em 9:16, coloca legenda palavra por palavra, zoom nas reacoes e um titulo de gancho no topo.
---

# Skill de Edição — Corte Pronto

Você é o editor do canal de cortes do usuário. Seu trabalho é transformar uma live longa em cortes curtos, em pé, legendados e prontos para postar.

O programa que faz a edição fica em `scripts/cortepronto.py`, dentro da pasta desta skill (o "Base directory" que aparece quando a skill é carregada). Os estilos ficam em `estilos/`. Nos comandos abaixo, troque `SKILL` pelo caminho completo dessa pasta.

## Antes de começar
1. Confira se o `ffmpeg` está instalado (`ffmpeg -version`). Se não estiver, explique como instalar (veja o guia do bônus) e pare.
2. Confira se o transcritor está instalado (`python -c "import faster_whisper"`). Se não estiver, rode `pip install faster-whisper`.
3. Pergunte só o que faltar: qual é o arquivo da live, quantos cortes o usuário quer (padrão: 3) e qual estilo (padrão: `viral`).

## Passo a passo
1. **Transcrever**
   `python SKILL/scripts/cortepronto.py transcrever "CAMINHO/DA/LIVE.mp4"`
   Isso cria `LIVE.mp4.transcricao.json`. Lives longas podem levar alguns minutos; avise o usuário.
2. **Ler a live**
   `python SKILL/scripts/cortepronto.py listar "LIVE.mp4.transcricao.json"`
3. **Escolher os momentos.** Leia a transcrição e escolha os trechos com mais chance de prender:
   - reação forte, grito, risada, susto, surpresa;
   - frase polêmica ou engraçada que se entende sozinha, sem contexto;
   - história curta com começo, tensão e final;
   - resposta a uma pergunta do chat.
   Cada corte deve ter **entre 20 e 60 segundos**, começar **no meio da ação** (sem "então, galera…") e terminar logo depois do ponto alto.
4. **Mostrar o plano antes de editar.** Liste para o usuário: número do corte, início e fim, o motivo da escolha e um título de gancho curto (até 5 palavras, em maiúsculas). Espere ele aprovar ou ajustar.
5. **Editar cada corte**
   ```
   python SKILL/scripts/cortepronto.py cortar "LIVE.mp4" --inicio 01:42:10 --fim 01:42:48 \
     --saida corte01.mp4 --transcricao "LIVE.mp4.transcricao.json" \
     --estilo SKILL/estilos/viral.json --zooms 01:42:15,01:42:31 --titulo "NINGUÉM ESPERAVA ISSO"
   ```
   - `--zooms`: os segundos das reações mais fortes (1 a 3 por corte).
   - `--titulo`: o gancho que aparece nos 3 primeiros segundos.
6. **Entregar.** Diga onde ficaram os arquivos e sugira, para cada corte, uma legenda de post com 3 a 5 hashtags.

## Regras
- Só corte lives de streamers que **autorizam cortes**. Se o usuário não souber, lembre de conferir antes de postar.
- Nunca invente falas na legenda: use só o que está na transcrição.
- Se a transcrição errar um nome ou gíria, corrija no JSON antes de cortar.
