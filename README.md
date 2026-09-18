# Kyoto Studios — Racing Tracks

Repositório público de pistas usadas pelo **KS Racing App / Eclipse RP**.

## Estrutura

- `tracks/circuit/`: 86 pistas de circuito em JSON.
- `index.json`: índice legível por aplicações, com nome, caminho, quantidade de checkpoints e URL RAW.
- `TRACK_URLS.md`: lista completa de links diretos para importação.

## Importar uma pista

No KS Racing App, abra **Importar pista** e cole a URL RAW da pista no campo **URL da pista**.

Exemplo:

```text
https://raw.githubusercontent.com/kyotostudios/ks_racing_tracks/main/tracks/circuit/10-80.json
```

Os arquivos publicados em `tracks/circuit/` preservam o JSON original; apenas os nomes de arquivo foram normalizados para URLs estáveis.
