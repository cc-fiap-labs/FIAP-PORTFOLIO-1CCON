"""
Neighborhood Action Dashboard - Jardins (São Paulo - SP)
Global Solution FIAP - Equipe cc-fiap-labs

Painel comunitário de ocorrências de bairro, em modo texto (terminal).
Usa apenas Python básico: funções, condicionais, laços, listas, dicionários
e leitura simples de arquivos. Todas as ocorrências são FICTÍCIAS.

Como executar (dentro da pasta GLOBAL-SOLUTION-1):
    python src/sistema.py
"""

import os

# ============================================================
# 1. CONSTANTES (valores padronizados)
# ============================================================
BAIRRO = "Jardins"
CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"]
STATUS = ["aberta", "em_analise", "concluida"]
DIA_ATUAL = 15  # "hoje" na simulação: usado em novos cadastros e atualizações

# Nomes para mostrar na tela
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

# Caminho dos arquivos: sempre a partir da pasta deste arquivo,
# para funcionar de qualquer lugar onde o programa for chamado
PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
ARQUIVO_OCORRENCIAS = os.path.join(PASTA_DADOS, "ocorrencias.csv")
ARQUIVO_HISTORICO = os.path.join(PASTA_DADOS, "historico.csv")

LINHA = "=" * 66


# ============================================================
# Funções de apoio
# ============================================================
def normalizar(texto):
    """Deixa o texto em minúsculas, sem espaços nas pontas e sem acentos.
    Assim "Iluminação" e "iluminacao" são entendidos como a mesma coisa."""
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


def eh_numero(texto): # confere se o texto é um número inteiro
    """True se o texto for um número inteiro (ex.: "12")."""
    return texto.strip().isdigit()


def escolher(opcoes, nomes, pergunta, permite_vazio=False):
    """Mostra uma lista numerada e aceita o número OU o nome digitado.
    Devolve o valor padronizado, "" (se vazio permitido) ou None (inválido)."""
    print(pergunta)
    for i in range(len(opcoes)):
        print(f"  {i + 1}. {nomes[opcoes[i]]}")
    resposta = input("> ").strip()
    if resposta == "" and permite_vazio:
        return ""
    if eh_numero(resposta) and 1 <= int(resposta) <= len(opcoes):
        return opcoes[int(resposta) - 1]
    resposta = normalizar(resposta)
    if resposta in opcoes:
        return resposta
    return None


# ============================================================
# 3. VALIDAÇÃO DE UMA OCORRÊNCIA
# ============================================================
def validar_ocorrencia(dados, indice):
    """Confere os campos obrigatórios e devolve a lista de erros.
    Lista vazia = registro válido."""
    erros = []
    codigo = dados["id"]

    # OR: basta um dos dois problemas para o código ser recusado
    if codigo == "" or codigo in indice:
        erros.append("código vazio ou repetido")

    # NOT: a categoria precisa estar na lista oficial
    if not (dados["categoria"] in CATEGORIAS):
        erros.append("categoria ausente ou inválida")

    if dados["descricao"] == "" or dados["local"] == "":
        erros.append("descrição ou local ausente")

    if not eh_numero(dados["dia_abertura"]):
        erros.append("dia de abertura inválido")

    if dados["status"] not in STATUS:
        erros.append("status desconhecido")

    # AND: só faz sentido conferir a conclusão quando o status é "concluida"
    if dados["status"] == "concluida" and (
            not eh_numero(dados["dia_conclusao"])
            or (eh_numero(dados["dia_abertura"])
                and int(dados["dia_conclusao"]) < int(dados["dia_abertura"]))):
        erros.append("conclusão ausente ou anterior à abertura")

    return erros


# ============================================================
# 4. CARREGAR ARQUIVOS
# ============================================================
def carregar_ocorrencias():
    """Lê o CSV, valida cada linha e monta a LISTA e o DICIONÁRIO (índice)."""
    ocorrencias = []   # LISTA: todas as ocorrências, na ordem do arquivo
    indice = {}        # DICIONÁRIO: código -> ocorrência (busca direta)
    rejeitadas = []
    reservados = []    # códigos de registros rejeitados: não podem ser reutilizados

    arquivo = open(ARQUIVO_OCORRENCIAS, "r", encoding="utf-8")
    linhas = arquivo.readlines()
    arquivo.close()

    for numero in range(1, len(linhas)):  # começa em 1 para pular o cabeçalho
        texto = linhas[numero].strip()
        if texto == "":
            continue
        partes = texto.split(";")
        while len(partes) < 7:  # linha curta: completa com campos vazios
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
        erros = validar_ocorrencia(dados, indice)
        if len(erros) == 0:
            dados["dia_abertura"] = int(dados["dia_abertura"])
            if dados["dia_conclusao"] != "":
                dados["dia_conclusao"] = int(dados["dia_conclusao"])
            ocorrencias.append(dados)
            indice[dados["id"]] = dados
        else:
            rejeitadas.append((numero + 1, dados["id"], erros))
            if eh_numero(dados["id"]):
                reservados.append(dados["id"])

    if len(rejeitadas) > 0:
        print(f"\nAtenção: {len(rejeitadas)} registro(s) do arquivo foram ignorados:")
        for linha, codigo, erros in rejeitadas:
            print(f"  - Linha {linha} (código {codigo or '?'}): {', '.join(erros)}.")
        print("  Corrija o arquivo data/ocorrencias.csv para incluí-los.")

    return ocorrencias, indice, reservados


def carregar_historico():
    """Lê o histórico de mudanças de status (do mais antigo ao mais novo)."""
    historico = []
    arquivo = open(ARQUIVO_HISTORICO, "r", encoding="utf-8")
    linhas = arquivo.readlines()
    arquivo.close()
    for numero in range(1, len(linhas)):
        partes = linhas[numero].strip().split(";")
        if len(partes) == 4:
            historico.append({"dia": int(partes[0]), "id": partes[1],
                              "de": partes[2], "para": partes[3]})
    return historico


# ============================================================
# 5. MONTAR FILA, PILHA E HIERARQUIA
# ============================================================
def montar_fila(ocorrencias):
    """FILA (FIFO): ocorrências abertas, da mais antiga para a mais nova.
    A primeira registrada é a primeira a ser examinada."""
    abertas = []
    for oc in ocorrencias:
        if oc["status"] == "aberta":
            abertas.append(oc)
    # ordena pelo dia de abertura (ordenação por inserção, feita à mão)
    for i in range(1, len(abertas)):
        atual = abertas[i]
        j = i - 1
        while j >= 0 and abertas[j]["dia_abertura"] > atual["dia_abertura"]:
            abertas[j + 1] = abertas[j]
            j -= 1
        abertas[j + 1] = atual
    fila = []
    for oc in abertas:
        fila.append(oc["id"])
    return fila


def montar_pilha(historico):
    """PILHA (LIFO): o evento mais recente fica no topo (fim da lista)."""
    pilha = []
    for evento in historico:
        pilha.append(evento)  # empilhar
    return pilha


def montar_hierarquia(ocorrencias):
    """HIERARQUIA: bairro -> categoria -> lista de códigos."""
    hierarquia = {BAIRRO: {}}
    for categoria in CATEGORIAS:
        hierarquia[BAIRRO][categoria] = []
    for oc in ocorrencias:
        hierarquia[BAIRRO][oc["categoria"]].append(oc["id"])
    return hierarquia


# ============================================================
# 6. LISTAR
# ============================================================
def listar(ocorrencias, titulo="OCORRÊNCIAS"):
    if len(ocorrencias) == 0:
        print("\nNenhuma ocorrência encontrada.")
        return
    print(f"\n{titulo} ({len(ocorrencias)})")
    print(f"{'CÓDIGO':<7} {'CATEGORIA':<15} {'LOCAL':<36} {'STATUS'}")
    print("-" * 70)
    for oc in ocorrencias:
        print(f"{oc['id']:<7} {NOME_CATEGORIA[oc['categoria']]:<15} "
              f"{oc['local']:<36} {NOME_STATUS[oc['status']]}")


# ============================================================
# 7. BUSCAR POR CÓDIGO (usa o dicionário)
# ============================================================
def buscar(indice):
    codigo = input("\nDigite o código da ocorrência (ex.: 005): ").strip()
    if eh_numero(codigo):
        codigo = codigo.zfill(3)  # "5" vira "005"
    if codigo in indice:
        oc = indice[codigo]
        print(f"\nOcorrência {oc['id']}")
        print(f"  Categoria:   {NOME_CATEGORIA[oc['categoria']]}")
        print(f"  Descrição:   {oc['descricao']}")
        print(f"  Local:       {oc['local']} - {BAIRRO}")
        print(f"  Aberta no:   dia {oc['dia_abertura']}")
        print(f"  Status:      {NOME_STATUS[oc['status']]}")
        if oc["status"] == "concluida":
            print(f"  Concluída no: dia {oc['dia_conclusao']}")
    else:
        print(f"\nOcorrência {codigo or '(vazio)'} não encontrada. Confira o número e tente de novo.")


# ============================================================
# 8. FILTRAR POR CATEGORIA E/OU STATUS
# ============================================================
def filtrar(ocorrencias):
    print("\nFiltro: deixe em branco (só Enter) para não filtrar por aquele campo.")
    categoria = escolher(CATEGORIAS, NOME_CATEGORIA, "Categoria:", permite_vazio=True)
    if categoria is None:
        print("Categoria inválida. Escolha um número da lista.")
        return
    status = escolher(STATUS, NOME_STATUS, "Status:", permite_vazio=True)
    if status is None:
        print("Status inválido. Escolha um número da lista.")
        return

    resultado = []
    for oc in ocorrencias:
        # Expressão booleana do filtro: campo vazio significa "qualquer valor"
        if (categoria == "" or oc["categoria"] == categoria) and (status == "" or oc["status"] == status):
            resultado.append(oc)
    listar(resultado, "RESULTADO DO FILTRO")


# ============================================================
# 9. CADASTRAR NOVA OCORRÊNCIA
# ============================================================
def proximo_codigo(indice, reservados):
    """Maior código já usado + 1. Conta também os códigos reservados
    (registros rejeitados), para não criar dois registros com o mesmo número."""
    maior = 0
    for codigo in indice:
        if int(codigo) > maior:
            maior = int(codigo)
    for codigo in reservados:
        if int(codigo) > maior:
            maior = int(codigo)
    return str(maior + 1).zfill(3)


def cadastrar(ocorrencias, indice, reservados, fila, hierarquia):
    print("\nNOVA OCORRÊNCIA (não informe nomes, telefones ou endereços com número)")
    categoria = escolher(CATEGORIAS, NOME_CATEGORIA, "Categoria:")
    descricao = input("Descrição breve: ").strip()
    local = input("Local genérico (ex.: Praça arborizada): ").strip()

    dados = {
        "id": proximo_codigo(indice, reservados),
        "categoria": categoria if categoria is not None else "",
        "descricao": descricao,
        "local": local,
        "dia_abertura": str(DIA_ATUAL),
        "status": "aberta",
        "dia_conclusao": "",
    }
    erros = validar_ocorrencia(dados, indice)
    if len(erros) > 0:
        print("\nNão foi possível cadastrar:")
        for erro in erros:
            print(f"  - {erro}")
        print("Nada foi salvo. Tente de novo preenchendo todos os campos.")
        return

    dados["dia_abertura"] = DIA_ATUAL
    ocorrencias.append(dados)                           # lista
    indice[dados["id"]] = dados                         # dicionário
    fila.append(dados["id"])                            # fim da fila
    hierarquia[BAIRRO][dados["categoria"]].append(dados["id"])  # hierarquia
    print(f"\nOcorrência {dados['id']} cadastrada com status Aberta. Ela entrou no fim da fila de análise.")


# ============================================================
# 10. ATUALIZAR STATUS (com histórico e pilha)
# ============================================================
def mudanca_permitida(atual, novo):
    """Expressão booleana documentada no README:
    só é permitido avançar uma etapa por vez."""
    return (atual == "aberta" and novo == "em_analise") or (atual == "em_analise" and novo == "concluida")


def atualizar_status(codigo, novo, indice, fila, pilha, historico):
    """IF / ELIF / ELSE: os casos se excluem. Só um caminho é seguido."""
    if codigo not in indice:
        print(f"\nOcorrência {codigo or '(vazio)'} não encontrada.")
        return False
    elif novo not in STATUS:
        print("\nStatus desconhecido. Opções: aberta, em_analise, concluida.")
        return False
    elif not mudanca_permitida(indice[codigo]["status"], novo):
        atual = indice[codigo]["status"]
        print(f"\nNão é possível passar de {NOME_STATUS[atual]} para {NOME_STATUS[novo]}.")
        print("Caminho permitido: Aberta -> Em análise -> Concluída.")
        return False
    else:
        oc = indice[codigo]
        atual = oc["status"]
        oc["status"] = novo
        if novo == "concluida":
            oc["dia_conclusao"] = DIA_ATUAL
        if atual == "aberta" and codigo in fila:
            fila.remove(codigo)  # saiu da fila: já foi examinada

        evento = {"dia": DIA_ATUAL, "id": codigo, "de": atual, "para": novo}
        historico.append(evento)
        pilha.append(evento)  # empilhar: vira o topo
        print(f"\nOcorrência {codigo}: {NOME_STATUS[atual]} -> {NOME_STATUS[novo]}. Registrado no histórico.")
        return True


def pedir_atualizacao(indice, fila, pilha, historico):
    codigo = input("\nCódigo da ocorrência: ").strip()
    if eh_numero(codigo):
        codigo = codigo.zfill(3)
    if codigo not in indice:
        print(f"\nOcorrência {codigo or '(vazio)'} não encontrada.")
        return
    print(f"Status atual: {NOME_STATUS[indice[codigo]['status']]}")
    novo = escolher(STATUS, NOME_STATUS, "Novo status:")
    if novo is None:
        print("\nStatus desconhecido. Escolha um número da lista.")
        return
    atualizar_status(codigo, novo, indice, fila, pilha, historico)


# ============================================================
# 11. EXAMINAR A PRÓXIMA DA FILA
# ============================================================
def examinar_proxima(indice, fila, pilha, historico):
    if len(fila) == 0:
        print("\nNão há ocorrências aguardando análise.")
        return
    print(f"\nFila de análise ({len(fila)}): {' -> '.join(fila)}")
    codigo = fila[0]  # FIFO: o primeiro que entrou
    oc = indice[codigo]
    print(f"Próxima: {codigo} - {NOME_CATEGORIA[oc['categoria']]} - {oc['descricao']} (aberta no dia {oc['dia_abertura']})")
    atualizar_status(codigo, "em_analise", indice, fila, pilha, historico)


# ============================================================
# 12. ÚLTIMAS ATUALIZAÇÕES (consulta o topo da pilha)
# ============================================================
def ver_ultimas(pilha, quantidade=5):
    if len(pilha) == 0:
        print("\nNenhuma atualização registrada.")
        return
    print(f"\nÚLTIMAS ATUALIZAÇÕES (da mais recente para a mais antiga)")
    posicao = len(pilha) - 1  # topo da pilha
    mostrados = 0
    while posicao >= 0 and mostrados < quantidade:
        ev = pilha[posicao]
        print(f"  Dia {ev['dia']:>2} | {ev['id']} | {NOME_STATUS[ev['de']]} -> {NOME_STATUS[ev['para']]}")
        posicao -= 1
        mostrados += 1


# ============================================================
# 13. MATRIZ CATEGORIA x STATUS
# ============================================================
def montar_matriz(ocorrencias):
    """Lista de listas: uma linha por categoria, uma coluna por status."""
    matriz = []
    for _ in CATEGORIAS:
        matriz.append([0, 0, 0])
    for oc in ocorrencias:
        linha = CATEGORIAS.index(oc["categoria"])
        coluna = STATUS.index(oc["status"])
        matriz[linha][coluna] += 1
    return matriz


# ============================================================
# 14. PAINEL DE INDICADORES (o "dashboard")
# ============================================================
def porcentagem(parte, total):
    return parte / total * 100


def br(numero):
    """Formata com 1 casa decimal e vírgula, como se escreve em português."""
    return f"{numero:.1f}".replace(".", ",")


def painel(ocorrencias):
    total = len(ocorrencias)
    if total == 0:
        print("\nSem dados para calcular os indicadores.")
        return
    matriz = montar_matriz(ocorrencias)

    print(f"\n{LINHA}")
    print(f"  PAINEL DE INDICADORES - {BAIRRO.upper()} (dados fictícios, dia {DIA_ATUAL})")
    print(LINHA)

    # Totais por status = soma de cada COLUNA da matriz
    totais_status = [0, 0, 0]
    for linha in matriz:
        for c in range(3):
            totais_status[c] += linha[c]
    pendencias = totais_status[0] + totais_status[1]
    print(f"Total de ocorrências: {total}   Pendências: {pendencias}   Concluídas: {totais_status[2]}")

    print("\nPOR CATEGORIA           qtd       %")
    for i in range(len(CATEGORIAS)):
        qtd = matriz[i][0] + matriz[i][1] + matriz[i][2]  # soma da LINHA
        pct = porcentagem(qtd, total)
        print(f"  {NOME_CATEGORIA[CATEGORIAS[i]]:<18} {qtd:>4}  {br(pct):>5}%  {'█' * qtd}")

    print("\nPOR STATUS              qtd       %")
    for c in range(len(STATUS)):
        pct = porcentagem(totais_status[c], total)
        print(f"  {NOME_STATUS[STATUS[c]]:<18} {totais_status[c]:>4}  {br(pct):>5}%  {'█' * totais_status[c]}")

    print("\nMATRIZ CATEGORIA x STATUS")
    print(f"  {'':<18} {'Aberta':>8} {'Em análise':>11} {'Concluída':>10}")
    for i in range(len(CATEGORIAS)):
        print(f"  {NOME_CATEGORIA[CATEGORIAS[i]]:<18} {matriz[i][0]:>8} {matriz[i][1]:>11} {matriz[i][2]:>10}")

    # Indicador adicional: tempo médio entre abertura e conclusão
    soma_dias = 0
    concluidas = 0
    for oc in ocorrencias:
        if oc["status"] == "concluida":
            soma_dias += oc["dia_conclusao"] - oc["dia_abertura"]
            concluidas += 1
    print("\nTEMPO MÉDIO ATÉ A CONCLUSÃO")
    if concluidas > 0:
        media = soma_dias / concluidas
        print(f"  {br(media)} dias")
        print(f"  Fórmula: soma(dia_conclusao - dia_abertura) / nº de concluídas = {soma_dias} / {concluidas}")
    else:
        print("  Ainda não há ocorrências concluídas.")

    # Interpretação automática: categoria com mais pendências
    maior = -1
    critica = ""
    for i in range(len(CATEGORIAS)):
        pend = matriz[i][0] + matriz[i][1]
        if pend > maior:
            maior = pend
            critica = CATEGORIAS[i]
    concluidas_critica = matriz[CATEGORIAS.index(critica)][2]
    print("\nINTERPRETAÇÃO")
    print(f"  {NOME_CATEGORIA[critica]} é a categoria com mais pendências ({maior}) "
          f"e tem {concluidas_critica} concluída(s).")
    print(f"  No conjunto simulado, é a necessidade mais urgente do bairro.")
    print(f"  {br(porcentagem(pendencias, total))}% das ocorrências ainda estão pendentes.")
    print(LINHA)


# ============================================================
# 15. HIERARQUIA BAIRRO -> CATEGORIA -> OCORRÊNCIAS
# ============================================================
def mostrar_hierarquia(hierarquia, indice):
    print(f"\n{BAIRRO}")
    for categoria in hierarquia[BAIRRO]:
        codigos = hierarquia[BAIRRO][categoria]
        print(f"  {NOME_CATEGORIA[categoria]} ({len(codigos)})")
        for codigo in codigos:
            oc = indice[codigo]
            print(f"    {codigo} - {oc['local']} - {NOME_STATUS[oc['status']]}")


# ============================================================
# 16. MENU PRINCIPAL
# ============================================================
def menu():
    print(LINHA)
    print(f"  NEIGHBORHOOD ACTION DASHBOARD - {BAIRRO} (São Paulo - SP)")
    print("  Todas as ocorrências são fictícias, criadas para testar o sistema.")
    print(LINHA)

    ocorrencias, indice, reservados = carregar_ocorrencias()
    historico = carregar_historico()
    fila = montar_fila(ocorrencias)
    pilha = montar_pilha(historico)
    hierarquia = montar_hierarquia(ocorrencias)
    print(f"\n{len(ocorrencias)} ocorrências carregadas. {len(historico)} eventos no histórico.")

    while True:
        print("\nO que você quer fazer?")
        print("  1. Listar todas as ocorrências")
        print("  2. Buscar ocorrência por código")
        print("  3. Filtrar por categoria e/ou status")
        print("  4. Cadastrar nova ocorrência")
        print("  5. Examinar a próxima da fila (Aberta -> Em análise)")
        print("  6. Atualizar status de uma ocorrência")
        print("  7. Ver últimas atualizações")
        print("  8. Ver painel de indicadores")
        print("  9. Ver organização por categoria")
        print("  0. Sair")
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
            print("\nAté logo! (As alterações desta sessão ficam só na memória.)")
            break
        else:
            print("\nOpção inválida. Digite um número de 0 a 9.")


if __name__ == "__main__":
    menu()
