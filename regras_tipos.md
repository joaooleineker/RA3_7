# Sistema de Regras de Tipos

Este documento descreve as regras de inferência de tipos da linguagem utilizando a notação formal de cálculo de sequentes, cumprindo o requisito de documentar as decisões semânticas desenvolvidas pelo grupo.

**Tipos Primitivos disponíveis:** `inteiro`, `real`, `bool`.

O ambiente de tipagem (nossa Tabela de Símbolos) é denotado por $\Gamma$, que mapeia variáveis para seus tipos inferidos. A notação formal $\Gamma \vdash e : T$ significa que, no contexto $\Gamma$, a expressão $e$ possui o tipo $T$.

---

## 1. Literais

Para valores literais, os tipos são inferidos diretamente com base na sua estrutura léxica.

```text
------------------------- (T-Int)
 Γ ⊢ literal_int : inteiro


------------------------- (T-Real)
 Γ ⊢ literal_real : real
```
*(Literal inteiro não possui ponto decimal; literal real possui o caractere `.` em sua estrutura.)*

O tipo `bool` não possui literais explícitos na linguagem. Valores booleanos são **produzidos exclusivamente por operadores relacionais** (`<`, `>`, `<=`, `>=`, `==`, `!=`).

---

## 2. Operadores Aritméticos

Os operadores aritméticos operam de forma estrita sobre os tipos numéricos (`inteiro` e `real`). Valores lógicos (`bool`) são sumariamente rejeitados nestas operações.

Seja $Num = \{inteiro, real\}$.

### 2.1. Divisão Inteira e Resto (`/`, `%`)

Estes operadores exigem que **ambos** os operandos sejam `inteiro`, resultando estritamente em `inteiro`.

```text
  Γ ⊢ e1 : inteiro    Γ ⊢ e2 : inteiro
---------------------------------------- (T-DivInt)
      Γ ⊢ e1 op e2 : inteiro
      (onde op ∈ {/, %})


  Γ ⊢ e1 : T1    Γ ⊢ e2 : T2    (T1 ∉ {inteiro} ou T2 ∉ {inteiro})
--------------------------------------------------------------------- (T-DivInt-Erro)
     ERRO SEMÂNTICO: op requer operandos 'inteiro', recebeu T1 e T2
     (onde op ∈ {/, %})
```

### 2.2. Divisão Real (`|`)

Resulta sempre no tipo `real`. Ambos os operandos devem ser numéricos.

```text
  Γ ⊢ e1 : T1    Γ ⊢ e2 : T2     T1, T2 ∈ Num
---------------------------------------------- (T-DivReal)
                Γ ⊢ e1 | e2 : real
```

### 2.3. Soma, Subtração, Multiplicação e Potenciação (`+`, `-`, `*`, `^`)

Aplica-se a regra de promoção de tipos: se ambos os operandos são `inteiro`, o resultado é `inteiro`; se houver qualquer operando `real`, o resultado é `real`. O tipo `bool` é proibido.

```text
  Γ ⊢ e1 : inteiro    Γ ⊢ e2 : inteiro
---------------------------------------- (T-Aritm-Int)
         Γ ⊢ e1 op e2 : inteiro
         (onde op ∈ {+, -, *, ^})


  Γ ⊢ e1 : T1    Γ ⊢ e2 : T2     T1, T2 ∈ Num     (T1 = real ou T2 = real)
----------------------------------------------------------------------------- (T-Aritm-Real)
                    Γ ⊢ e1 op e2 : real
                    (onde op ∈ {+, -, *, ^})


  Γ ⊢ e1 : T1    Γ ⊢ e2 : T2     (T1 = bool ou T2 = bool)
----------------------------------------------------------- (T-Aritm-Erro)
  ERRO SEMÂNTICO: op não pode ser aplicado ao tipo 'bool'
  (onde op ∈ {+, -, *, ^, /, %, |})
```

---

## 3. Operadores Relacionais

Operadores relacionais avaliam grandezas e sempre produzem o tipo `bool`.

### 3.1. Operadores de Ordenação (`<`, `>`, `<=`, `>=`)

Apenas operandos **numéricos** são permitidos. O uso de `bool` como operando é proibido.

```text
  Γ ⊢ e1 : T1    Γ ⊢ e2 : T2     T1, T2 ∈ Num
---------------------------------------------- (T-Rel-Num)
               Γ ⊢ e1 op e2 : bool
               (onde op ∈ {<, >, <=, >=})


  Γ ⊢ e1 : T1    Γ ⊢ e2 : T2     (T1 = bool ou T2 = bool)
----------------------------------------------------------- (T-Rel-Erro)
  ERRO SEMÂNTICO: op não pode ser aplicado ao tipo 'bool'
  (onde op ∈ {<, >, <=, >=})
```

### 3.2. Operadores de Igualdade (`==`, `!=`)

Aceitam dois numéricos (comparados entre si por coerção natural) **ou** dois booleanos (comparados entre si). Tipos mistos entre `bool` e numérico são inválidos.

```text
  Γ ⊢ e1 : T    Γ ⊢ e2 : T
---------------------------- (T-Eq-MesmoTipo)
    Γ ⊢ e1 op e2 : bool
    (onde op ∈ {==, !=})


  Γ ⊢ e1 : T1    Γ ⊢ e2 : T2     T1, T2 ∈ Num
---------------------------------------------- (T-Eq-Num)
                 Γ ⊢ e1 op e2 : bool
                 (onde op ∈ {==, !=})


  Γ ⊢ e1 : T1    Γ ⊢ e2 : T2     T1 ≠ T2     ¬(T1, T2 ∈ Num)
--------------------------------------------------------------- (T-Eq-Erro)
   ERRO SEMÂNTICO: comparação entre tipos incompatíveis T1 e T2
   (onde op ∈ {==, !=})
```

---

## 4. Variáveis e Memória

A recuperação de variáveis da memória (LOAD) e o armazenamento (STORE) dependem do contexto e da Tabela de Símbolos.

```text
       x : T ∈ Γ
----------------------- (T-Var)
      Γ ⊢ x : T
```

Para o **STORE** (primeira atribuição), a variável herda permanentemente o tipo da expressão. Para atribuições subsequentes, o tipo da expressão deve ser idêntico ao tipo já registrado.

```text
  Γ ⊢ e : T     x ∉ Γ
--------------------------------------- (T-Store-Novo)
    Γ[x ↦ T] ⊢ e x : T


  Γ ⊢ e : T     x : T ∈ Γ
--------------------------------------- (T-Store-Compat)
         Γ ⊢ e x : T


  Γ ⊢ e : T2     x : T1 ∈ Γ     T1 ≠ T2
----------------------------------------- (T-Store-Erro)
  ERRO SEMÂNTICO: redefinição incompatível de x (T1 → T2)
```
*(Nota: O STORE na RPN consome a expressão e anota a si mesmo com o tipo armazenado.)*

---

## 5. Estruturas de Controle

As estruturas de decisão e laço requerem que a sua condição principal resulte **obrigatoriamente** num valor lógico `bool`.

### 5.1. Laço de Repetição (`WHILE`)

```text
  Γ ⊢ condicao : bool     Γ ⊢ corpo : T_corpo
----------------------------------------------- (T-While)
          Γ ⊢ ( condicao ) corpo WHILE : void


  Γ ⊢ condicao : T     T ≠ bool
---------------------------------------------- (T-While-Erro)
  ERRO SEMÂNTICO: condição do WHILE deve ser 'bool', recebeu T
```

### 5.2. Decisão (`IF`)

```text
  Γ ⊢ condicao : bool    Γ ⊢ bloco_then : T1    Γ ⊢ bloco_else : T2
--------------------------------------------------------------------- (T-If)
       Γ ⊢ ( condicao ) bloco_then bloco_else IF : void


  Γ ⊢ condicao : T     T ≠ bool
---------------------------------------------- (T-If-Erro)
  ERRO SEMÂNTICO: condição do IF deve ser 'bool', recebeu T
```
*(Nota de Implementação: Estruturas de controle não registram valor no histórico global de `RES`; seu tipo de retorno externo é `void`.)*

---

## 6. Operador de Histórico (`RES`)

O comando `RES` busca o resultado da N-ésima operação armazenada no histórico global. O argumento `n` deve ser obrigatoriamente do tipo `inteiro` e positivo.

```text
  Γ ⊢ n : inteiro     n > 0     Histórico[|Histórico| - n] : T
--------------------------------------------------------------- (T-Res)
                      Γ ⊢ n RES : T


  Γ ⊢ n : T     T ≠ inteiro
---------------------------------- (T-Res-Erro-Tipo)
  ERRO SEMÂNTICO: argumento de RES deve ser 'inteiro', recebeu T


  Γ ⊢ n : inteiro     n ≤ 0
---------------------------------- (T-Res-Erro-Valor)
  ERRO SEMÂNTICO: RES(n) inválido — n deve ser positivo


  Γ ⊢ n : inteiro     n > |Histórico|
---------------------------------------- (T-Res-Erro-Alcance)
  ERRO SEMÂNTICO: RES(n) fora do alcance — histórico tem |Histórico| entradas
```
