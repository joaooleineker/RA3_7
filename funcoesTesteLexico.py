# Integrantes do grupo (ordem alfabética):
# Daniel de Almeida Santos Bina - danielbina
# Eduardo Ferreira de Melo - edufmelo
# João Eduardo Faccin Leineker - joaooleineker
#
# Nome do grupo no Canvas: RA3_7

from lexico import (
    parseExpressao,
    executarExpressao,
    resolverAninhamento,
    gerarAssembly,
)

def testarAnalisadorLexico():
    print("=" * 50)
    print("Testes do analisador lexico\n")

    # Cada caso tem: (descrição, entrada, True se valido / False se invalido)
    casos = [
        # Casos válidos
        ("Adicao simples", "(3.0 2.0 +)", True),
        ("Subtracao simples", "(5.0 1.0 -)", True),
        ("Multiplicacao simples", "(3.0 4.0 *)", True),
        ("Divisao real", "(10.0 2.0 |)", True),
        ("Divisao inteira", "(10 3 /)", True),
        ("Resto", "(10 3 %)", True),
        ("Potenciacao", "(2.0 8 ^)", True),

        ("Expressao aninhada", "((2.0 3.0 *) 4.0 +)", True),
        ("Comando RES", "(2 RES)", True),
        ("Comando store MEM", "(5.0 X)", True),
        ("Comando load MEM", "(X)", True),
        # Casos inválidos
        ("Numero malformado", "(3.14.5 2.0 +)", False),
        ("Separador virgula", "(3,14 2.0 +)", False),
        ("Operador invalido", "(3.0 2.0 &)", False),
        ("Identificador minusculo", "(3.0 var +)", False),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, entrada, esperaValido in casos:
        tokens = []
        parseExpressao(entrada, tokens)

        temErro = any(t.tipo == "ERRO" for t in tokens)

        # O teste passa se:
        # - esperava válido e não tem erro
        # - esperava inválido e tem erro
        passou = (esperaValido and not temErro) or (not esperaValido and temErro)

        if passou:
            aprovados += 1
        else:
            reprovados += 1

    print("Resultado: " + str(aprovados) + " aprovados, " + str(reprovados) + " reprovados")
    print("=" * 50 + "\n")

def testarExecutarExpressao():
    print("=" * 50)
    print("Testes do executar expressao\n")

    memoria = {}

    # Teste 1 - (1 RES) deve retornar 20.0
    resultados1 = []
    tokens1 = []
    parseExpressao("(3.14 2.0 +)", tokens1)
    executarExpressao(tokens1, resultados1, memoria)  # resultados1 = [5.14]

    tokens2 = []
    parseExpressao("(10.0 2.0 *)", tokens2)
    executarExpressao(tokens2, resultados1, memoria)  # resultados1 = [5.14, 20.0]

    tokens3 = []
    parseExpressao("(1 RES)", tokens3)
    resultado = executarExpressao(tokens3, resultados1, memoria)
    passou = resultado == 20.0
    print(("OK" if passou else "FALHOU") + " | (1 RES) deve retornar 20.0, retornou: " + str(resultado))

    # Teste 2 - (2 RES) deve retornar 5.14 → histórico separado!
    resultados2 = []
    tokens4 = []
    parseExpressao("(3.14 2.0 +)", tokens4)
    executarExpressao(tokens4, resultados2, memoria)  # resultados2 = [5.14]

    tokens5 = []
    parseExpressao("(10.0 2.0 *)", tokens5)
    executarExpressao(tokens5, resultados2, memoria)  # resultados2 = [5.14, 20.0]

    tokens6 = []
    parseExpressao("(2 RES)", tokens6)
    resultado = executarExpressao(tokens6, resultados2, memoria)
    passou = abs(resultado - 5.14) < 0.001
    print(("OK" if passou else "FALHOU") + " | (2 RES) deve retornar 5.14, retornou: " + str(resultado))

    # Teste 3 - store e load de memoria
    resultados3 = []
    tokens7 = []
    parseExpressao("(9.0 CONT)", tokens7)
    executarExpressao(tokens7, resultados3, memoria)

    tokens8 = []
    parseExpressao("(CONT)", tokens8)
    resultado = executarExpressao(tokens8, resultados3, memoria)
    passou = resultado == 9.0
    print(("OK" if passou else "FALHOU") + " | (CONT) deve retornar 9.0, retornou: " + str(resultado))
    print("=" * 50 + "\n")

def testarResolverAninhamento():
    print("=" * 50)
    print("Testes do resolver aninhamento\n")

    # ((2.0 3.0 *) 4.0 +) deve gerar 2 grupos:
    # grupo 1: [NUMERO(2.0), NUMERO(3.0), OPERADOR(*)]
    # grupo 2: [NUMERO(4.0), OPERADOR(+)]
    tokens = []
    parseExpressao("((2.0 3.0 *) 4.0 +)", tokens)
    grupos = resolverAninhamento(tokens)

    print("Entrada: ((2.0 3.0 *) 4.0 +)")
    print("Grupos encontrados: " + str(len(grupos)))
    for i, grupo in enumerate(grupos):
        textoGrupo = "["
        for j, t in enumerate(grupo):
            textoGrupo += "(" + t.tipo + ", " + t.valor + ")"
            if j < len(grupo) - 1:
                textoGrupo += ", "
        textoGrupo += "]"
        print("  Grupo " + str(i) + ": " + textoGrupo)

    passou = len(grupos) == 2
    print(("OK" if passou else "FALHOU") + " | deve ter 2 grupos")
    print("=" * 50 + "\n")

def testarGerarAssembly():
    print("=" * 50)
    print("Testes da geracao de assembly\n")

    # Testa com todas as expressoes obrigatorias de uma vez
    entradas = [
        "(3.14 2.0 +)",
        "((1.5 2.0 *) (3.0 4.0 *) |)",
        "(5.0 MEM)",
        "(MEM)",
        "(2 RES)",
        "(10 3 /)",
        "(10 3 %)",
        "(2.0 8 ^)",
    ]

    listaTokens = []
    for entrada in entradas:
        tokens = []
        parseExpressao(entrada, tokens)
        listaTokens.append(tokens)

    codigoAssembly = []
    gerarAssembly(listaTokens, codigoAssembly)

    # Verificacoes
    temGlobal = any(".global _start" in linha for linha in codigoAssembly)
    temSecaoDados = any(".data" in linha for linha in codigoAssembly)
    temSecaoTexto = any(".text" in linha for linha in codigoAssembly)
    temFim = any("B fim" in linha for linha in codigoAssembly)
    temLinhas = any("linha1:" in linha for linha in codigoAssembly)

    # Verifica deduplicacao de constantes (2.0 aparece varias vezes, deve ter so 1 label)
    contagem2_0 = sum(1 for linha in codigoAssembly if "const_2_0" in linha and ".double" in linha)
    deduplicou = contagem2_0 == 1

    testes = [
        ("Tem .global _start", temGlobal),
        ("Tem .data", temSecaoDados),
        ("Tem .text", temSecaoTexto),
        ("Tem B fim", temFim),
        ("Tem labels linha1:", temLinhas),
        ("Deduplicou constantes (2.0 aparece 1x no .data)", deduplicou),
    ]

    aprovados = 0
    reprovados = 0

    for descricao, passou in testes:
        if passou:
            aprovados += 1
            status = "OK"
        else:
            reprovados += 1
            status = "FALHOU"
        print(status + " | " + descricao)

    print("Resultado: " + str(aprovados) + " aprovados, " + str(reprovados) + " reprovados")
    print("=" * 50 + "\n")

def iniciarTestes():
    print("Realização dos testes:\n")
    testarAnalisadorLexico()
    testarExecutarExpressao()
    testarResolverAninhamento()
    testarGerarAssembly()


if __name__ == "__main__":
    iniciarTestes()
