# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="../../../assets/logo-fiap.png"
       alt="FIAP - Faculdade de Informática e Administração Paulista"
       width="40%">
</a>
</p>

<br>

# Neighborhood Action Dashboard: Jardins (São Paulo - SP)

Global Solution 2026: desafio CitizenTech

## Nome do grupo

**cc-fiap-labs**

## 👨‍🎓 Integrantes

| Nome | RM |
| --- | --- |
| Gabriela de Sousa Reis | RM00000 |
| Kauan Henrique Martins Alves | RM00000 |
| Leonardo Gomes Gonçalves | RM00000 |
| Rosangela Sousa de Oliveira | RM00000 |
| Victoria Nascimento Santana | RM00000 |

## 👩‍🏫 Professores

### Tutor(a)
- Nome do tutor(a)

### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a>

---

## 📜 Descrição

### O bairro e o problema

O sistema simula um painel comunitário de ocorrências do bairro **Jardins**, em São Paulo (SP). O bairro é real, mas **todas as ocorrências são fictícias** e foram criadas apenas para testar o sistema.

Problemas de infraestrutura, como um poste apagado, uma calçada quebrada ou lixo acumulado, costumam ser relatados de forma dispersa. Assim, as prioridades não ficam claras e os moradores não conseguem acompanhar o que já foi resolvido. O Neighborhood Action Dashboard organiza esses relatos: cadastra cada ocorrência, classifica por categoria, acompanha o andamento e mostra indicadores simples sobre o bairro.

### Público beneficiado

- Moradores e frequentadores do bairro, que registram e acompanham as demandas.
- Associações de bairro e lideranças comunitárias, que usam os indicadores para saber quais problemas são mais frequentes.
- Pessoas com mobilidade reduzida, já que acessibilidade é uma das categorias acompanhadas.

### O que o sistema faz

| Função | Opção do menu |
| --- | --- |
| Listar todas as ocorrências | 1 |
| Buscar por código | 2 |
| Filtrar por categoria e/ou status | 3 |
| Cadastrar nova ocorrência, com validação | 4 |
| Examinar a próxima da fila (Aberta → Em análise) | 5 |
| Atualizar o status, com registro no histórico | 6 |
| Ver as últimas atualizações | 7 |
| Painel de indicadores (dashboard textual) | 8 |
| Ver a organização bairro → categoria → ocorrências | 9 |

---

## 📁 Estrutura de pastas

```text
GLOBAL-SOLUTION-1/
├── README.md              ← este arquivo
├── src/
│   └── sistema.py         ← o programa
├── data/
│   ├── ocorrencias.csv    ← 13 registros (12 válidos + 1 com erro proposital)
│   └── historico.csv      ← 10 atualizações de status
└── docs/
    └── uso_ia.md          ← como a IA apoiou o desenvolvimento
```

---

## 🗂️ Formato dos dados

Os registros ficam em arquivos de texto com campos separados por `;`. Usamos ponto e vírgula porque a descrição pode conter vírgulas.

### `data/ocorrencias.csv`

```text
id;categoria;descricao;local;dia_abertura;status;dia_conclusao
001;iluminacao;Poste apagado há três noites;Rua residencial transversal;2;aberta;
```

| Campo | Exemplo | Obrigatório |
| --- | --- | --- |
| `id` | `001` | Sim, e único |
| `categoria` | `iluminacao` | Sim |
| `descricao` | Poste apagado há três noites | Sim |
| `local` | Rua residencial transversal | Sim, sempre genérico |
| `dia_abertura` | `2` (dia simulado) | Sim |
| `status` | `aberta` | Sim |
| `dia_conclusao` | `9` | Só quando o status é `concluida` |

As datas são **dias simulados** (dia 1, dia 2…), e não datas reais. Assim o cálculo do tempo de atendimento é uma subtração simples. O "dia de hoje" da simulação é o **dia 15**.

### `data/historico.csv`

```text
dia;id;status_anterior;status_novo
4;003;aberta;em_analise
```

### Valores padronizados

**Categorias:** `iluminacao`, `acessibilidade`, `limpeza`, `conservacao`.

**Status:**

| Status | Significado |
| --- | --- |
| `aberta` | Registrada e ainda não examinada |
| `em_analise` | Em avaliação ou em resolução |
| `concluida` | Resolvida |

O único caminho permitido é **aberta → em_analise → concluida**. Não é possível pular etapas nem voltar.

### Registro inconsistente

A linha 14 do arquivo (código `013`) foi criada **sem categoria**, de propósito. Ao iniciar, o sistema detecta o erro, avisa quais registros foram ignorados e por quê, e não deixa o registro entrar nos indicadores:

```text
Atenção: 1 registro(s) do arquivo foram ignorados:
  - Linha 14 (código 013): categoria ausente ou inválida.
  Corrija o arquivo data/ocorrencias.csv para incluí-los.
```

O código `013` fica **reservado**. Por isso, a próxima ocorrência cadastrada recebe o `014`, e não existe risco de dois registros terem o mesmo número quando o arquivo for corrigido.

---

## 🧱 Estruturas de dados e justificativa

| Estrutura | Como foi usada | Por que esta escolha |
| --- | --- | --- |
| **Lista** | `ocorrencias`: todas as ocorrências válidas | Mantém a ordem do arquivo e permite percorrer tudo, na listagem, no filtro e nos indicadores |
| **Dicionário** | `indice`: código → ocorrência | Busca direta pelo código, sem percorrer a lista inteira |
| **Fila (FIFO)** | `fila`: códigos das ocorrências `aberta`, da mais antiga para a mais nova | Justiça no atendimento: quem registrou primeiro é examinado primeiro. Uma ocorrência nova entra no **fim** e a opção 5 retira do **início** |
| **Pilha (LIFO)** | `pilha`: eventos do histórico, com o mais recente no topo | Responde "o que mudou por último?". A opção 7 lê do topo para baixo, sem retirar nada |
| **Hierarquia** (dicionário dentro de dicionário) | `hierarquia[bairro][categoria]` → lista de códigos | Organiza as informações como as pessoas pensam: "quais problemas de limpeza existem nos Jardins?" |
| **Matriz** (lista de listas) | `matriz[categoria][status]`: 4 linhas × 3 colunas | Uma única tabela de contagens que serve de base para todos os indicadores: soma da linha = total da categoria, soma da coluna = total do status |

A fila é montada já **ordenada pelo dia de abertura**, usando ordenação por inserção feita à mão (função `montar_fila`).

---

## ⚙️ Regras lógicas

### Validação de cadastro (`validar_ocorrencia`)

Cada condição é um `if` **separado**, sem `elif`. Isso é proposital: queremos mostrar **todos** os erros de uma vez, e não só o primeiro.

| Condição | Operador | Mensagem |
| --- | --- | --- |
| `codigo == "" or codigo in indice` | `OR` | código vazio ou repetido |
| `not (categoria in CATEGORIAS)` | `NOT` | categoria ausente ou inválida |
| `descricao == "" or local == ""` | `OR` | descrição ou local ausente |
| `status == "concluida" and (not eh_numero(dia_conclusao) or conclusao < abertura)` | `AND`, `OR`, `NOT` | conclusão ausente ou anterior à abertura |

### Consulta e filtro (`buscar`, `filtrar`)

- A busca usa o **dicionário**: `if codigo in indice` mostra a ocorrência, e o `else` mostra "não encontrada".
- O filtro deixa a pessoa usar só a categoria, só o status, ou os dois. Um campo deixado em branco significa "qualquer valor":

```python
(categoria == "" or oc["categoria"] == categoria) and (status == "" or oc["status"] == status)
```

### Atualização de status (`atualizar_status`)

Aqui os casos **se excluem**, por isso usamos `if / elif / else`. Só um caminho é seguido:

```python
if codigo not in indice:              # 1. não existe       → "não encontrada"
elif novo not in STATUS:              # 2. status estranho  → "status desconhecido"
elif not mudanca_permitida(...):      # 3. pulou etapa      → "não é possível passar de..."
else:                                 # 4. tudo certo       → atualiza, histórico e pilha
```

### Expressão booleana documentada

A regra central do sistema é a função `mudanca_permitida`:

```python
(atual == "aberta" and novo == "em_analise") or (atual == "em_analise" and novo == "concluida")
```

**Como ler:** a mudança é permitida **se** a ocorrência está aberta **e** vai para análise, **ou se** está em análise **e** vai para concluída. Qualquer outra combinação dá `False`: aberta → concluída, concluída → aberta, ou repetir o mesmo status.

**Por que essa regra produz cada mensagem:**
- `aberta → em_analise`: o primeiro parêntese é `True`, a expressão é `True`, o status muda e o evento vai para o histórico.
- `aberta → concluida`: os dois parênteses são `False`, a expressão é `False`, e aparece "Não é possível passar de Aberta para Concluída".
- `concluida → qualquer status`: nenhum parêntese começa com `concluida`, então o resultado é `False`. Uma ocorrência concluída não pode ser reaberta.

### Menu

O menu é uma cadeia `if / elif / ... / else`. Qualquer opção diferente de 0 a 9 cai no `else`: "Opção inválida. Digite um número de 0 a 9."

---

## 📊 Indicadores

### Fórmulas

| Indicador | Regra de cálculo |
| --- | --- |
| Total por categoria | Soma da linha da matriz |
| % por categoria | quantidade ÷ total × 100 |
| Total por status | Soma da coluna da matriz |
| % por status | quantidade ÷ total × 100 |
| Pendências | abertas + em análise |
| **Tempo médio até a conclusão** | soma de (dia_conclusao − dia_abertura) ÷ número de concluídas |

### Resultado com os dados de origem

```text
==================================================================
  PAINEL DE INDICADORES - JARDINS (dados fictícios, dia 15)
==================================================================
Total de ocorrências: 12   Pendências: 9   Concluídas: 3

POR CATEGORIA           qtd       %
  Iluminação            3   25,0%  ███
  Acessibilidade        3   25,0%  ███
  Limpeza               3   25,0%  ███
  Conservação           3   25,0%  ███

POR STATUS              qtd       %
  Aberta                5   41,7%  █████
  Em análise            4   33,3%  ████
  Concluída             3   25,0%  ███

MATRIZ CATEGORIA x STATUS
                       Aberta  Em análise  Concluída
  Iluminação                2           1          0
  Acessibilidade            1           1          1
  Limpeza                   1           1          1
  Conservação               1           1          1

TEMPO MÉDIO ATÉ A CONCLUSÃO
  5,7 dias
  Fórmula: soma(dia_conclusao - dia_abertura) / nº de concluídas = 17 / 3
```

Cálculo do tempo médio, passo a passo: 002 (6 − 1 = 5), 004 (9 − 2 = 7) e 007 (11 − 6 = 5). A soma dá 17, e 17 ÷ 3 = 5,7 dias.

### Interpretação

As quatro categorias têm o mesmo número de registros (3 cada), mas **o andamento é diferente**. **Iluminação** é a única categoria sem nenhuma ocorrência concluída e tem 3 pendências. No conjunto simulado, ela é a necessidade mais urgente do bairro. Além disso, **75% das ocorrências ainda estão pendentes**, o que indica uma fila de atendimento acumulada.

Como os dados são fictícios, essas conclusões valem **só para o cenário de teste**. Elas mostram que o sistema funciona, e não a situação real dos Jardins.

---

## 🔧 Como executar o código

**Pré-requisito:** Python 3 (testado no 3.13). Não é preciso instalar nenhuma biblioteca, porque o sistema usa só Python básico e o módulo `os`, que já vem com o Python.

```bash
# 1. Clonar o repositório
git clone https://github.com/cc-fiap-labs/FIAP-PORTFOLIO-1CCON.git

# 2. Entrar na pasta da entrega
cd FIAP-PORTFOLIO-1CCON/1CC-AGO/1CCOS/GLOBAL-SOLUTION-1

# 3. Executar
python src/sistema.py
```

No macOS e no Linux, use `python3 src/sistema.py`.

O programa encontra os arquivos de dados a partir da pasta onde ele está. Por isso também funciona se for executado por uma IDE, como o PyCharm ou o VS Code.

---

## 💻 Exemplo de uso

O exemplo abaixo reproduz o cenário do enunciado. A saída veio do terminal, resumida: o menu e as listas de opções não aparecem para o texto ficar curto.

**1. Consultar as ocorrências abertas de iluminação** (opção 3 → categoria 1 → status 1)

```text
RESULTADO DO FILTRO (2)
CÓDIGO  CATEGORIA       LOCAL                                STATUS
----------------------------------------------------------------------
001     Iluminação      Rua residencial transversal          Aberta
009     Iluminação      Ciclofaixa                           Aberta
```

**2. Cadastrar uma nova demanda** (opção 4)

```text
NOVA OCORRÊNCIA (não informe nomes, telefones ou endereços com número)
Categoria: 1
Descrição breve: Poste com fiação exposta
Local genérico (ex.: Praça arborizada): Praça arborizada

Ocorrência 014 cadastrada com status Aberta. Ela entrou no fim da fila de análise.
```

**3. Alterar a ocorrência 014 para "em análise"** (opção 6)

```text
Código da ocorrência: 014
Status atual: Aberta
Novo status: 2

Ocorrência 014: Aberta -> Em análise. Registrado no histórico.
```

**4. Ver as últimas atualizações** (opção 7: a pilha, do topo para baixo)

```text
ÚLTIMAS ATUALIZAÇÕES (da mais recente para a mais antiga)
  Dia 15 | 014 | Aberta -> Em análise
  Dia 12 | 010 | Aberta -> Em análise
  Dia 11 | 007 | Em análise -> Concluída
  Dia  9 | 008 | Aberta -> Em análise
  Dia  9 | 004 | Em análise -> Concluída
```

**5. Tentar pular uma etapa** (opção 6: código 001 → Concluída)

```text
Não é possível passar de Aberta para Concluída.
Caminho permitido: Aberta -> Em análise -> Concluída.
```

**6. Sair** (opção 0)

```text
Até logo! (As alterações desta sessão ficam só na memória.)
```

---

## ♿ Acessibilidade, inclusão e privacidade

**Acessibilidade e inclusão**
- O menu é numerado e tem frases curtas, sem siglas ou termos técnicos.
- Categoria e status podem ser escolhidos **pelo número** ou **pelo nome**, com ou sem acento: "Iluminação", "iluminacao" ou "1".
- Toda mensagem de erro diz **o que aconteceu e o que fazer**, por exemplo: "Ocorrência 099 não encontrada. Confira o número e tente de novo."
- A interface é só texto: funciona em qualquer computador, sem internet, e pode ser lida por leitores de tela.
- Acessibilidade é uma das quatro categorias acompanhadas, o que dá visibilidade a barreiras como calçadas quebradas e falta de rampas.

**Privacidade**
- Nenhum dado pessoal é coletado: não há nome, telefone nem endereço com número.
- Os locais são sempre **genéricos** ("Praça arborizada", "Ciclofaixa").
- Na tela de cadastro há um aviso: "não informe nomes, telefones ou endereços com número".

**Responsabilidade**
- O sistema **não se conecta à prefeitura** e não promete atendimento. Ele organiza informações para a comunidade acompanhar.
- O README e a tela inicial deixam claro que os dados são fictícios.

---

## 📎 Links e observações

### 🔗 Links do projeto

* **[Vídeo de apresentação no YouTube](https://www.youtube.com/)** - substituir pelo link do vídeo "Não listado".

### 🧠 Decisões técnicas

> - **Python básico, sem bibliotecas externas:** segue a regra do enunciado de usar só conteúdos das fases 1 a 3, e permite rodar em qualquer máquina.
> - **Arquivo `.csv` com `;`:** é fácil de editar em qualquer editor de texto e não conflita com vírgulas nas descrições.
> - **Dias simulados em vez de datas reais:** o tempo de atendimento vira uma subtração simples.
> - **Alterações só em memória:** cada execução começa do mesmo ponto, o que garante uma demonstração previsível.
> - **Uso de IA:** documentado em [`docs/uso_ia.md`](docs/uso_ia.md).

### 📢 Observações gerais

* **Participação na competição:** [ ] Sim, aceitamos participar / [ ] Não vamos participar.

---

## 🧭 Conclusões, limitações e aprendizados

**Conclusões**
O protótipo cumpre o ciclo completo de uma demanda comunitária: registrar, organizar, acompanhar e resumir em indicadores. Com poucas estruturas de dados (lista, dicionário, fila, pilha, hierarquia e matriz), relatos soltos viram informação útil. No cenário simulado, por exemplo, iluminação aparece como prioridade.

**Limitações**
- Os dados são fictícios e o volume é pequeno (12 ocorrências). Os indicadores não representam a realidade do bairro.
- Cadastros e mudanças feitos durante o uso **não são salvos** no arquivo ao sair.
- Não há login: qualquer pessoa pode alterar um status. Uma versão real precisaria de controle de acesso.
- Não há integração com órgãos públicos, nem notificação a quem registrou.

**Aprendizados**
- Escolher a estrutura de dados certa simplifica o código. O dicionário evita percorrer a lista em cada busca, e a matriz centraliza todos os totais.
- `if` separados e `if / elif / else` servem para coisas diferentes: os separados juntam todos os erros, e o `elif` escolhe um único caminho.
- Validar os dados logo na entrada impede que um registro inconsistente distorça os indicadores.

---

## 📋 Licença

Projeto acadêmico desenvolvido para a Global Solution da FIAP.
