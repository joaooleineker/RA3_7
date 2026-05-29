# Fase 3 - Analisador Semântico

## Informações do Projeto

* **Instituição:** PUCPR - Pontifícia Universidade Católica do Paraná
* **Ano:** 2026 - 1º Semestre
* **Disciplina:** Linguagens Formais e Compiladores
* **Professor:** Frank Coelho de Alcantara
* **Grupo:** RA3\_7
* **Linguagem de implementação:** Python 3

## Integrantes do Grupo

* Daniel de Almeida Santos Bina - `danielbina`
* Eduardo Ferreira de Melo - `edufmelo`
* João Eduardo Faccin Leineker - `joaooleineker`

## Objetivo

Este projeto implementa a terceira fase do trabalho da disciplina de Linguagens Formais e Compiladores: o **analisador semântico**.

A Fase 3 reaproveita os analisadores desenvolvidos nas fases anteriores:

1. **Analisador léxico:** identifica os tokens do programa-fonte.
2. **Analisador sintático:** verifica a estrutura gramatical e gera a árvore sintática.
3. **Analisador semântico:** verifica se o programa faz sentido semanticamente, validando variáveis, tipos, comandos especiais, estruturas de controle e gerando a árvore sintática atribuída.

O analisador também prepara as informações necessárias para a geração de código Assembly compatível com o ambiente **Cpulator-ARMv7 DEC1-SOC(v16.1)**.

## Como Executar

O programa deve ser executado pela linha de comando, passando o arquivo de teste como argumento.

Exemplo:

```bash
python semantico.py teste1.txt
```

Também é possível executar com outros arquivos de teste:

```bash
python semantico.py teste2.txt
python semantico.py teste3.txt
```

Não há menu interativo. Todo o processamento depende do arquivo informado como argumento.

## Como Executar os Testes

Os testes foram separados por fase do analisador.

### Testes do léxico

```bash
python funcoesTesteLexico.py
```

### Testes do sintático

```bash
python funcoesTesteSintatico.py
```

### Testes do semântico

```bash
python funcoesTesteSemantico.py
```

Os testes semânticos validam casos envolvendo literais, operações aritméticas, divisão inteira, resto, operadores relacionais, variáveis, comandos especiais, estruturas de controle e incompatibilidades de tipos.

## Fluxo Geral do Compilador

O fluxo completo do programa é:

```text
arquivo .txt
   ↓
analisador léxico
   ↓
tokens.txt
   ↓
analisador sintático
   ↓
arvore_sintatica.md / arvore_sintatica.json
   ↓
analisador semântico
   ↓
tabela_simbolos.md
   ↓
relatorio_tipos.md
   ↓
erros_semanticos.md
   ↓
arvore_atribuida.md / arvore_atribuida.json
   ↓
código Assembly (.s)
```

A função principal da Fase 3 é `executarAnaliseSemantica(nome_arquivo)`, que coordena a execução do analisador semântico.

De forma resumida, o programa executa as seguintes etapas:

1. Lê o arquivo de entrada.
2. Gera os tokens com o analisador léxico.
3. Verifica se o programa começa com `(START)` e termina com `(END)`.
4. Aciona o analisador sintático.
5. Gera a árvore sintática inicial.
6. Verifica se existem erros léxicos ou sintáticos antes da análise semântica.
7. Decora a árvore com números de linha.
8. Constrói a tabela de símbolos.
9. Verifica os tipos das expressões.
10. Gera a árvore sintática atribuída.
11. Gera o código Assembly (apenas se não houver erros).
12. Salva os artefatos finais da execução.

## Descrição da Linguagem

A linguagem utiliza expressões em notação pós-fixada, também chamada de RPN (*Reverse Polish Notation*).

Cada comando deve ser delimitado por parênteses.

Exemplo de soma:

```text
(3.14 2.0 +)
```

Neste exemplo, os operandos `3.14` e `2.0` aparecem antes do operador `+`.

A partir da Fase 3, o arquivo passa a representar um programa completo. Portanto, todo programa deve começar com:

```text
(START)
```

e terminar com:

```text
(END)
```

Exemplo de programa válido:

```text
(START)
(3.14 2.0 +)
(5.0 VAR)
(VAR)
(END)
```

## Comentários

A linguagem aceita comentários iniciados por `*{` e finalizados por `}*`.

Os comentários são reconhecidos pelo analisador léxico e descartados antes da geração do vetor de tokens utilizado pelo analisador sintático.

Exemplo de comentário em linha inteira:

```text
*{ comentario em linha inteira }*
```

Exemplo de comentário no final de uma linha:

```text
(5.0 VAR) *{ comentario no final }*
```

Exemplo de comentário entre elementos de uma expressão:

```text
(10.0 *{ comentario no meio }* MEM)
```

Os comentários não aparecem no arquivo `tokens.txt`.

## Operações Suportadas

A linguagem suporta operações aritméticas, relacionais, comandos especiais e estruturas de controle.

### Operadores aritméticos

| Operador | Descrição        |
| -------- | ---------------- |
| `+`      | Soma             |
| `-`      | Subtração        |
| `*`      | Multiplicação    |
| `\|`     | Divisão real     |
| `/`      | Divisão inteira  |
| `%`      | Resto da divisão |
| `^`      | Potenciação      |

Exemplos:

```text
(3 2 +)
(10 3 -)
(10 3 /)
(10 3 %)
(2 8 ^)
(10.0 3.0 |)
```

### Operadores relacionais

| Operador | Descrição      |
| -------- | -------------- |
| `<`      | Menor que      |
| `>`      | Maior que      |
| `<=`     | Menor ou igual |
| `>=`     | Maior ou igual |
| `==`     | Igual          |
| `!=`     | Diferente      |

Exemplo:

```text
(VAR 10.0 <)
```

Operadores relacionais retornam o tipo `bool`.

## Tipos Suportados

A linguagem trabalha com três tipos principais:

| Tipo      | Descrição                                                |
| --------- | -------------------------------------------------------- |
| `inteiro` | Números sem ponto decimal, como `3`, `10`, `25`          |
| `real`    | Números com ponto decimal, como `3.14`, `2.0`, `10.5`    |
| `bool`    | Resultado de expressões relacionais, como `(VAR 10.0 <)` |

Não existem literais booleanos explícitos na linguagem. O tipo `bool` é produzido exclusivamente por operadores relacionais.

Exemplos:

```text
(10 3 /)       *{ resultado inteiro }*
(3.14 2.0 +)   *{ resultado real }*
(VAR 10.0 <)   *{ resultado bool }*
```

## Regras de Tipos

As regras de tipos estão documentadas em dois arquivos:

* `regras_tipos.md` — sistema de tipos em cálculo de sequentes.
* `gramatica.md` — gramática atribuída em EBNF com as regras semânticas de cada produção.

Resumo das principais regras:

* Números sem ponto decimal são inferidos como `inteiro`.
* Números com ponto decimal são inferidos como `real`.
* Operadores relacionais produzem `bool`.
* Os operadores `/` e `%` exigem operandos `inteiro`.
* O operador `|` representa divisão real e produz `real`.
* Os operadores `+`, `-`, `*` e `^` aceitam operandos numéricos; `int + int → int`, qualquer `real → real`.
* Operações aritméticas não aceitam operandos do tipo `bool`.
* Condições de `IF` e `WHILE` devem produzir `bool`.
* Variáveis possuem tipo estático e forte após sua primeira definição.

## Variáveis e Memória

Variáveis são representadas por identificadores em letras maiúsculas, como:

```text
VAR
MEM
RESULTADO
CONTADOR
```

A definição de uma variável ocorre quando um valor é armazenado em uma memória.

Exemplo:

```text
(5.0 VAR)
```

Nesse caso, o valor `5.0` é armazenado em `VAR`, e a variável passa a ter tipo `real`.

O uso de uma variável ocorre quando ela aparece sozinha ou dentro de uma expressão.

Exemplo:

```text
(VAR)
```

ou:

```text
(VAR 10.0 <)
```

O analisador semântico verifica se a variável foi definida antes de ser usada.

Exemplo inválido:

```text
(START)
(VAR)
(END)
```

Nesse caso, `VAR` foi usada antes de receber um valor.

## Comando RES

O comando `RES` permite acessar resultados anteriores do histórico de expressões.

Sintaxe:

```text
(N RES)
```

em que `N` deve ser um inteiro positivo.

Exemplo:

```text
(START)
(3.14 2.0 +)
(10.0 2.0 *)
(1 RES)
(END)
```

Nesse exemplo, `(1 RES)` retorna o último resultado armazenado no histórico.

O analisador semântico valida se:

* `N` é do tipo `inteiro`;
* `N` é positivo;
* existe resultado anterior suficiente no histórico.

## Estruturas de Controle

A linguagem suporta decisão e repetição em notação pós-fixada.

### WHILE

A estrutura `WHILE` executa um corpo enquanto a condição for verdadeira.

Exemplo:

```text
((VAR 10.0 <) ((VAR 1.0 +) VAR) WHILE)
```

A condição `(VAR 10.0 <)` deve produzir um valor do tipo `bool`.

### IF

A estrutura `IF` representa uma tomada de decisão com bloco `then` e bloco `else`.

Exemplo:

```text
((VAR 5.0 >) (1.0 RESULTADO) (0.0 RESULTADO) IF)
```

A condição `(VAR 5.0 >)` deve produzir um valor do tipo `bool`.

O analisador semântico valida se as condições usadas em `IF` e `WHILE` são expressões lógicas.

## Tabela de Símbolos

A tabela de símbolos registra as variáveis identificadas durante a análise semântica.

O arquivo gerado é:

```text
tabela_simbolos.md
```

Cada entrada contém:

| Campo            | Descrição                                |
| ---------------- | ---------------------------------------- |
| Nome             | Nome da variável                         |
| Tipo             | Tipo inferido da variável                |
| Escopo           | Escopo da variável                       |
| Linha Definição  | Linha em que a variável foi definida     |
| Linha Último Uso | Última linha em que a variável foi usada |

Exemplo de tabela:

```text
| Nome      | Tipo | Escopo | Linha Definição | Linha Último Uso |
|-----------|------|--------|-----------------|------------------|
| VAR       | real | global | 8               | 12               |
| MEM       | real | global | 13              | 15               |
| RESULTADO | real | global | 11              | 11               |
```

## Verificação Semântica

O analisador semântico realiza validações que não são responsabilidade do léxico nem do sintático.

Entre elas:

* uso de variável antes da definição;
* redefinição de variável com tipo incompatível;
* uso incorreto do comando `RES`;
* operações aritméticas com tipos incompatíveis;
* uso de `bool` em operação aritmética;
* divisão inteira e resto com operandos não inteiros;
* condição de `IF` ou `WHILE` sem tipo `bool`.

Quando erros são encontrados, eles são reportados antes da geração da árvore atribuída e do código Assembly.

## Relatórios de Erros

Os relatórios gerados são:

```text
erros_semanticos.md
relatorio_tipos.md
```

O arquivo `erros_semanticos.md` registra erros semânticos gerais, como uso de variável antes da definição, redefinição incompatível e erro no uso de `RES`.

O arquivo `relatorio_tipos.md` registra erros de tipos, como operações incompatíveis e condições inválidas em estruturas de controle.

Exemplo de erro semântico:

```text
Linha 2 | Variável VAR | Variável 'VAR' usada antes de ser definida.
```

Exemplo de erro de tipo:

```text
Linha 3 | Condição do WHILE deve ser do tipo 'bool', mas é 'real'.
```

## Árvore Sintática Atribuída

A árvore sintática atribuída é uma versão aumentada da árvore sintática gerada pelo analisador sintático.

Ela adiciona informações semânticas aos nós da árvore, como:

* tipo inferido;
* categoria semântica;
* linha do código-fonte;
* informação auxiliar para geração de Assembly.

Os arquivos gerados são:

```text
arvore_atribuida.md
arvore_atribuida.json
```

Exemplo de anotação na árvore atribuída:

```text
NUMERO (3.14) [tipo: real, cat: literal]
OPERADOR (+) [tipo: real, cat: operador_aritmetico]
MEMORIA (VAR) [tipo: real, cat: var_store]
MEMORIA (VAR) [tipo: real, cat: var_load]
```

Categorias semânticas utilizadas:

| Categoria             | Descrição                                                 |
| --------------------- | --------------------------------------------------------- |
| `literal`             | Valor numérico literal                                    |
| `operador_aritmetico` | Operador aritmético                                       |
| `operador_relacional` | Operador relacional                                       |
| `var_store`           | Armazenamento em variável                                 |
| `var_load`            | Leitura de variável                                       |
| `historico_res`       | Acesso a resultado anterior com `RES`                     |
| `controle`            | Comando de controle: `START`, `END`, `IF`, `WHILE`        |
| `pontuacao`           | Elementos estruturais, como parênteses e ε                |

## Geração de Assembly

O código Assembly é gerado apenas quando o programa não possui erros léxicos, sintáticos ou semânticos.

A geração utiliza as informações da árvore sintática atribuída, como tipos inferidos, categorias semânticas e informações auxiliares de cada nó.

O Assembly produzido é compatível com o ambiente:

```text
Cpulator-ARMv7 DEC1-SOC(v16.1)
```

## Arquivos Gerados

Durante a execução, o analisador pode gerar os seguintes arquivos:

| Arquivo                 | Descrição                                              |
| ----------------------- | ------------------------------------------------------ |
| `tokens.txt`            | Lista de tokens gerada pelo analisador léxico          |
| `arvore_sintatica.md`   | Representação textual da árvore sintática              |
| `arvore_sintatica.json` | Árvore sintática em formato JSON                       |
| `tabela_simbolos.md`    | Tabela de símbolos produzida pelo analisador semântico |
| `erros_semanticos.md`   | Relatório de erros semânticos                          |
| `relatorio_tipos.md`    | Relatório de erros de tipos                            |
| `arvore_atribuida.md`   | Representação textual da árvore sintática atribuída    |
| `arvore_atribuida.json` | Árvore sintática atribuída em formato JSON             |
| `.s`                    | Código Assembly gerado para o programa analisado       |

## Documentação do Projeto

| Arquivo          | Descrição                                                          |
| ---------------- | ------------------------------------------------------------------ |
| `gramatica.md`   | Gramática atribuída em formato EBNF com regras semânticas          |
| `regras_tipos.md`| Sistema de regras de tipos em cálculo de sequentes                 |

## Arquivos do Projeto

| Arquivo                    | Descrição                                   |
| -------------------------- | ------------------------------------------- |
| `lexico.py`                | Implementação do analisador léxico          |
| `sintatico.py`             | Implementação do analisador sintático LL(1) |
| `semantico.py`             | Implementação do analisador semântico       |
| `funcoesTesteLexico.py`    | Testes do analisador léxico                 |
| `funcoesTesteSintatico.py` | Testes do analisador sintático              |
| `funcoesTesteSemantico.py` | Testes do analisador semântico              |
| `teste1.txt`               | Arquivo de teste com programa válido        |
| `teste2.txt`               | Arquivo de teste com programa válido        |
| `teste3.txt`               | Arquivo de teste com erros semânticos       |
| `teste_invalido.txt`       | Arquivo de teste com erro léxico intencional |
| `teste_sintatico.txt`      | Arquivo de teste com erro sintático intencional |

## Exemplo de Programa Semanticamente Válido

```text
(START)
(3.14 2.0 +)
(10 3 /)
(10 3 %)
(2.0 8 ^)
(5.0 VAR)
(VAR)
((VAR 10.0 <) ((VAR 1.0 +) VAR) WHILE)
((VAR 5.0 >) (1.0 RESULTADO) (0.0 RESULTADO) IF)
(END)
```

Esse programa é válido porque:

* começa com `(START)`;
* termina com `(END)`;
* define `VAR` antes de usá-la;
* usa operadores aritméticos com tipos compatíveis;
* usa condições relacionais em `WHILE` e `IF`;
* armazena valores em variáveis com tipos compatíveis.

## Exemplo de Programa Semanticamente Inválido

```text
(START)
(VAR)
(END)
```

Esse programa é inválido porque `VAR` é usada antes de ser definida.

Outro exemplo inválido:

```text
(START)
(3.5 2 /)
(END)
```

Esse programa é inválido porque `/` representa divisão inteira e exige operandos do tipo `inteiro`, mas `3.5` é do tipo `real`.

Outro exemplo inválido:

```text
(START)
(5.0 VAR)
((VAR) (1.0 RESULTADO) (0.0 RESULTADO) IF)
(END)
```

Esse programa é inválido porque a condição do `IF` deve produzir `bool`, mas `(VAR)` produz `real`.

## Última Execução

Os artefatos finais disponíveis no repositório correspondem à última execução do analisador semântico.

Para reproduzir a última execução:

```bash
python semantico.py teste1.txt
```

Arquivos gerados nessa execução:

```text
tokens.txt
arvore_sintatica.md
arvore_sintatica.json
tabela_simbolos.md
erros_semanticos.md
relatorio_tipos.md
arvore_atribuida.md
arvore_atribuida.json
teste1.s
```

## Organização e Rastreabilidade

O repositório foi organizado com separação entre as etapas do compilador:

* análise léxica;
* análise sintática;
* análise semântica;
* documentação;
* testes;
* artefatos gerados.

As contribuições dos integrantes estão registradas por meio de commits claros e pull requests, mantendo a rastreabilidade do desenvolvimento.
