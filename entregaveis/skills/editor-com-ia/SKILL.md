---
name: editor-com-ia
description: Editor de cortes por pedido em linguagem natural. Use quando o usuario descrever como quer o video ("legenda amarela grande", "zoom nas risadas", "estilo gamer", "mais limpo", "titulo no topo") e pedir para editar um corte ou uma live do jeito dele.
---

# Editor com IA Automático — Corte Pronto

O usuário descreve a edição com as palavras dele e você transforma o pedido em configuração do programa da skill `corte-pronto`. Ela fica ao lado desta pasta: `../corte-pronto/scripts/cortepronto.py` a partir do "Base directory" desta skill. Se ela não estiver instalada, avise o usuário.

## Como traduzir o pedido
Monte um arquivo de estilo (`meu-estilo.json`) a partir do que o usuário pediu. Campos disponíveis:

| O usuário fala… | Campo | Exemplo de valor |
|---|---|---|
| "legenda amarela", "destaque verde" | `cor_destaque` | `"#FFE14D"`, `"#39FF14"` |
| "legenda branca", "letra preta" | `cor_texto` | `"#FFFFFF"` |
| "letra grande", "legenda pequena" | `tamanho` | grande `90`, normal `78`, pequena `60` |
| "tudo maiúsculo" / "normal" | `maiusculas` | `true` / `false` |
| "uma palavra por vez", "frase inteira" | `palavras_por_bloco` | `1` a `6` |
| "legenda mais pra cima / embaixo" | `posicao_legenda` | `0.15` (baixo) a `0.45` (meio) |
| "fundo desfocado" / "tela cheia" | `enquadramento` | `"borrado"` / `"centro"` |
| "zoom forte", "sem zoom" | `zoom` | `0.20` / `0.0` |
| "fonte gamer", "fonte limpa" | `fonte` | `"Impact"` / `"Arial"` |
| "título rosa / laranja" | `titulo_fundo` | `"#FE2C55"` / `"#FF6A3D"` |

Estilos prontos para começar: `../corte-pronto/estilos/viral.json`, `limpo.json` e `gamer.json`.

## Fluxo
1. Leia o pedido e **repita em uma frase** como vai ficar ("Legenda amarela grande, duas palavras por vez, zoom forte nas risadas e título rosa no topo.").
2. Crie `meu-estilo.json` com os campos acima (só os que mudam; o resto usa o padrão).
3. Se o pedido citar momentos ("zoom quando ele grita", "corta a parte da risada"), use a transcrição para achar os segundos exatos.
4. Rode o `cortar` com `--estilo meu-estilo.json` (veja a skill `corte-pronto` para os outros passos).
5. Entregue o corte e pergunte se quer ajustar algo. Ajustes viram uma nova versão do `meu-estilo.json`, sem refazer o resto.

## Exemplos de pedido
- "Faz igual corte de podcast: legenda branca limpa, sem zoom, frase inteira."
- "Quero estilo gamer: fonte Impact, destaque ciano, uma palavra por vez, zoom forte."
- "Legenda amarela no meio da tela e título laranja 'ELE NÃO ACREDITOU'."
