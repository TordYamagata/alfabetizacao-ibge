import csv
import requests
from pathlib import Path

BASE = "https://apisidra.ibge.gov.br"
TABELA = 9542

DESTINO = (
    Path(__file__).resolve().parent
    / "alfabetizacao_uf_sexo_raca.csv"
)

COLUNAS = [
    "uf",
    "sexo",
    "cor_raca",
    "populacao_total",
    "populacao_alfabetizada",
]


def consultar(url):
    resposta = requests.get(url, timeout=120)
    if not resposta.ok:
        print("URL:", url)
        print("Resposta:", resposta.text[:1000])
        resposta.raise_for_status()
    return resposta.json()


def localizar(texto, opcoes):
    for item in opcoes:
        nome = item["nome"].lower()
        if texto in nome:
            return item
    raise ValueError(f"Classificacao nao encontrada: {texto}")


def main():
    print("Consultando metadados do IBGE...")

    meta = consultar(
        f"{BASE}/metadados/agregados/{TABELA}"
    )

    classificacoes = []

    for codigo, dados in meta["classificacoes"].items():
        classificacoes.append({
            "codigo": codigo,
            "nome": dados["nome"],
            "categorias": dados["categorias"],
        })

    for item in classificacoes:
        print(item["codigo"], item["nome"])

    sexo = localizar("sexo", classificacoes)
    raca = localizar("cor ou raça", classificacoes)

    alfabetizacao = localizar(
        "alfabetização", classificacoes
    )

    def codigo_categoria(classe, texto):
        for codigo, nome in classe["categorias"].items():
            if texto in nome.lower():
                return codigo
        raise ValueError(
            f"Categoria nao encontrada: {texto}"
        )

    cod_homens = codigo_categoria(sexo, "homens")
    cod_mulheres = codigo_categoria(sexo, "mulheres")

    cod_total = codigo_categoria(
        alfabetizacao, "total"
    )

    cod_alfabetizadas = codigo_categoria(
        alfabetizacao, "alfabetiz"
    )

    racas = {}

    for codigo, nome in raca["categorias"].items():
        if nome.lower() in [
            "branca",
            "preta",
            "parda",
            "amarela",
            "indígena",
        ]:
            racas[codigo] = nome

    print("Consultando dados do Censo 2022...")

    url = (
        f"{BASE}/values/t/{TABELA}"
        "/n3/all/v/all/p/2022"
        f"/c{sexo['codigo']}/{cod_homens},{cod_mulheres}"
        f"/c{raca['codigo']}/{','.join(racas)}"
        f"/c{alfabetizacao['codigo']}/"
        f"{cod_total},{cod_alfabetizadas}"
    )

    dados = consultar(url)

    if len(dados) < 2:
        raise ValueError("Nenhum dado retornado.")

    cabecalho = dados[0]

    def achar_coluna(texto):
        for chave, valor in cabecalho.items():
            if texto in str(valor).lower():
                if not chave.endswith("C"):
                    return chave
        raise ValueError(
            f"Coluna nao encontrada: {texto}"
        )

    col_uf = achar_coluna("unidade da federação")
    col_sexo = achar_coluna("sexo")
    col_raca = achar_coluna("cor ou raça")
    col_alf = achar_coluna("alfabetização")

    registros = {}

    for item in dados[1:]:
        uf = item[col_uf]
        sexo_nome = item[col_sexo]
        raca_nome = item[col_raca]
        condicao = item[col_alf].lower()

        try:
            valor = int(item["V"])
        except (ValueError, TypeError):
            continue

        chave = (uf, sexo_nome, raca_nome)

        if chave not in registros:
            registros[chave] = {}

        if condicao == "total":
            registros[chave]["total"] = valor

        elif "alfabetiz" in condicao:
            registros[chave]["alfabetizada"] = valor

    linhas = []

    for chave, valores in registros.items():
        total = valores.get("total")
        alfabetizada = valores.get("alfabetizada")

        if total is None or alfabetizada is None:
            continue

        if total <= 0 or alfabetizada > total:
            continue

        linhas.append({
            "uf": chave[0],
            "sexo": chave[1],
            "cor_raca": chave[2],
            "populacao_total": total,
            "populacao_alfabetizada": alfabetizada,
        })

    if not linhas:
        raise ValueError(
            "Nenhum registro valido encontrado."
        )

    with open(
        DESTINO,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=COLUNAS,
        )

        escritor.writeheader()
        escritor.writerows(linhas)

    print("CSV criado com sucesso!")
    print("Arquivo:", DESTINO)
    print("Registros:", len(linhas))


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print("Erro:", erro)
