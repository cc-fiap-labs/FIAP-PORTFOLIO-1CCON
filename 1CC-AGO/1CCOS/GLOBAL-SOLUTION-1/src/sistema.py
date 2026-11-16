
import os

## CONSTANTES
BAIRRO = "Jardins"
CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"]
STATUS = ["aberta", "em_analise", "concluida"]
DIA_ATUAL = 15 #Dia de hoje para simulação

NOME_CATEGORIA = {
    "iluminacao": "Iluminação",
    "acessibilidade": "Acessibilidade",
    "limpeza": "Limpeza",
    "conservacao": "Conservação",


}
NOME_STATUS = {
    "aberta": "Aberta",
    "em_analise": "Em análise",
    "concluida": "Concluída",
}

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
ARQUIVO_OCORRENCIAS = os.path.join(PASTA_DADOS, "ocorrencias.csv")
ARQUIVO_HISTORICO = os.path.join(PASTA_DADOS, "historico.csv")

LINHA = "=" * 66

#FUNÇÕES DE APOIO

def normalizar(texto):
    texto = texto.strip().lower().replace(" ", "_")
    trocas = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
              "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}
    resultado = ""
    for letra in texto:
        if letra in trocas:
            resultado += trocas[letra]
        else:
            resultado += letra
    return resultado

def numero_True(texto):
    return texto.strip().isdigit()


def escolher(opcoes, nomes, pergunta, permite_vazio=False):
    print(pergunta)

    for i in range(len(opcoes)):
        print(i + 1, "-", nomes[opcoes[i]])
    resposta = input("> ").strip()

    if resposta == "" and permite_vazio:
        return ""

    if numero_True(resposta):
        numero = int(resposta)
        if numero >= 1 and numero <= len(opcoes):
            return opcoes[numero - 1]
    resposta = normalizar(resposta)

    if resposta in opcoes:
        return resposta
    return None



#VALIDAR OCORRÊNCIAS

def validar_ocorrencias(dados, indice):
    erros = []
    codigo = dados["id"]

    if codigo == "" or codigo in indice:
        erros.append("código vazio ou repetido")

    if not (dados["categoria"] in CATEGORIAS):
        erros.append("categoria ausente ou inválida")

    if dados["descricao"] == "" or dados["local"] == "":
        erros.append("descrição ou local ausente")

    if not numero_True(dados["dia_abertura"]):
        erros.append("dia de abertura inválido")

    if dados["status"] not in STATUS:
        erros.append("status desconhecido")


    if dados["status"] == "concluida" and (
            not numero_True(dados["dia_conclusao"])
            or (numero_True(dados["dia_abertura"])
                and int(dados["dia_conclusao"]) < int(dados["dia_abertura"]))):
        erros.append("conclusão ausente ou anterior à abertura")

    return erros


#CARREGAR OCORRÊNCIAS
def carregar_ocorrencias():
    ocorrencias = []
    indice = {}
    reservadas = []

    arquivo = open(ARQUIVO_OCORRENCIAS, "r", encoding="utf-8")
    linhas = arquivo.readlines()
    arquivo.close()

    for i in range(1, len(linhas)):
        texto = linhas[i].strip()

        if texto == "":
            continue
        partes = texto.split(";")
        while len(partes) < 7:
            partes.append("")
        dados = {
            "id": partes[0].strip(),
            "categoria": normalizar(partes[1]),
            "descricao": partes[2].strip(),
            "local": partes[3].strip(),
            "dia_abertura": partes[4].strip(),
            "status": normalizar(partes[5]),
            "dia_conclusao": partes[6].strip(),
        }
        erros = validar_ocorrencias(dados, indice)
        if len(erros) == 0:
            dados["dia_abertura"] = int(dados["dia_abertura"])

            if dados["dia_conclusao"] != "":
                dados["dia_conclusao"] = int(dados["dia_conclusao"])

            ocorrencias.append(dados)
            indice[dados["id"]] = dados


        else:
            print("Registro ignorado na linha", i + 1, ":", erros)

            if numero_True(dados["id"]):
                reservadas.append(dados["id"])
    return ocorrencias, indice, reservadas

def carregar_historicos():
    historico = []

    arquivo = open(ARQUIVO_HISTORICO, "r", encoding="utf-8")
    linhas = arquivo.readlines()
    arquivo.close()

    for i in range(1, len(linhas)):
        partes = linhas[i].strip().split(";")

        if len(partes) == 4:
            evento = {
                "dia": int(partes[0]),
                "id": partes[1],
                "de": partes[2],
                "para": partes[3],

            }
            historico.append(evento)
    return historico



# MONTAR FILA, PILHA, HIERARQUIA

def montar_fila(ocorrencias):
    abertas = []
    for oc in ocorrencias:
        if oc["status"] == "aberta":
            abertas.append(oc)
    for i in range( len(abertas)):
        for j in range(i + 1, len(abertas)):
            if abertas[i]["dia_abertura"] >  abertas[j]["dia_abertura"]:
                auxilar = abertas[i]
                abertas[i] = abertas[j]
                abertas[j] = auxilar
    fila = []
    for oc in abertas:
        fila.append(oc["id"])
    return fila


def montar_pilha(historicos):
    pilha = []
    for evento in historicos:
        pilha.append(evento)
    return pilha


def montar_hierarquia(ocorrencias):
    hierarquia = {}
    hierarquia[BAIRRO] = {}

    for categoria in CATEGORIAS:
        hierarquia[BAIRRO][categoria] = []

    for oc in ocorrencias:
        categoria = oc["categoria"]
        codigo = oc["id"]

        hierarquia[BAIRRO][categoria].append(codigo)

    return hierarquia

#LISTAR E BUSCAR OCORRENCIAS

def listar(ocorrencias, titulo="OCORRÊNCIAS"):
    if len(ocorrencias) == 0:
        print("Nenhuma ocorrencia encontrada.")
        return

    print("\n", titulo)

    for oc in ocorrencias:
        cetegoria = NOME_CATEGORIA[oc["categoria"]]
        status = NOME_STATUS[oc["status"]]

        print(oc["id"], "-", cetegoria, "-", oc["local"], "-", status)
def buscar(indice):
    codigo = input("Digite o código: ").strip()

    if numero_True(codigo):
        codigo = str(codigo)
        if numero_True(codigo):
            codigo = codigo.zfill(3)

    if codigo in indice:
        oc = indice[codigo]

        print("\nCódigo:", oc["id"])
        print("Categoria:", NOME_CATEGORIA[oc["categoria"]])
        print("Descrição:", oc["descricao"])
        print("Local:", oc["local"])
        print("Dia de abertura:", oc["dia_abertura"])
        print("Status:", NOME_STATUS[oc["status"]])

        if oc["status"] == "concluida":
            print("Dia de conclusão:", oc["dia_conclusao"])
    else:
        print("Ocorrência não encontrada.")

# FILTAR
def filtrar(ocorrencias):
    print("Se quiser ignorar um filtro, aperte Enter.")

    categoria = escolher(
        CATEGORIAS, NOME_CATEGORIA, "Escolha uma categoria:", True
    )

    if categoria is None:
        print("Categoria inválida.")
        return

    status = escolher(
        STATUS, NOME_STATUS, "Escolha um status:", True
    )

    if status is None:
        print("Status inválido.")
        return

    resultado = []

    for oc in ocorrencias:
        categoria_correta = categoria == "" or oc["categoria"] == categoria
        status_correto = status == "" or oc["status"] == status

        if categoria_correta and status_correto:
            resultado.append(oc)

    listar(resultado, "RESULTADO DO FILTRO")

#CADASTRA OCORRENCIA
def proximo_codigo(indice, reservados):
    maior = 0

    for codigo in indice:
        if int(codigo) > maior:
            maior = int(codigo)

    for codigo in reservados:
        if int(codigo) > maior:
            maior = int(codigo)

    novo_codigo = maior + 1
    return str(novo_codigo).zfill(3)


def cadastrar(ocorrencias, indice, reservados, fila, hierarquia):
    print("\nNOVA OCORRÊNCIA")

    categoria = escolher(CATEGORIAS, NOME_CATEGORIA, "Escolha a categoria:")
    descricao = input("Digite uma descrição: ").strip()
    local = input("Digite o local: ").strip()

    if categoria is None:
        print("Categoria inválida. Cadastro cancelado.")
        return

    dados = {
        "id": proximo_codigo(indice, reservados),
        "categoria": categoria,
        "descricao": descricao,
        "local": local,
        "dia_abertura": str(DIA_ATUAL),
        "status": "aberta",
        "dia_conclusao": ""
    }

    erros = validar_ocorrencias(dados, indice)

    if len(erros) > 0:
        print("Não foi possível cadastrar:", erros)
        return

    dados["dia_abertura"] = int(dados["dia_abertura"])
    # Guarda a ocorrência na lista e no dicionário
    ocorrencias.append(dados)
    indice[dados["id"]] = dados

    # Coloca o código no final da fila
    fila.append(dados["id"])

    # Coloca o código na categoria correspondente
    hierarquia[BAIRRO][categoria].append(dados["id"])

    print("Ocorrência cadastrada com o código", dados["id"])

#ATUALIZAR STATUTUS E GUARDAR HISTÓRICO
def atualizar_status(codigo, novo_status, indice, fila, pilha, historico):
    if codigo not in indice:
        print("Ocorrência não encontrada.")
        return

    if novo_status not in STATUS:
        print("Status inválido.")
        return

    oc = indice[codigo]
    status_antigo = oc["status"]

    if status_antigo == "aberta" and novo_status == "em_analise":
        permitido = True
    elif status_antigo == "em_analise" and novo_status == "concluida":
        permitido = True
    else:
        permitido = False

    if permitido == False:
        print("Não é possível fazer essa mudança de status.")
        print("A ordem correta é: Aberta -> Em análise -> Concluída.")
        return

    oc["status"] = novo_status

    if novo_status == "concluida":
        oc["dia_conclusao"] = DIA_ATUAL

    if codigo in fila:
        fila.remove(codigo)

    evento = {
        "dia": DIA_ATUAL,
        "id": codigo,
        "de": status_antigo,
        "para": novo_status
    }

    # Guarda a mudança no histórico e no topo da pilha
    historico.append(evento)
    pilha.append(evento)

    print("Status atualizado:", NOME_STATUS[status_antigo], "->", NOME_STATUS[novo_status])


def pedir_atualizacao(indice, fila, pilha, historico):
    codigo = input("Digite o código da ocorrência: ").strip()

    if numero_True(codigo):
        codigo = codigo.zfill(3)

    if codigo not in indice:
        print("Ocorrência não encontrada.")
        return

    print("Status atual:", NOME_STATUS[indice[codigo]["status"]])

    novo_status = escolher(STATUS, NOME_STATUS, "Escolha o novo status:")

    if novo_status is None:
        print("Status inválido.")
        return

    atualizar_status(codigo, novo_status, indice, fila, pilha, historico)

# EXAMINAR A PROXIMA OCORRENCIA DA FILA

def examinar_proxima(indice, fila, pilha, historico):
    if len(fila) == 0:
        print("Não existem ocorrências aguardando análise.")
        return

    codigo = fila[0]
    oc = indice[codigo]

    print("\nPróxima ocorrência:")
    print("Código:", codigo)
    print("Categoria:", NOME_CATEGORIA[oc["categoria"]])
    print("Descrição:", oc["descricao"])

    atualizar_status(codigo, "em_analise", indice, fila, pilha, historico)

#VER ULTIMAS ATUALIZACOES DA PILHA
def ver_ultimas(pilha):
    if len(pilha) == 0:
        print("Nenhuma atualização registrada.")
        return

    print("\nÚLTIMAS ATUALIZAÇÕES")

    posicao = len(pilha) - 1
    quantidade = 0

    while posicao >= 0 and quantidade < 5:
        evento = pilha[posicao]

        print(
            "Dia", evento["dia"],
            "| Código:", evento["id"],
            "|", NOME_STATUS[evento["de"]],
            "->", NOME_STATUS[evento["para"]]
        )

        posicao = posicao - 1
        quantidade = quantidade + 1
#MONTAR MATRIZ
def montar_matriz(ocorrencias):
    matriz = []

    for categoria in CATEGORIAS:
        matriz.append([0, 0, 0])

    for oc in ocorrencias:
        linha = CATEGORIAS.index(oc["categoria"])
        coluna = STATUS.index(oc["status"])

        matriz[linha][coluna] = matriz[linha][coluna] + 1

    return matriz

#PAINEL DE INDICADORES
def painel(ocorrencias):
    total = len(ocorrencias)

    if total == 0:
        print("Não existem dados para mostrar.")
        return

    matriz = montar_matriz(ocorrencias)

    totais_status = [0, 0, 0]

    for linha in matriz:
        for coluna in range(3):
            totais_status[coluna] = totais_status[coluna] + linha[coluna]

    pendencias = totais_status[0] + totais_status[1]

    print("\n", LINHA)
    print("PAINEL DE INDICADORES -", BAIRRO)
    print(LINHA)

    print("Total de ocorrências:", total)
    print("Pendências:", pendencias)
    print("Concluídas:", totais_status[2])

    print("\nQUANTIDADE POR CATEGORIA")

    for i in range(len(CATEGORIAS)):
        quantidade = matriz[i][0] + matriz[i][1] + matriz[i][2]
        porcentagem = quantidade / total * 100

        print(NOME_CATEGORIA[CATEGORIAS[i]], ":", quantidade, "-", round(porcentagem, 1), "%")


    print("\nQUANTIDADE POR STATUS")

    for i in range(len(STATUS)):
        porcentagem = totais_status[i] / total * 100

        print(NOME_STATUS[STATUS[i]], ":", totais_status[i], "-", round(porcentagem, 1), "%")

    print("\nMATRIZ CATEGORIA X STATUS")
    print("Categoria | Aberta | Em análise | Concluída")

    for i in range(len(CATEGORIAS)):
        print(
            NOME_CATEGORIA[CATEGORIAS[i]], "|",
            matriz[i][0], "|",
            matriz[i][1], "|",
            matriz[i][2]
        )

    # Calcula o tempo médio para concluir as ocorrências
    soma_dias = 0
    concluidas = 0

    for oc in ocorrencias:
        if oc["status"] == "concluida":
            tempo = oc["dia_conclusao"] - oc["dia_abertura"]
            soma_dias = soma_dias + tempo
            concluidas = concluidas + 1

    print("\nTEMPO MÉDIO PARA CONCLUIR")

    if concluidas > 0:
        media = soma_dias / concluidas
        print(round(media, 1), "dias")
    else:
        print("Ainda não existem ocorrências concluídas.")

    # Descobre qual categoria tem mais pendências
    maior = -1
    categoria_mais_pendente = ""

    for i in range(len(CATEGORIAS)):
        pendentes = matriz[i][0] + matriz[i][1]

        if pendentes > maior:
            maior = pendentes
            categoria_mais_pendente = CATEGORIAS[i]

    print("\nINTERPRETAÇÃO")
    print("Categoria com mais pendências:", NOME_CATEGORIA[categoria_mais_pendente])
    print("Quantidade de pendências:", maior)
    print(LINHA)

#MOSTAR A HIERARQUIA DO BAIRRO

def mostrar_hierarquia(hierarquia, indice):
    print("\nBAIRRO:", BAIRRO)

    for categoria in CATEGORIAS:
        codigos = hierarquia[BAIRRO][categoria]

        print("\n", NOME_CATEGORIA[categoria])

        for codigo in codigos:
            oc = indice[codigo]

            print(
                codigo, "-",
                oc["local"], "-",
                NOME_STATUS[oc["status"]]
            )


#MENU

def menu():

    print("NEIGHBORHOOD ACTION DASHBOARD -", BAIRRO)
    print("Todas as ocorrências são fictícias.")


    ocorrencias, indice, reservados = carregar_ocorrencias()
    historico = carregar_historicos()

    # Monta as estruturas que serão usadas pelo programa
    fila = montar_fila(ocorrencias)
    pilha = montar_pilha(historico)
    hierarquia = montar_hierarquia(ocorrencias)

    print(len(ocorrencias), "ocorrências carregadas.")

    while True:
        print("\nO QUE DESEJA FAZER?")
        print("1 - Listar ocorrências")
        print("2 - Buscar ocorrência")
        print("3 - Filtrar ocorrências")
        print("4 - Cadastrar ocorrência")
        print("5 - Examinar próxima da fila")
        print("6 - Atualizar status")
        print("7 - Ver últimas atualizações")
        print("8 - Ver painel de indicadores")
        print("9 - Ver organização por categoria")
        print("0 - Sair")

        opcao = input("> ").strip()

        if opcao == "1":
            listar(ocorrencias)

        elif opcao == "2":
            buscar(indice)

        elif opcao == "3":
            filtrar(ocorrencias)

        elif opcao == "4":
            cadastrar(ocorrencias, indice, reservados, fila, hierarquia)

        elif opcao == "5":
            examinar_proxima(indice, fila, pilha, historico)

        elif opcao == "6":
            pedir_atualizacao(indice, fila, pilha, historico)

        elif opcao == "7":
            ver_ultimas(pilha)

        elif opcao == "8":
            painel(ocorrencias)

        elif opcao == "9":
            mostrar_hierarquia(hierarquia, indice)

        elif opcao == "0":
            print("Até logo!")
            break

        else:
            print("Opção inválida. Digite um número de 0 a 9.")

menu()



