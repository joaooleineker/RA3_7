# Árvore Sintática (Derivação)

## Resultado do teste1.txt:

```text
programa
└── comando_lista
    ├── comando
    │   ├── ABRE_PAREN (()
    │   ├── conteudo_comando
    │   │   └── KEYWORD_START (START)
    │   └── FECHA_PAREN ())
    └── comando_lista
        ├── comando
        │   ├── ABRE_PAREN (()
        │   ├── conteudo_comando
        │   │   ├── NUMERO (3.14)
        │   │   └── sufixo_numero
        │   │       ├── NUMERO (2.0)
        │   │       └── operador_final
        │   │           └── OPERADOR (+)
        │   └── FECHA_PAREN ())
        └── comando_lista
            ├── comando
            │   ├── ABRE_PAREN (()
            │   ├── conteudo_comando
            │   │   ├── NUMERO (10)
            │   │   └── sufixo_numero
            │   │       ├── NUMERO (3)
            │   │       └── operador_final
            │   │           └── OPERADOR (/)
            │   └── FECHA_PAREN ())
            └── comando_lista
                ├── comando
                │   ├── ABRE_PAREN (()
                │   ├── conteudo_comando
                │   │   ├── NUMERO (10)
                │   │   └── sufixo_numero
                │   │       ├── NUMERO (3)
                │   │       └── operador_final
                │   │           └── OPERADOR (%)
                │   └── FECHA_PAREN ())
                └── comando_lista
                    ├── comando
                    │   ├── ABRE_PAREN (()
                    │   ├── conteudo_comando
                    │   │   ├── NUMERO (2.0)
                    │   │   └── sufixo_numero
                    │   │       ├── NUMERO (8)
                    │   │       └── operador_final
                    │   │           └── OPERADOR (^)
                    │   └── FECHA_PAREN ())
                    └── comando_lista
                        ├── comando
                        │   ├── ABRE_PAREN (()
                        │   ├── conteudo_comando
                        │   │   ├── NUMERO (2.0)
                        │   │   └── sufixo_numero
                        │   │       ├── NUMERO (8)
                        │   │       └── operador_final
                        │   │           └── OPERADOR (*)
                        │   └── FECHA_PAREN ())
                        └── comando_lista
                            ├── comando
                            │   ├── ABRE_PAREN (()
                            │   ├── conteudo_comando
                            │   │   ├── NUMERO (1)
                            │   │   └── sufixo_numero
                            │   │       └── KEYWORD_RES (RES)
                            │   └── FECHA_PAREN ())
                            └── comando_lista
                                ├── comando
                                │   ├── ABRE_PAREN (()
                                │   ├── conteudo_comando
                                │   │   ├── NUMERO (5.0)
                                │   │   └── sufixo_numero
                                │   │       ├── MEMORIA (VAR)
                                │   │       └── apos_mem
                                │   │           └── ε ()
                                │   └── FECHA_PAREN ())
                                └── comando_lista
                                    ├── comando
                                    │   ├── ABRE_PAREN (()
                                    │   ├── conteudo_comando
                                    │   │   ├── MEMORIA (VAR)
                                    │   │   └── sufixo_memoria
                                    │   │       └── ε ()
                                    │   └── FECHA_PAREN ())
                                    └── comando_lista
                                        ├── comando
                                        │   ├── ABRE_PAREN (()
                                        │   ├── conteudo_comando
                                        │   │   ├── comando
                                        │   │   │   ├── ABRE_PAREN (()
                                        │   │   │   ├── conteudo_comando
                                        │   │   │   │   ├── MEMORIA (VAR)
                                        │   │   │   │   └── sufixo_memoria
                                        │   │   │   │       ├── NUMERO (10.0)
                                        │   │   │   │       └── operador_final
                                        │   │   │   │           └── OPERADOR_REL (<)
                                        │   │   │   └── FECHA_PAREN ())
                                        │   │   └── sufixo_comando
                                        │   │       ├── comando
                                        │   │       │   ├── ABRE_PAREN (()
                                        │   │       │   ├── conteudo_comando
                                        │   │       │   │   ├── comando
                                        │   │       │   │   │   ├── ABRE_PAREN (()
                                        │   │       │   │   │   ├── conteudo_comando
                                        │   │       │   │   │   │   ├── MEMORIA (VAR)
                                        │   │       │   │   │   │   └── sufixo_memoria
                                        │   │       │   │   │   │       ├── NUMERO (1.0)
                                        │   │       │   │   │   │       └── operador_final
                                        │   │       │   │   │   │           └── OPERADOR (+)
                                        │   │       │   │   │   └── FECHA_PAREN ())
                                        │   │       │   │   └── sufixo_comando
                                        │   │       │   │       ├── MEMORIA (VAR)
                                        │   │       │   │       └── apos_mem
                                        │   │       │   │           └── ε ()
                                        │   │       │   └── FECHA_PAREN ())
                                        │   │       └── apos_cmd
                                        │   │           └── KEYWORD_WHILE (WHILE)
                                        │   └── FECHA_PAREN ())
                                        └── comando_lista
                                            ├── comando
                                            │   ├── ABRE_PAREN (()
                                            │   ├── conteudo_comando
                                            │   │   ├── comando
                                            │   │   │   ├── ABRE_PAREN (()
                                            │   │   │   ├── conteudo_comando
                                            │   │   │   │   ├── MEMORIA (VAR)
                                            │   │   │   │   └── sufixo_memoria
                                            │   │   │   │       ├── NUMERO (5.0)
                                            │   │   │   │       └── operador_final
                                            │   │   │   │           └── OPERADOR_REL (>)
                                            │   │   │   └── FECHA_PAREN ())
                                            │   │   └── sufixo_comando
                                            │   │       ├── comando
                                            │   │       │   ├── ABRE_PAREN (()
                                            │   │       │   ├── conteudo_comando
                                            │   │       │   │   ├── NUMERO (1.0)
                                            │   │       │   │   └── sufixo_numero
                                            │   │       │   │       ├── MEMORIA (RESULTADO)
                                            │   │       │   │       └── apos_mem
                                            │   │       │   │           └── ε ()
                                            │   │       │   └── FECHA_PAREN ())
                                            │   │       └── apos_cmd
                                            │   │           ├── comando
                                            │   │           │   ├── ABRE_PAREN (()
                                            │   │           │   ├── conteudo_comando
                                            │   │           │   │   ├── NUMERO (0.0)
                                            │   │           │   │   └── sufixo_numero
                                            │   │           │   │       ├── MEMORIA (RESULTADO)
                                            │   │           │   │       └── apos_mem
                                            │   │           │   │           └── ε ()
                                            │   │           │   └── FECHA_PAREN ())
                                            │   │           └── KEYWORD_IF (IF)
                                            │   └── FECHA_PAREN ())
                                            └── comando_lista
                                                ├── comando
                                                │   ├── ABRE_PAREN (()
                                                │   ├── conteudo_comando
                                                │   │   ├── MEMORIA (VAR)
                                                │   │   └── sufixo_memoria
                                                │   │       └── ε ()
                                                │   └── FECHA_PAREN ())
                                                └── comando_lista
                                                    ├── comando
                                                    │   ├── ABRE_PAREN (()
                                                    │   ├── conteudo_comando
                                                    │   │   ├── NUMERO (5.0)
                                                    │   │   └── sufixo_numero
                                                    │   │       ├── MEMORIA (MEM)
                                                    │   │       └── apos_mem
                                                    │   │           └── ε ()
                                                    │   └── FECHA_PAREN ())
                                                    └── comando_lista
                                                        ├── comando
                                                        │   ├── ABRE_PAREN (()
                                                        │   ├── conteudo_comando
                                                        │   │   ├── NUMERO (10.0)
                                                        │   │   └── sufixo_numero
                                                        │   │       ├── MEMORIA (MEM)
                                                        │   │       └── apos_mem
                                                        │   │           └── ε ()
                                                        │   └── FECHA_PAREN ())
                                                        └── comando_lista
                                                            ├── comando
                                                            │   ├── ABRE_PAREN (()
                                                            │   ├── conteudo_comando
                                                            │   │   ├── MEMORIA (MEM)
                                                            │   │   └── sufixo_memoria
                                                            │   │       └── ε ()
                                                            │   └── FECHA_PAREN ())
                                                            └── comando_lista
                                                                ├── comando
                                                                │   ├── ABRE_PAREN (()
                                                                │   ├── conteudo_comando
                                                                │   │   └── KEYWORD_END (END)
                                                                │   └── FECHA_PAREN ())
                                                                └── comando_lista
                                                                    └── ε ()
```
