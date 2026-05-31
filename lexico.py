# Integrantes do grupo (ordem alfabética):
# Daniel de Almeida Santos Bina - danielbina
# Eduardo Ferreira de Melo - edufmelo
# João Eduardo Faccin Leineker - joaooleineker
#
# Nome do grupo no Canvas: RA3_7

import sys

# Como nos slides (Aula 04), contudo, de forma mais simples com tipo e valor
class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo  # o tipo do token (NUMERO, OPERADOR, PARENTESE, IDENTIFICADOR, KEYWORD, ERRO)
        self.valor = valor  # o texto original do token (ex: '3.14', '+', 'RES')

# Lê o arquivo de entrada e armazena cada linha na lista 'linhas'
def lerArquivo(nomeArquivo, linhas):
    try:
        arquivo = open(nomeArquivo, "r")

        for linha in arquivo:
            linhaLimpada = linha.strip()
            if linhaLimpada != "":
                linhas.append(linhaLimpada)

        arquivo.close()

    except FileNotFoundError:
        print("Erro: arquivo '" + nomeArquivo + "' nao encontrado.")

    except Exception as e:
        print("Erro ao ler arquivo: " + str(e))

# Deve analisar uma linha de expressão RPN e extrair tokens - age como estado inicial do AFD
def parseExpressao(linha, vetorTokens):
    pos = 0
    while pos < len(linha):
        char = linha[pos]

        if char == " " or char == "\t":
            pos += 1
        elif char == "*" and pos + 1 < len(linha) and linha[pos + 1] == "{":
            pos = estadoComentario(linha, pos, vetorTokens)
        elif char.isdigit() or char == ".":
            pos = estadoNumero(linha, pos, vetorTokens)
        elif char in "-+*/|%^":
            pos = estadoOperador(linha, pos, vetorTokens)
        elif char in "<>=!":    
            pos = estadoRelacional(linha, pos, vetorTokens)
        elif char in "()":
            pos = estadoParenteses(linha, pos, vetorTokens)
        elif char.isalpha():
            pos = estadoIdentificador(linha, pos, vetorTokens)
        else:
            pos = estadoErro(linha, pos, vetorTokens)

def estadoComentario(linha, pos, tokens):
    pos += 2 # ignora '*{'

    # Continua 'procurando' enquanto estiver pelo menos dois caracteres
    while pos + 1 < len(linha):
        if linha[pos] == "}" and linha[pos + 1] == "*":
            return pos + 2

        pos += 1

    novoToken = Token("ERRO", "comentario_nao_fechado")
    tokens.append(novoToken)

    return len(linha)

def estadoNumero(linha, pos, tokens):
    textoNumero = ""
    qtdePontos = 0

    while pos < len(linha) and (linha[pos].isdigit() or linha[pos] == "."):
        if linha[pos] == ".":
            qtdePontos += 1

        textoNumero += linha[pos]
        pos += 1

    if qtdePontos <= 1:
        novoToken = Token("NUMERO", textoNumero)
    else:
        novoToken = Token("ERRO", textoNumero)

    tokens.append(novoToken)

    return pos

def estadoOperador(linha, pos, tokens):
    char = linha[pos]

    # Como divisão real = | e inteira = /, removemos o que estava fazendo na fase 1
    # if char == "/" and pos + 1 < len(linha) and linha[pos + 1] == "/":
    #     novoToken = Token("OPERADOR", "//")
    #     tokens.append(novoToken)
    #     return pos + 2

    novoToken = Token("OPERADOR", char)
    tokens.append(novoToken)

    return pos + 1

def estadoRelacional(linha, pos, tokens):
    char = linha[pos]
    
    # Verifica caracteres duplos
    if pos + 1 < len(linha):
        proximo_char = linha[pos + 1]
        operador_duplo = char + proximo_char
        
        if operador_duplo in ["==", "<=", ">=", "!="]:
            novoToken = Token("OPERADOR_REL", operador_duplo)
            tokens.append(novoToken)
            return pos + 2
            
    if char in ["<", ">"]:
        novoToken = Token("OPERADOR_REL", char)
    else:
        novoToken = Token("ERRO", char)

    tokens.append(novoToken)
    return pos + 1

def estadoParenteses(linha, pos, tokens):
    char = linha[pos]

    if char == "(":
        novoToken = Token("ABRE_PAREN", char)
    else:
        novoToken = Token("FECHA_PAREN", char)

    tokens.append(novoToken)
    return pos + 1

def estadoIdentificador(linha, pos, tokens):  # keywords e memoria
    textoId = ""

    while pos < len(linha) and linha[pos].isalpha():
        textoId += linha[pos]
        pos += 1

    palavras_reservadas = ["RES", "START", "END",
                           "IF", "WHILE"]  
    
    if textoId in palavras_reservadas:
        novoToken = Token("KEYWORD_" + textoId, textoId)
    elif textoId.isupper():
        novoToken = Token("MEMORIA", textoId)
    else:
        novoToken = Token("ERRO", textoId)
        
    tokens.append(novoToken)
    return pos

# Numeros malformados, tokens inválidos
def estadoErro(linha, pos, tokens):
    charInvalido = linha[pos]
    novoToken = Token("ERRO", charInvalido)
    tokens.append(novoToken)

    return pos + 1

# Avalia as expressões RPN (pilha) e gerencia memoria/RES
def executarExpressao(tokens, resultados, memoria):
    pilha = []
    i = 0
    acaoMemoria = None  

    while i < len(tokens):
        token = tokens[i]

        # Ignora parênteses - estrutura já capturada pela ordem dos tokens
        if token.tipo in ("ABRE_PAREN", "FECHA_PAREN"):
            i += 1

        elif token.tipo == "NUMERO":
            pilha.append(float(token.valor))
            i += 1

        elif token.tipo == "OPERADOR":
            if len(pilha) < 2:
                print("Erro: operandos insuficientes para operador '" + token.valor + "'")
                return None

            b = pilha.pop()
            a = pilha.pop()

            if token.valor == "+":
                pilha.append(a + b)

            elif token.valor == "-":
                pilha.append(a - b)

            elif token.valor == "*":
                pilha.append(a * b)

            elif token.valor == "|":
                if b == 0:
                    print("Erro: divisao real por zero")
                    return None
                pilha.append(a / b)

            elif token.valor == "/":
                if b == 0:
                    print("Erro: divisao inteira por zero")
                    return None
                pilha.append(float(int(a) // int(b)))

            elif token.valor == "%":
                if b == 0:
                    print("Erro: resto por zero")
                    return None
                pilha.append(float(int(a) % int(b)))

            elif token.valor == "^":
                pilha.append(float(a ** int(b)))

            i += 1

        elif token.tipo == "MEMORIA":
            nomeMem = token.valor

            if len(pilha) > 0:
                valorTopo = pilha.pop()
                memoria[nomeMem] = valorTopo
                acaoMemoria = f"{valorTopo:.1f} armazenado" # Guarda o texto
            else:
                if nomeMem in memoria:
                    pilha.append(memoria[nomeMem])
                else:
                    print("Aviso: memoria '" + nomeMem + "' nao inicializada, usando 0.0")
                    pilha.append(0.0)

            i += 1

        elif token.tipo == "KEYWORD_RES":
            if len(pilha) < 1:
                print("Erro: falta o valor N para RES")
                return None

            n = int(pilha.pop())
            indice = len(resultados) - n

            if indice < 0 or indice >= len(resultados):
                print("Erro: RES(" + str(n) + ") fora do historico disponivel")
                return None

            pilha.append(resultados[indice])
            i += 1

        elif token.tipo == "ERRO":
            print("Erro lexico: " + token.valor)
            return None

        else:
            i += 1

    # Ao final, o topo da pilha é o resultado
    if len(pilha) == 1:
        resultado = pilha[0]
        resultados.append(resultado)
        return resultado
    elif len(pilha) == 0:
        if acaoMemoria is not None:  # Se guardou algo, retorna o texto
            return acaoMemoria
        return None
    else:
        print("Erro: pilha com multiplos valores ao final - expressao mal formada")
        return None

# Retorna uma lista de grupos de tokens por nível de aninhamento
def resolverAninhamento(tokens):
    pilhaGrupos = []
    grupoAtual = []
    grupos = []

    for token in tokens:
        if token.tipo == "ABRE_PAREN":
            pilhaGrupos.append(grupoAtual)
            grupoAtual = []
        elif token.tipo == "FECHA_PAREN":
            if not pilhaGrupos:
                # Caso 1: Fechamento sem abertura (Desbalanceado)
                print("Erro Sintático: Parênteses desbalanceado. ')' encontrado sem '(' correspondente.")
                return None
            
            grupos.append(grupoAtual)
            grupoAtual = pilhaGrupos.pop()
        else:
            grupoAtual.append(token)

    if pilhaGrupos:
        # Caso 2: Abertura sem fechamento (Desbalanceado ao final)
        print(f"Erro Sintático: Parênteses desbalanceado. Faltam {len(pilhaGrupos)} parênteses de fechamento.")
        return None

    return grupos

# Gera codigo Assembly ARMv7 (VFP)
def gerarAssembly(listaTokens, codigoAssembly):
    secaoDados = []  # linhas da secao .data (constantes e variaveis)
    secaoTexto = []  # linhas da secao .text (instrucoes)
    contadorLabel = 0  # contador de labels para loops (potenciacao)
    labelsMemoria = set()  # labels de memoria ja criadas no .data
    constantesUsadas = {}  # mapeia valor -> nome do label (deduplicacao)

    for numLinha, tokens in enumerate(listaTokens):
        numReal = numLinha + 1
        grupos = resolverAninhamento(tokens)
        if grupos is None:
            secaoTexto.append("")
            secaoTexto.append(f"    @ Linha {numReal} - IGNORADA (ERRO SINTATICO)")
            continue

        pilhaRegistradores = []
        contadorRegistrador = 0

        temErro = any(t.tipo == "ERRO" for t in tokens)
        if temErro:
            secaoTexto.append("")
            secaoTexto.append(f"    @ Linha {numReal} - IGNORADA (ERRO LEXICO)")
            continue

        secaoTexto.append("")
        secaoTexto.append(f"    @ Linha {numReal}")
        secaoTexto.append(f"linha{numReal}:")

        for grupo in grupos:
            for token in grupo:
                if token.tipo == "NUMERO":
                    valorNumero = token.valor

                    # Deduplicacao: reutiliza label se o valor ja foi declarado
                    if valorNumero in constantesUsadas:
                        nomeConst = constantesUsadas[valorNumero]
                    else:
                        valorLabel = valorNumero.replace(".", "_")
                        nomeConst = "const_" + valorLabel
                        constantesUsadas[valorNumero] = nomeConst
                        secaoDados.append("    .align 3")
                        secaoDados.append("    " + nomeConst + ": .double " + valorNumero)

                    nomeReg = "D" + str(contadorRegistrador)
                    contadorRegistrador += 1
                    secaoTexto.append("    LDR R4, =" + nomeConst)
                    secaoTexto.append("    VLDR " + nomeReg + ", [R4]        @ carrega double " + valorNumero)
                    pilhaRegistradores.append(nomeReg)

                # Operador: desempilha 2 registradores, opera, empilha resultado
                elif token.tipo == "OPERADOR":
                    if len(pilhaRegistradores) < 2:
                        secaoTexto.append("    @ ERRO: operandos insuficientes para '" + token.valor + "'")
                        continue

                    regB = pilhaRegistradores.pop()
                    regA = pilhaRegistradores.pop()
                    regResultado = "D" + str(contadorRegistrador)
                    contadorRegistrador += 1

                    if token.valor == "+":
                        secaoTexto.append("    VADD.F64 " + regResultado + ", " + regA + ", " + regB + "    @ " + regA + " + " + regB)

                    elif token.valor == "-":
                        secaoTexto.append("    VSUB.F64 " + regResultado + ", " + regA + ", " + regB + "    @ " + regA + " - " + regB)

                    elif token.valor == "*":
                        secaoTexto.append("    VMUL.F64 " + regResultado + ", " + regA + ", " + regB + "    @ " + regA + " * " + regB)

                    elif token.valor == "/":
                        secaoTexto.append("    VDIV.F64 " + regResultado + ", " + regA + ", " + regB + "    @ " + regA + " / " + regB)

                    elif token.valor == "//":
                        secaoTexto.append("    @ divisao inteira: " + regA + " // " + regB)
                        secaoTexto.append("    VDIV.F64 " + regResultado + ", " + regA + ", " + regB)
                        secaoTexto.append("    VCVT.S32.F64 S31, " + regResultado + "    @ trunca para inteiro em temp S31")
                        secaoTexto.append("    VCVT.F64.S32 " + regResultado + ", S31    @ volta para double")

                    elif token.valor == "%":
                        secaoTexto.append("    @ resto: " + regA + " % " + regB)
                        secaoTexto.append("    VDIV.F64 " + regResultado + ", " + regA + ", " + regB + "    @ quociente double")
                        secaoTexto.append("    VCVT.S32.F64 S31, " + regResultado + "    @ trunca para inteiro em temp S31")
                        secaoTexto.append("    VCVT.F64.S32 " + regResultado + ", S31    @ quociente inteiro como double")
                        secaoTexto.append("    VMUL.F64 " + regResultado + ", " + regResultado + ", " + regB + "    @ quociente * divisor")
                        secaoTexto.append("    VSUB.F64 " + regResultado + ", " + regA + ", " + regResultado + "    @ resto = dividendo - quociente * divisor")

                    elif token.valor == "^":
                        nomeLabel = "potencia" + str(contadorLabel)
                        contadorLabel += 1
                        secaoTexto.append("    @ potenciacao: " + regA + " ^ " + regB + " (loop com VMUL)")
                        secaoTexto.append("    VCVT.S32.F64 S31, " + regB)
                        secaoTexto.append("    VMOV R0, S31              @ R0 = expoente (inteiro)")
                        secaoTexto.append("    @ inicializa resultado com 1.0")
                        if "1.0" in constantesUsadas:
                            nomeConst1 = constantesUsadas["1.0"]
                        else:
                            nomeConst1 = "const_1_0"
                            constantesUsadas["1.0"] = nomeConst1
                            secaoDados.append("    .align 3")
                            secaoDados.append("    " + nomeConst1 + ": .double 1.0")
                        secaoTexto.append("    LDR R4, =" + nomeConst1)
                        secaoTexto.append("    VLDR " + regResultado + ", [R4]    @ resultado = 1.0")
                        secaoTexto.append(nomeLabel + ":")
                        secaoTexto.append("    CMP R0, #0")
                        secaoTexto.append("    BLE " + nomeLabel + "_fim")
                        secaoTexto.append(
                            "    VMUL.F64 "
                            + regResultado
                            + ", "
                            + regResultado
                            + ", "
                            + regA
                        )
                        secaoTexto.append("    SUB R0, R0, #1")
                        secaoTexto.append("    B " + nomeLabel)
                        secaoTexto.append(nomeLabel + "_fim:")

                    pilhaRegistradores.append(regResultado)

                # Memoria: store (pilha com valor) ou load (pilha vazia)
                elif token.tipo == "MEMORIA":
                    nomeMem = token.valor
                    nomeLabel = "mem_" + nomeMem

                    if nomeLabel not in labelsMemoria:
                        secaoDados.append("    .align 3")
                        secaoDados.append("    " + nomeLabel + ": .double 0.0")
                        labelsMemoria.add(nomeLabel)

                    if len(pilhaRegistradores) > 0:
                        # Store: valor da pilha vai para memória
                        regValor = pilhaRegistradores.pop()
                        secaoTexto.append("    LDR R0, =" + nomeLabel + "        @ store em " + nomeMem)
                        secaoTexto.append("    VSTR " + regValor + ", [R0]")
                    else:
                        # Load: valor da memória vai para registrador
                        regCarregado = "D" + str(contadorRegistrador)
                        contadorRegistrador += 1
                        secaoTexto.append("    LDR R0, =" + nomeLabel + "        @ load de " + nomeMem)
                        secaoTexto.append("    VLDR " + regCarregado + ", [R0]")
                        pilhaRegistradores.append(regCarregado)

                # RES: acessa histórico de resultados
                elif token.tipo == "KEYWORD_RES":
                    if len(pilhaRegistradores) < 1:
                        secaoTexto.append("    @ ERRO: falta N para RES")
                        continue

                    regN = pilhaRegistradores.pop()
                    regResultado = "D" + str(contadorRegistrador)
                    contadorRegistrador += 1

                    secaoTexto.append("    @ RES: acessa resultado anterior")
                    secaoTexto.append("    VCVT.S32.F64 S31, " + regN)
                    secaoTexto.append("    VMOV R0, S31              @ R0 = N")
                    secaoTexto.append("    LDR R1, =resultados")
                    secaoTexto.append("    LDR R2, =numResultados")
                    secaoTexto.append("    LDR R2, [R2]")
                    secaoTexto.append("    SUB R2, R2, R0              @ indice = total - N")
                    secaoTexto.append("    LSL R2, R2, #3              @ offset em bytes (double = 8)")
                    secaoTexto.append("    ADD R1, R1, R2")
                    secaoTexto.append("    VLDR " + regResultado + ", [R1]")
                    pilhaRegistradores.append(regResultado)

        if len(pilhaRegistradores) == 1:
            regFinal = pilhaRegistradores.pop()
            secaoTexto.append("    @ Armazena resultado no historico")
            secaoTexto.append("    LDR R0, =numResultados")
            secaoTexto.append("    LDR R1, [R0]                @ R1 = numResultados atual")
            secaoTexto.append("    LDR R2, =resultados")
            secaoTexto.append("    LSL R3, R1, #3              @ offset = R1 * 8 (double = 8 bytes)")
            secaoTexto.append("    ADD R2, R2, R3")
            secaoTexto.append("    VSTR " + regFinal + ", [R2]               @ guarda resultado no array")
            secaoTexto.append("    ADD R1, R1, #1")
            secaoTexto.append("    STR R1, [R0]                @ numResultados++")

    # Sempre adiciona resultados e numResultados ao .data (necessario para historico)
    secaoDados.append("    .align 3")
    secaoDados.append("    resultados: .space 800       @ espaco para 100 doubles")
    secaoDados.append("    numResultados: .word 0")

    secaoTexto.append("")
    secaoTexto.append("    @ Fim do programa")
    secaoTexto.append("fim:")
    secaoTexto.append("    B fim")

    # Monta o código Assembly completo
    codigoAssembly.append(".global _start")
    codigoAssembly.append("")
    codigoAssembly.append(".data")
    for linha in secaoDados:
        codigoAssembly.append(linha)
    codigoAssembly.append("")
    codigoAssembly.append(".text")
    codigoAssembly.append("_start:")
    for linha in secaoTexto:
        codigoAssembly.append(linha)

# Exibe os resultados formatados
def exibirResultados(exibicao):
    print("\nResultados das expressoes (CPULATOR)")

    if not exibicao:
        print("Nenhum resultado para exibir.")
        return

    for num_linha, valor in exibicao:
        if valor is None:
            print(f"Linha {num_linha}: ---")
        elif isinstance(valor, str):  # Se for string, imprime direto -> texto de MEM
            print(f"Linha {num_linha}: {valor}")
        else: # Se for número, imprime com uma casa decimal
            print(f"Linha {num_linha}: {valor:.1f}")
    print("\n")

# Salva uma lista de linhas em um arquivo
def salvarArquivo(nome, linhas):
    try:
        with open(nome, "w") as f:
            for linha in linhas:
                f.write(linha + "\n")
        print(f"Arquivo {nome} salvo com sucesso.\n")
    except Exception as e:
        print(f"Erro ao salvar arquivo {nome}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python analisador.py <arquivo_teste>")
        return

    from funcoesTesteLexico import iniciarTestes

    iniciarTestes()

    nomeArquivo = sys.argv[1]
    linhas = []
    lerArquivo(nomeArquivo, linhas)

    resultados = []  # historico de resultados para RES
    memoria = {}  # dicionario de variaveis para MEM
    listaTokens = []  # acumula tokens de todas as linhas

    exibicao = []  # lista de tuplas (num_linha, valor) para exibir os resultados

    for i, linha in enumerate(linhas):
        vetorTokens = []
        parseExpressao(linha, vetorTokens)
        listaTokens.append(vetorTokens)

        grupos = resolverAninhamento(vetorTokens)
        if grupos is None:
            exibicao.append((i + 1, None))
            continue

        res = executarExpressao(vetorTokens, resultados, memoria)
        exibicao.append((i + 1, res))

    exibirResultados(exibicao)

    # Exporta tokens para tokens.txt - diferente do linhasTokens que é uma lista de listas de tokens
    linhasTokens = []
    for expressao in listaTokens:
        tokens_formatados = []
        for t in expressao:
            tokens_formatados.append(f"{t.tipo}:{t.valor}")
        
        # Junta os tokens daquela linha com um espaço entre eles
        linha_completa = " ".join(tokens_formatados)
        linhasTokens.append(linha_completa)
        
    salvarArquivo("tokens.txt", linhasTokens)

    codigoAssembly = []
    gerarAssembly(listaTokens, codigoAssembly)

    nomeAssembly = nomeArquivo.replace(".txt", ".s")
    salvarArquivo(nomeAssembly, codigoAssembly)

if __name__ == "__main__":
    main()