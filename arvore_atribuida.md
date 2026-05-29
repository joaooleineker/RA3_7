# Árvore Sintática Atribuída (Aumentada)

```text
programa
└── comando_lista
    ├── comando
    │   ├── ABRE_PAREN (()
    │   ├── conteudo_comando [tipo: void, cat: controle]
    │   │   └── KEYWORD_START (START) [tipo: void, cat: controle]
    │   └── FECHA_PAREN ())
    └── comando_lista
        ├── comando
        │   ├── ABRE_PAREN (()
        │   ├── conteudo_comando [tipo: real, cat: expressao]
        │   │   ├── NUMERO (3.14) [tipo: real, cat: literal]
        │   │   └── sufixo_numero
        │   │       ├── NUMERO (2.0) [tipo: real, cat: literal]
        │   │       └── operador_final
        │   │           └── OPERADOR (+) [tipo: real, cat: operador_aritmetico]
        │   └── FECHA_PAREN ())
        └── comando_lista
            ├── comando
            │   ├── ABRE_PAREN (()
            │   ├── conteudo_comando [tipo: inteiro, cat: expressao]
            │   │   ├── NUMERO (10) [tipo: inteiro, cat: literal]
            │   │   └── sufixo_numero
            │   │       ├── NUMERO (3) [tipo: inteiro, cat: literal]
            │   │       └── operador_final
            │   │           └── OPERADOR (/) [tipo: inteiro, cat: operador_aritmetico]
            │   └── FECHA_PAREN ())
            └── comando_lista
                ├── comando
                │   ├── ABRE_PAREN (()
                │   ├── conteudo_comando [tipo: inteiro, cat: expressao]
                │   │   ├── NUMERO (10) [tipo: inteiro, cat: literal]
                │   │   └── sufixo_numero
                │   │       ├── NUMERO (3) [tipo: inteiro, cat: literal]
                │   │       └── operador_final
                │   │           └── OPERADOR (%) [tipo: inteiro, cat: operador_aritmetico]
                │   └── FECHA_PAREN ())
                └── comando_lista
                    ├── comando
                    │   ├── ABRE_PAREN (()
                    │   ├── conteudo_comando [tipo: real, cat: expressao]
                    │   │   ├── NUMERO (2.0) [tipo: real, cat: literal]
                    │   │   └── sufixo_numero
                    │   │       ├── NUMERO (8) [tipo: inteiro, cat: literal]
                    │   │       └── operador_final
                    │   │           └── OPERADOR (^) [tipo: real, cat: operador_aritmetico]
                    │   └── FECHA_PAREN ())
                    └── comando_lista
                        ├── comando
                        │   ├── ABRE_PAREN (()
                        │   ├── conteudo_comando [tipo: real, cat: expressao]
                        │   │   ├── NUMERO (2.0) [tipo: real, cat: literal]
                        │   │   └── sufixo_numero
                        │   │       ├── NUMERO (8) [tipo: inteiro, cat: literal]
                        │   │       └── operador_final
                        │   │           └── OPERADOR (*) [tipo: real, cat: operador_aritmetico]
                        │   └── FECHA_PAREN ())
                        └── comando_lista
                            ├── comando
                            │   ├── ABRE_PAREN (()
                            │   ├── conteudo_comando [tipo: real, cat: expressao]
                            │   │   ├── NUMERO (10.0) [tipo: real, cat: literal]
                            │   │   └── sufixo_numero
                            │   │       ├── NUMERO (3.0) [tipo: real, cat: literal]
                            │   │       └── operador_final
                            │   │           └── OPERADOR (-) [tipo: real, cat: operador_aritmetico]
                            │   └── FECHA_PAREN ())
                            └── comando_lista
                                ├── comando
                                │   ├── ABRE_PAREN (()
                                │   ├── conteudo_comando [tipo: real, cat: expressao]
                                │   │   ├── NUMERO (10.0) [tipo: real, cat: literal]
                                │   │   └── sufixo_numero
                                │   │       ├── NUMERO (3.0) [tipo: real, cat: literal]
                                │   │       └── operador_final
                                │   │           └── OPERADOR (|) [tipo: real, cat: operador_aritmetico]
                                │   └── FECHA_PAREN ())
                                └── comando_lista
                                    ├── comando
                                    │   ├── ABRE_PAREN (()
                                    │   ├── conteudo_comando [tipo: real, cat: expressao]
                                    │   │   ├── NUMERO (1) [tipo: inteiro, cat: literal]
                                    │   │   └── sufixo_numero
                                    │   │       └── KEYWORD_RES (RES) [tipo: real, cat: historico_res]
                                    │   └── FECHA_PAREN ())
                                    └── comando_lista
                                        ├── comando
                                        │   ├── ABRE_PAREN (()
                                        │   ├── conteudo_comando [tipo: void, cat: expressao]
                                        │   │   ├── NUMERO (5.0) [tipo: real, cat: literal]
                                        │   │   └── sufixo_numero
                                        │   │       ├── MEMORIA (VAR) [tipo: real, cat: var_store]
                                        │   │       └── apos_mem
                                        │   │           └── ε () [tipo: void, cat: pontuacao]
                                        │   └── FECHA_PAREN ())
                                        └── comando_lista
                                            ├── comando
                                            │   ├── ABRE_PAREN (()
                                            │   ├── conteudo_comando [tipo: real, cat: expressao]
                                            │   │   ├── MEMORIA (VAR) [tipo: real, cat: var_load]
                                            │   │   └── sufixo_memoria
                                            │   │       └── ε () [tipo: void, cat: pontuacao]
                                            │   └── FECHA_PAREN ())
                                            └── comando_lista
                                                ├── comando
                                                │   ├── ABRE_PAREN (()
                                                │   ├── conteudo_comando [tipo: void, cat: controle]
                                                │   │   ├── comando
                                                │   │   │   ├── ABRE_PAREN (()
                                                │   │   │   ├── conteudo_comando [tipo: bool, cat: expressao]
                                                │   │   │   │   ├── MEMORIA (VAR) [tipo: real, cat: var_load]
                                                │   │   │   │   └── sufixo_memoria
                                                │   │   │   │       ├── NUMERO (10.0) [tipo: real, cat: literal]
                                                │   │   │   │       └── operador_final
                                                │   │   │   │           └── OPERADOR_REL (<) [tipo: bool, cat: operador_relacional]
                                                │   │   │   └── FECHA_PAREN ())
                                                │   │   └── sufixo_comando
                                                │   │       ├── comando
                                                │   │       │   ├── ABRE_PAREN (()
                                                │   │       │   ├── conteudo_comando [tipo: void, cat: expressao]
                                                │   │       │   │   ├── comando
                                                │   │       │   │   │   ├── ABRE_PAREN (() [tipo: void, cat: pontuacao]
                                                │   │       │   │   │   ├── conteudo_comando
                                                │   │       │   │   │   │   ├── MEMORIA (VAR) [tipo: real, cat: var_load]
                                                │   │       │   │   │   │   └── sufixo_memoria
                                                │   │       │   │   │   │       ├── NUMERO (1.0) [tipo: real, cat: literal]
                                                │   │       │   │   │   │       └── operador_final
                                                │   │       │   │   │   │           └── OPERADOR (+) [tipo: real, cat: operador_aritmetico]
                                                │   │       │   │   │   └── FECHA_PAREN ()) [tipo: void, cat: pontuacao]
                                                │   │       │   │   └── sufixo_comando
                                                │   │       │   │       ├── MEMORIA (VAR) [tipo: real, cat: var_store]
                                                │   │       │   │       └── apos_mem
                                                │   │       │   │           └── ε () [tipo: void, cat: pontuacao]
                                                │   │       │   └── FECHA_PAREN ())
                                                │   │       └── apos_cmd
                                                │   │           └── KEYWORD_WHILE (WHILE)
                                                │   └── FECHA_PAREN ())
                                                └── comando_lista
                                                    ├── comando
                                                    │   ├── ABRE_PAREN (()
                                                    │   ├── conteudo_comando [tipo: void, cat: controle]
                                                    │   │   ├── comando
                                                    │   │   │   ├── ABRE_PAREN (()
                                                    │   │   │   ├── conteudo_comando [tipo: bool, cat: expressao]
                                                    │   │   │   │   ├── MEMORIA (VAR) [tipo: real, cat: var_load]
                                                    │   │   │   │   └── sufixo_memoria
                                                    │   │   │   │       ├── NUMERO (5.0) [tipo: real, cat: literal]
                                                    │   │   │   │       └── operador_final
                                                    │   │   │   │           └── OPERADOR_REL (>) [tipo: bool, cat: operador_relacional]
                                                    │   │   │   └── FECHA_PAREN ())
                                                    │   │   └── sufixo_comando
                                                    │   │       ├── comando
                                                    │   │       │   ├── ABRE_PAREN (()
                                                    │   │       │   ├── conteudo_comando [tipo: void, cat: expressao]
                                                    │   │       │   │   ├── NUMERO (1.0) [tipo: real, cat: literal]
                                                    │   │       │   │   └── sufixo_numero
                                                    │   │       │   │       ├── MEMORIA (RESULTADO) [tipo: real, cat: var_store]
                                                    │   │       │   │       └── apos_mem
                                                    │   │       │   │           └── ε () [tipo: void, cat: pontuacao]
                                                    │   │       │   └── FECHA_PAREN ())
                                                    │   │       └── apos_cmd
                                                    │   │           ├── comando
                                                    │   │           │   ├── ABRE_PAREN (()
                                                    │   │           │   ├── conteudo_comando [tipo: void, cat: expressao]
                                                    │   │           │   │   ├── NUMERO (0.0) [tipo: real, cat: literal]
                                                    │   │           │   │   └── sufixo_numero
                                                    │   │           │   │       ├── MEMORIA (RESULTADO) [tipo: real, cat: var_store]
                                                    │   │           │   │       └── apos_mem
                                                    │   │           │   │           └── ε () [tipo: void, cat: pontuacao]
                                                    │   │           │   └── FECHA_PAREN ())
                                                    │   │           └── KEYWORD_IF (IF)
                                                    │   └── FECHA_PAREN ())
                                                    └── comando_lista
                                                        ├── comando
                                                        │   ├── ABRE_PAREN (()
                                                        │   ├── conteudo_comando [tipo: real, cat: expressao]
                                                        │   │   ├── MEMORIA (VAR) [tipo: real, cat: var_load]
                                                        │   │   └── sufixo_memoria
                                                        │   │       └── ε () [tipo: void, cat: pontuacao]
                                                        │   └── FECHA_PAREN ())
                                                        └── comando_lista
                                                            ├── comando
                                                            │   ├── ABRE_PAREN (()
                                                            │   ├── conteudo_comando [tipo: void, cat: expressao]
                                                            │   │   ├── NUMERO (5.0) [tipo: real, cat: literal]
                                                            │   │   └── sufixo_numero
                                                            │   │       ├── MEMORIA (MEM) [tipo: real, cat: var_store]
                                                            │   │       └── apos_mem
                                                            │   │           └── ε () [tipo: void, cat: pontuacao]
                                                            │   └── FECHA_PAREN ())
                                                            └── comando_lista
                                                                ├── comando
                                                                │   ├── ABRE_PAREN (()
                                                                │   ├── conteudo_comando [tipo: void, cat: expressao]
                                                                │   │   ├── NUMERO (10.0) [tipo: real, cat: literal]
                                                                │   │   └── sufixo_numero
                                                                │   │       ├── MEMORIA (MEM) [tipo: real, cat: var_store]
                                                                │   │       └── apos_mem
                                                                │   │           └── ε () [tipo: void, cat: pontuacao]
                                                                │   └── FECHA_PAREN ())
                                                                └── comando_lista
                                                                    ├── comando
                                                                    │   ├── ABRE_PAREN (()
                                                                    │   ├── conteudo_comando [tipo: real, cat: expressao]
                                                                    │   │   ├── MEMORIA (MEM) [tipo: real, cat: var_load]
                                                                    │   │   └── sufixo_memoria
                                                                    │   │       └── ε () [tipo: void, cat: pontuacao]
                                                                    │   └── FECHA_PAREN ())
                                                                    └── comando_lista
                                                                        ├── comando
                                                                        │   ├── ABRE_PAREN (()
                                                                        │   ├── conteudo_comando [tipo: void, cat: controle]
                                                                        │   │   └── KEYWORD_END (END) [tipo: void, cat: controle]
                                                                        │   └── FECHA_PAREN ())
                                                                        └── comando_lista
                                                                            └── ε ()
```
