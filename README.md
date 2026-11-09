# Projeto Integrado — Alfabetização por Sexo e Raça

Dashboard em Python/Streamlit para comparar taxas de alfabetização por UF, sexo e cor ou raça, com estatística descritiva.

## Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Dados

O aplicativo não inclui dados inventados. Envie na barra lateral um CSV UTF-8 com estas colunas:

- `uf`: sigla da Unidade da Federação
- `sexo`: categoria de sexo
- `cor_raca`: categoria de cor ou raça
- `populacao_total`: população do grupo no recorte etário escolhido
- `populacao_alfabetizada`: pessoas alfabetizadas nesse grupo

Cada linha deve corresponder a uma combinação exclusiva de UF, sexo e cor ou raça. **Não misture subtotais e linhas detalhadas**. Use o mesmo ano e faixa etária em todas as linhas (recomendação: Censo 2022, pessoas de 15 anos ou mais).

Fonte: https://sidra.ibge.gov.br/

A taxa é calculada por `100 * populacao_alfabetizada / populacao_total`. O total é ponderado pela população; as estatísticas descritivas por UF tratam cada UF como uma observação.

## Entrega no GitHub

Crie um repositório e envie `app.py`, `requirements.txt`, `README.md` e o CSV oficial tratado. Documente no README a tabela SIDRA, ano, variáveis e filtros usados na extração.
