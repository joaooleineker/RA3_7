# Gramática Atribuída — Formato EBNF

Este documento descreve a gramática atribuída da linguagem implementada pelo grupo, escrita em formato EBNF com as regras semânticas associadas a cada produção.

**Convenções:**
- Não-terminais são escritos em letras minúsculas: `programa`, `comando`, etc.
- Terminais são escritos em letras maiúsculas: `NUMERO`, `OPERADOR`, `MEMORIA`, etc.
- `ε` representa a produção vazia.
- Atributos semânticos são indicados entre colchetes após cada produção: `{ ação semântica }`.

---

## Terminais da Linguagem

| Terminal        | Descrição                                              | Exemplos                        |
| --------------- | ------------------------------------------------------ | ------------------------------- |
| `ABRE_PAREN`    | Parêntese de abertura                                  | `(`                             |
| `FECHA_PAREN`   | Parêntese de fechamento                                | `)`                             |
| `NUMERO`        | Literal numérico inteiro ou real                       | `3`, `10`, `3.14`, `2.0`        |
| `OPERADOR`      | Operador aritmético                                    | `+`, `-`, `*`, `\|`, `/`, `%`, `^` |
| `OPERADOR_REL`  | Operador relacional                                    | `<`, `>`, `<=`, `>=`, `==`, `!=` |
| `MEMORIA`       | Identificador de variável (letras maiúsculas)          | `VAR`, `CONTADOR`, `RESULTADO`  |
| `KEYWORD_START` | Marcador de início de programa                         | `START`                         |
| `KEYWORD_END`   | Marcador de fim de programa                            | `END`                           |
| `KEYWORD_RES`   | Operador de acesso ao histórico de resultados          | `RES`                           |
| `KEYWORD_IF`    | Operador de decisão                                    | `IF`                            |
| `KEYWORD_WHILE` | Operador de repetição                                  | `WHILE`                         |

---

## Regras de Produção

### programa

```ebnf
programa ::= comando_lista
```

**Regra semântica:**
```
{ programa.tipo := void }
```

---

### comando_lista

```ebnf
comando_lista ::= comando comando_lista
               | ε
```

**Regras semânticas:**
```
comando_lista → comando comando_lista
{ comando_lista.historico := comando_lista_2.historico após processar comando }

comando_lista → ε
{ comando_lista.historico := [] }
```

---

### comando

```ebnf
comando ::= ABRE_PAREN conteudo_comando FECHA_PAREN
```

**Regra semântica:**
```
{ comando.tipo    := conteudo_comando.tipo
  comando.linha   := token_atual.linha }
```

---

### conteudo_comando

```ebnf
conteudo_comando ::= KEYWORD_START
                   | KEYWORD_END
                   | NUMERO sufixo_numero
                   | MEMORIA sufixo_memoria
                   | comando sufixo_comando
```

**Regras semânticas:**

```
conteudo_comando → KEYWORD_START
{ conteudo_comando.tipo := void
  conteudo_comando.categoria := "controle" }

conteudo_comando → KEYWORD_END
{ conteudo_comando.tipo := void
  conteudo_comando.categoria := "controle" }

conteudo_comando → NUMERO sufixo_numero
{ NUMERO.tipo_inferido := inferirTipoNumero(NUMERO.valor)
    — se NUMERO.valor contém '.': tipo = real
    — caso contrário:             tipo = inteiro
  conteudo_comando.tipo := sufixo_numero.tipo_resultado
  conteudo_comando.categoria := sufixo_numero.categoria }

conteudo_comando → MEMORIA sufixo_memoria
{ se sufixo_memoria = ε:
    — LOAD: verificar se MEMORIA está na tabela de símbolos
    — se não estiver: ERRO SEMÂNTICO — variável usada antes de definição
    — se estiver:     MEMORIA.tipo := tabela[MEMORIA.nome].tipo
  senão:
    — STORE: MEMORIA recebe o tipo do topo da pilha RPN
  conteudo_comando.tipo := MEMORIA.tipo }

conteudo_comando → comando sufixo_comando
{ conteudo_comando.tipo := sufixo_comando.tipo_resultado }
```

---

### sufixo_numero

Aplicado após um `NUMERO` inicial na pilha RPN.

```ebnf
sufixo_numero ::= KEYWORD_RES
                | NUMERO operador_final
                | MEMORIA apos_mem
                | comando operador_final
```

**Regras semânticas:**

```
sufixo_numero → KEYWORD_RES
{ verificar se NUMERO.tipo = inteiro; se não: ERRO SEMÂNTICO
  verificar se NUMERO.valor > 0;       se não: ERRO SEMÂNTICO
  verificar se NUMERO.valor ≤ |historico|; se não: ERRO SEMÂNTICO
  sufixo_numero.tipo_resultado := historico[|historico| - NUMERO.valor].tipo }

sufixo_numero → NUMERO operador_final
{ sufixo_numero.tipo_resultado := inferirTipoOperacao(operador_final.valor,
                                    tipo_a, tipo_b)
  — regras detalhadas na seção de operadores }

sufixo_numero → MEMORIA apos_mem
{ sufixo_numero.tipo_resultado := tipo após operação com MEMORIA }

sufixo_numero → comando operador_final
{ sufixo_numero.tipo_resultado := inferirTipoOperacao(operador_final.valor,
                                    tipo_esquerdo, comando.tipo) }
```

---

### sufixo_memoria

Aplicado após um `MEMORIA` na pilha RPN.

```ebnf
sufixo_memoria ::= NUMERO operador_final
                 | MEMORIA apos_mem
                 | comando operador_final
                 | ε
```

**Regras semânticas:**

```
sufixo_memoria → ε
{ — LOAD: recupera valor de MEMORIA da tabela de símbolos
  — se MEMORIA não declarado: ERRO SEMÂNTICO — variável usada antes de definição }

sufixo_memoria → NUMERO operador_final
{ sufixo_memoria.tipo_resultado := inferirTipoOperacao(operador_final.valor,
                                     MEMORIA.tipo, NUMERO.tipo) }

sufixo_memoria → MEMORIA apos_mem
{ sufixo_memoria.tipo_resultado := tipo resultante após apos_mem }

sufixo_memoria → comando operador_final
{ sufixo_memoria.tipo_resultado := inferirTipoOperacao(operador_final.valor,
                                     MEMORIA.tipo, comando.tipo) }
```

---

### sufixo_comando

Aplicado após um `comando` aninhado na pilha RPN.

```ebnf
sufixo_comando ::= NUMERO operador_final
                 | MEMORIA apos_mem
                 | comando apos_cmd
                 | ε
```

**Regras semânticas:**

```
sufixo_comando → ε
{ — o comando interno é o único valor na pilha: resultado direto
  sufixo_comando.tipo_resultado := comando.tipo }

sufixo_comando → NUMERO operador_final
{ sufixo_comando.tipo_resultado := inferirTipoOperacao(operador_final.valor,
                                     comando.tipo, NUMERO.tipo) }

sufixo_comando → MEMORIA apos_mem
{ sufixo_comando.tipo_resultado := tipo resultante após apos_mem }

sufixo_comando → comando apos_cmd
{ sufixo_comando.tipo_resultado := apos_cmd.tipo_resultado }
```

---

### operador_final

Operador que encerra uma expressão binária.

```ebnf
operador_final ::= OPERADOR
                 | OPERADOR_REL
```

**Regras semânticas:**

```
operador_final → OPERADOR
{ verificar compatibilidade de tipos (ver regras abaixo)
  operador_final.tipo_resultado := inferirTipoOperacao(OPERADOR.valor, tipo_a, tipo_b) }

operador_final → OPERADOR_REL
{ verificar compatibilidade de tipos para comparação
  operador_final.tipo_resultado := bool }
```

---

### apos_mem

Sufixo após um acesso a `MEMORIA` dentro de uma expressão.

```ebnf
apos_mem ::= OPERADOR
           | OPERADOR_REL
           | ε
```

**Regras semânticas:**

```
apos_mem → ε
{ — STORE: MEMORIA recebe o tipo do operando que estava na pilha antes
  — registra na tabela de símbolos com o tipo inferido
  — se já existia com tipo diferente: ERRO SEMÂNTICO — redefinição incompatível }

apos_mem → OPERADOR
{ apos_mem.tipo_resultado := inferirTipoOperacao(OPERADOR.valor, tipo_esq, MEMORIA.tipo) }

apos_mem → OPERADOR_REL
{ apos_mem.tipo_resultado := bool }
```

---

### apos_cmd

Sufixo após um `comando` aninhado, distinguindo operações binárias, `WHILE` e `IF`.

```ebnf
apos_cmd ::= OPERADOR
           | OPERADOR_REL
           | KEYWORD_WHILE
           | comando KEYWORD_IF
```

**Regras semânticas:**

```
apos_cmd → OPERADOR
{ apos_cmd.tipo_resultado := inferirTipoOperacao(OPERADOR.valor,
                               tipo_esquerdo, tipo_direito) }

apos_cmd → OPERADOR_REL
{ apos_cmd.tipo_resultado := bool }

apos_cmd → KEYWORD_WHILE
{ verificar se condicao.tipo = bool
  — se não: ERRO SEMÂNTICO — condição do WHILE deve ser 'bool'
  apos_cmd.tipo_resultado := void }

apos_cmd → comando KEYWORD_IF
{ verificar se condicao.tipo = bool
  — se não: ERRO SEMÂNTICO — condição do IF deve ser 'bool'
  apos_cmd.tipo_resultado := void }
```

---

## Regras de Inferência de Tipos para Operadores

### inferirTipoNumero

```
valor contém '.'  →  tipo = real
valor sem '.'     →  tipo = inteiro
```

### inferirTipoOperacao

| Operador | Tipo A    | Tipo B    | Tipo Resultado | Observação                              |
| -------- | --------- | --------- | -------------- | --------------------------------------- |
| `/`      | inteiro   | inteiro   | inteiro        | divisão inteira                         |
| `/`      | outro     | outro     | —              | ERRO SEMÂNTICO: exige inteiro           |
| `%`      | inteiro   | inteiro   | inteiro        | resto da divisão                        |
| `%`      | outro     | outro     | —              | ERRO SEMÂNTICO: exige inteiro           |
| `\|`     | numérico  | numérico  | real           | divisão real                            |
| `\|`     | bool      | qualquer  | —              | ERRO SEMÂNTICO: bool não permitido      |
| `+`      | inteiro   | inteiro   | inteiro        | promoção: int + int = int               |
| `+`      | numérico  | numérico  | real           | promoção: qualquer real = real          |
| `+`      | bool      | qualquer  | —              | ERRO SEMÂNTICO: bool não permitido      |
| `-`      | inteiro   | inteiro   | inteiro        |                                         |
| `-`      | numérico  | numérico  | real           |                                         |
| `-`      | bool      | qualquer  | —              | ERRO SEMÂNTICO: bool não permitido      |
| `*`      | inteiro   | inteiro   | inteiro        |                                         |
| `*`      | numérico  | numérico  | real           |                                         |
| `*`      | bool      | qualquer  | —              | ERRO SEMÂNTICO: bool não permitido      |
| `^`      | inteiro   | inteiro   | inteiro        | potenciação                             |
| `^`      | numérico  | numérico  | real           |                                         |
| `^`      | bool      | qualquer  | —              | ERRO SEMÂNTICO: bool não permitido      |
| `<`      | numérico  | numérico  | bool           |                                         |
| `<`      | bool      | qualquer  | —              | ERRO SEMÂNTICO: bool não permitido      |
| `>`      | numérico  | numérico  | bool           |                                         |
| `>=`     | numérico  | numérico  | bool           |                                         |
| `<=`     | numérico  | numérico  | bool           |                                         |
| `==`     | T         | T         | bool           | mesmo tipo                              |
| `==`     | numérico  | numérico  | bool           | int e real são compatíveis              |
| `==`     | bool      | não-bool  | —              | ERRO SEMÂNTICO: tipos incompatíveis     |
| `!=`     | T         | T         | bool           | mesmo tipo                              |
| `!=`     | numérico  | numérico  | bool           |                                         |
| `!=`     | bool      | não-bool  | —              | ERRO SEMÂNTICO: tipos incompatíveis     |

---

## Gramática Completa (visão compacta)

```ebnf
programa         ::= comando_lista

comando_lista    ::= comando comando_lista
                   | ε

comando          ::= ABRE_PAREN conteudo_comando FECHA_PAREN

conteudo_comando ::= KEYWORD_START
                   | KEYWORD_END
                   | NUMERO sufixo_numero
                   | MEMORIA sufixo_memoria
                   | comando sufixo_comando

sufixo_numero    ::= KEYWORD_RES
                   | NUMERO operador_final
                   | MEMORIA apos_mem
                   | comando operador_final

sufixo_memoria   ::= NUMERO operador_final
                   | MEMORIA apos_mem
                   | comando operador_final
                   | ε

sufixo_comando   ::= NUMERO operador_final
                   | MEMORIA apos_mem
                   | comando apos_cmd
                   | ε

operador_final   ::= OPERADOR
                   | OPERADOR_REL

apos_mem         ::= OPERADOR
                   | OPERADOR_REL
                   | ε

apos_cmd         ::= OPERADOR
                   | OPERADOR_REL
                   | KEYWORD_WHILE
                   | comando KEYWORD_IF
```

---

## Propriedades da Gramática

- A gramática é **LL(1)**: cada célula da tabela de análise tem no máximo uma produção, sem conflitos FIRST/FOLLOW.
- O símbolo inicial é `programa`.
- A gramática é livre de ambiguidade para a linguagem definida.
- Comentários (`*{ ... }*`) são removidos pelo analisador léxico antes da análise sintática e não aparecem na gramática.
