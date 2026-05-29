.global _start

.data
    .align 3
    const_3_14: .double 3.14
    .align 3
    const_2_0: .double 2.0
    iconst_10: .word 10
    iconst_3: .word 3
    iconst_8: .word 8
    .align 3
    const_1_0: .double 1.0
    .align 3
    const_10_0: .double 10.0
    .align 3
    const_3_0: .double 3.0
    iconst_1: .word 1
    .align 3
    const_5_0: .double 5.0
    .align 3
    mem_VAR: .double 0.0
    .align 3
    mem_RESULTADO: .double 0.0
    .align 3
    const_0_0: .double 0.0
    .align 3
    mem_MEM: .double 0.0
    .align 3
    resultados: .space 800       @ espaco para 100 doubles
    numResultados: .word 0

.text
_start:

    @ (START) - inicio do programa

    @ Comando RPN: ( 3.14 2.0 + )
    LDR R4, =const_3_14
    VLDR D0, [R4]             @ carrega double 3.14
    LDR R4, =const_2_0
    VLDR D1, [R4]             @ carrega double 2.0
    VADD.F64 D2, D0, D1    @ soma real
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D2, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ Comando RPN: ( 10 3 / )
    LDR R4, =iconst_10
    LDR R5, [R4]              @ carrega inteiro 10
    LDR R4, =iconst_3
    LDR R6, [R4]              @ carrega inteiro 3
    @ divisao inteira via VFP (Cortex-A9 nao suporta SDIV)
    VMOV S30, R5
    VCVT.F64.S32 D0, S30         @ dividendo int -> double
    VMOV S30, R6
    VCVT.F64.S32 D1, S30         @ divisor int -> double
    VDIV.F64 D0, D0, D1
    VCVT.S32.F64 S31, D0         @ trunca para inteiro
    VMOV R7, S31
    VMOV S30, R7              @ copia int para VFP
    VCVT.F64.S32 D2, S30   @ converte int para double
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D2, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ Comando RPN: ( 10 3 % )
    LDR R4, =iconst_10
    LDR R5, [R4]              @ carrega inteiro 10
    LDR R4, =iconst_3
    LDR R6, [R4]              @ carrega inteiro 3
    @ resto via VFP: R5 % R6
    VMOV S30, R5
    VCVT.F64.S32 D0, S30
    VMOV S30, R6
    VCVT.F64.S32 D1, S30
    VDIV.F64 D0, D0, D1  @ quociente real
    VCVT.S32.F64 S31, D0           @ trunca quociente
    VMOV R7, S31
    MUL R8, R7, R6
    SUB R8, R5, R8   @ resto
    VMOV S30, R8              @ copia int para VFP
    VCVT.F64.S32 D2, S30   @ converte int para double
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D2, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ Comando RPN: ( 2.0 8 ^ )
    LDR R4, =const_2_0
    VLDR D0, [R4]             @ carrega double 2.0
    LDR R4, =iconst_8
    LDR R5, [R4]              @ carrega inteiro 8
    @ potenciacao: base ^ expoente
    LDR R4, =const_1_0
    VLDR D1, [R4]         @ resultado = 1.0
    MOV R0, R5            @ R0 = expoente
potencia_0:
    CMP R0, #0
    BLE potencia_0_fim
    VMUL.F64 D1, D1, D0
    SUB R0, R0, #1
    B potencia_0
potencia_0_fim:
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D1, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ Comando RPN: ( 2.0 8 * )
    LDR R4, =const_2_0
    VLDR D0, [R4]             @ carrega double 2.0
    LDR R4, =iconst_8
    LDR R5, [R4]              @ carrega inteiro 8
    VMOV S30, R5              @ copia int para VFP
    VCVT.F64.S32 D1, S30   @ converte int para double
    VMUL.F64 D2, D0, D1    @ multiplicacao real
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D2, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ Comando RPN: ( 10.0 3.0 - )
    LDR R4, =const_10_0
    VLDR D0, [R4]             @ carrega double 10.0
    LDR R4, =const_3_0
    VLDR D1, [R4]             @ carrega double 3.0
    VSUB.F64 D2, D0, D1    @ subtracao real
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D2, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ Comando RPN: ( 10.0 3.0 | )
    LDR R4, =const_10_0
    VLDR D0, [R4]             @ carrega double 10.0
    LDR R4, =const_3_0
    VLDR D1, [R4]             @ carrega double 3.0
    VDIV.F64 D2, D0, D1    @ divisao real
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D2, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ Comando RPN: ( 1 RES )
    LDR R4, =iconst_1
    LDR R5, [R4]              @ carrega inteiro 1
    @ RES: acessa resultado anterior
    LDR R1, =resultados
    LDR R2, =numResultados
    LDR R2, [R2]                @ R2 = contador total
    SUB R2, R2, R5         @ indice = total - N
    LSL R2, R2, #3              @ offset em bytes (double = 8)
    ADD R1, R1, R2
    VLDR D0, [R1]        @ carrega resultado historico
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D0, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ Comando RPN: ( 5.0 VAR )
    LDR R4, =const_5_0
    VLDR D0, [R4]             @ carrega double 5.0
    LDR R0, =mem_VAR        @ store em VAR
    VSTR D0, [R0]

    @ Comando RPN: ( VAR )
    LDR R0, =mem_VAR        @ load de VAR
    VLDR D0, [R0]
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D0, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ WHILE - inicio do loop
while_1:
    @ Avalia condicao do WHILE

    @ Comando RPN: ( VAR 10.0 < )
    LDR R0, =mem_VAR        @ load de VAR
    VLDR D0, [R0]
    LDR R4, =const_10_0
    VLDR D1, [R4]             @ carrega double 10.0
    @ comparacao relacional '<'
    VCMP.F64 D0, D1
    VMRS APSR_nzcv, FPSCR
    BLT rel_verdade_2
    MOV R5, #0            @ false
    B rel_fim_3
rel_verdade_2:
    MOV R5, #1            @ true
rel_fim_3:
    VMOV S30, R5              @ copia int para VFP
    VCVT.F64.S32 D2, S30   @ converte int para double
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D2, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++
    CMP R5, #0
    BEQ while_1_fim             @ se condicao == 0 (falso), sai do loop
    @ Corpo do WHILE

    @ Comando RPN: ( VAR 1.0 + VAR )
    LDR R0, =mem_VAR        @ load de VAR
    VLDR D0, [R0]
    LDR R4, =const_1_0
    VLDR D1, [R4]             @ carrega double 1.0
    VADD.F64 D2, D0, D1    @ soma real
    LDR R0, =mem_VAR        @ store em VAR
    VSTR D2, [R0]
    B while_1               @ volta ao inicio do loop
while_1_fim:

    @ IF - Avalia condicao

    @ Comando RPN: ( VAR 5.0 > )
    LDR R0, =mem_VAR        @ load de VAR
    VLDR D0, [R0]
    LDR R4, =const_5_0
    VLDR D1, [R4]             @ carrega double 5.0
    @ comparacao relacional '>'
    VCMP.F64 D0, D1
    VMRS APSR_nzcv, FPSCR
    BGT rel_verdade_6
    MOV R5, #0            @ false
    B rel_fim_7
rel_verdade_6:
    MOV R5, #1            @ true
rel_fim_7:
    VMOV S30, R5              @ copia int para VFP
    VCVT.F64.S32 D2, S30   @ converte int para double
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D2, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++
    CMP R5, #0
    BEQ if_else_4            @ se falso (0), pula pro else
    @ IF - Bloco THEN (Verdadeiro)

    @ Comando RPN: ( 1.0 RESULTADO )
    LDR R4, =const_1_0
    VLDR D0, [R4]             @ carrega double 1.0
    LDR R0, =mem_RESULTADO        @ store em RESULTADO
    VSTR D0, [R0]
    B if_fim_5               @ fim do then, pula o else
if_else_4:
    @ IF - Bloco ELSE (Falso)

    @ Comando RPN: ( 0.0 RESULTADO )
    LDR R4, =const_0_0
    VLDR D0, [R4]             @ carrega double 0.0
    LDR R0, =mem_RESULTADO        @ store em RESULTADO
    VSTR D0, [R0]
if_fim_5:

    @ Comando RPN: ( VAR )
    LDR R0, =mem_VAR        @ load de VAR
    VLDR D0, [R0]
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D0, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ Comando RPN: ( 5.0 MEM )
    LDR R4, =const_5_0
    VLDR D0, [R4]             @ carrega double 5.0
    LDR R0, =mem_MEM        @ store em MEM
    VSTR D0, [R0]

    @ Comando RPN: ( 10.0 MEM )
    LDR R4, =const_10_0
    VLDR D0, [R4]             @ carrega double 10.0
    LDR R0, =mem_MEM        @ store em MEM
    VSTR D0, [R0]

    @ Comando RPN: ( MEM )
    LDR R0, =mem_MEM        @ load de MEM
    VLDR D0, [R0]
    @ Armazena resultado no historico
    LDR R0, =numResultados
    LDR R1, [R0]                @ R1 = numResultados atual
    LDR R2, =resultados
    LSL R3, R1, #3              @ offset = R1 * 8
    ADD R2, R2, R3
    VSTR D0, [R2]     @ guarda resultado
    ADD R1, R1, #1
    STR R1, [R0]                @ numResultados++

    @ (END) - fim do programa

    @ Fim do programa
fim:
    B fim
