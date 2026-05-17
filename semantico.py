# Integrantes do grupo (ordem alfabética):
# Daniel de Almeida Santos Bina - danielbina
# Eduardo Ferreira de Melo - edufmelo
# João Eduardo Faccin Leineker - joaooleineker
#
# Nome do grupo no Canvas: RA3_7

import sys

from lexico import lerArquivo
from sintatico import construirGramatica, gerarTokens, lerTokens, parsear, gerarArvore

def prepararEntradaSemantica(nome_arquivo):
    linhas_arquivo = []
    lerArquivo(nome_arquivo, linhas_arquivo)
    
    print("Arquivo carregado com sucesso.")
    print("Quantidade de linhas:", len(linhas_arquivo))

    # Utilizando as funções criadas no sintático
    gerarTokens(linhas_arquivo)
    tokens = lerTokens("tokens.txt")

    # Valida se o programa começa com (START) e termina com (END)
    erros = validarInicioFimPrograma(tokens)
    if len(erros) > 0:
        for erro in erros:
            print(erro)

        return tokens, None

    resultado_gramatica = construirGramatica()
    derivacao = parsear(tokens, resultado_gramatica["tabela_ll1"])
    arvore_sintatica_inicial = gerarArvore(derivacao, nome_arquivo)

    return tokens, arvore_sintatica_inicial

def validarInicioFimPrograma(tokens):
    erros = []

    if len(tokens) == 0:
        erros.append("Erro: programa vazio.")
        return erros

    primeira_linha = tokens[0]
    ultima_linha = tokens[-1]

    inicio_valido = (
        len(primeira_linha) == 3
        and primeira_linha[0].tipo == "ABRE_PAREN"
        and primeira_linha[1].tipo == "KEYWORD_START"
        and primeira_linha[2].tipo == "FECHA_PAREN"
    )

    fim_valido = (
        len(ultima_linha) == 3
        and ultima_linha[0].tipo == "ABRE_PAREN"
        and ultima_linha[1].tipo == "KEYWORD_END"
        and ultima_linha[2].tipo == "FECHA_PAREN"
    )

    if not inicio_valido:
        erros.append("Erro: o programa deve comecar com (START).")

    if not fim_valido:
        erros.append("Erro: o programa deve terminar com (END).")

    return erros

def construirTabelaSimbolos(arvore_sintatica):
    pass

def verificarTipos(arvore_sintatica, tabela_simbolos):
    pass

def gerarArvoreAtribuida(arvore_sintatica, tabela_simbolos):
    pass

def gerarAssembly(arvore_atribuida):
    pass

def possuiErroLexico(tokens):
    for linha_tokens in tokens:
        for token in linha_tokens:
            if token.tipo == "ERRO" or token.tipo == "LINHA_INVALIDA":
                return True

    return False

def possuiErroSintatico(no):
    # Caso não exista árvore
    if no is None:
        return True

    if not isinstance(no, dict):
        return False

    # Procura erros na árvore
    if (
        no.get("nodo_pai") == "comando_descartado"
        or "erro" in no
        or "erro_sintatico" in no
        or "erro_nodo_pai" in no
    ):
        return True

    for filho in no.get("nodos_filhos", []):
        if possuiErroSintatico(filho):
            return True

    return False

def executarAnaliseSemantica(nome_arquivo):
    tokens, arvore_sintatica_inicial = prepararEntradaSemantica(nome_arquivo)

    # Reportar erros léxicos antes da etapa semântica
    if possuiErroLexico(tokens):
        print("Análise semântica interrompida: foram encontrados erros léxicos.")
        return

    # Reportar erros sintáticos antes da etapa semântica
    if possuiErroSintatico(arvore_sintatica_inicial):
        print("Análise semântica interrompida: foram encontrados erros sintáticos.")
        return

    # construirTabelaSimbolos(arvore_sintatica_inicial)
    # verificarTipos(arvore_sintatica_inicial, tabela_simbolos)
    # gerarArvoreAtribuida(...)
    # gerarAssembly(...)

    print("Analisador semântico iniciado.")

def main():
    if len(sys.argv) < 2:
        print("Uso: python semantico.py <arquivo_teste>")
        return

    nome_arquivo = sys.argv[1]
    executarAnaliseSemantica(nome_arquivo)

if __name__ == "__main__":
    main()

