# Uso de Inteligência Artificial

Este arquivo registra, como pede o enunciado, como a IA apoiou o desenvolvimento e como a equipe **cc-fiap-labs** verificou os resultados.

## Ferramenta utilizada

- **Claude (Anthropic)**, usado em conversa (chat).

## Como a IA apoiou

| Etapa | O que a IA fez | O que a equipe fez |
| --- | --- | --- |
| Planejamento | Sugeriu as etapas, os campos da ocorrência e quais estruturas de dados usar em cada parte | Escolheu o bairro (Jardins), os status e o nome da equipe |
| Pseudocódigo | Analisou o pseudocódigo feito pela equipe | Fez o pseudocódigo |
| Dados fictícios | Analisou as  as 12 ocorrências, o registro com erro proposital e o histórico | Criou as 12 ocorrências |
| Código | Revisou o código feito pela equipe | Pelo pseudocódigo, fez o 'sistema.py', analisando cada função, executou e pediu ajustes (ex.: trocar uma sequência de `if` por `if / elif / else` em `atualizar_status`) |
| Documentação | Ajudou a redigir este README | Revisou o texto e completou RMs, tutor e link do vídeo |

## Como os resultados foram verificados

1. **Execução do programa:** o sistema foi rodado no terminal (`python3 src/sistema.py`).
2. **Cenário do enunciado:** filtro de iluminação + aberta, cadastro da ocorrência 014, mudança da 014 para "em análise" e atualização do painel. Funcionou como esperado.
3. **Casos de erro:** código inexistente (099), cadastro sem campos, mudança que pula etapa (aberta → concluída) e opção de menu inválida. Todos mostram mensagem clara e não alteram os dados.
4. **Indicadores conferidos à mão:** 12 ocorrências (5 abertas, 4 em análise, 3 concluídas) e tempo médio de (5 + 7 + 5) ÷ 3 = 5,7 dias. O valor bate com o painel.
5. **Registro inconsistente:** a linha com o código 013, sem categoria, é recusada ao carregar, com aviso na tela.

## Responsabilidade

A equipe entende o código entregue e é responsável por ele. Todos os integrantes leram as funções acompanhando o pseudocódigo e conseguem explicar as estruturas de dados, as regras lógicas e os indicadores.
