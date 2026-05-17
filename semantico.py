# Integrantes do grupo (ordem alfabética):
# Daniel de Almeida Santos Bina - danielbina
# Eduardo Ferreira de Melo - edufmelo
# João Eduardo Faccin Leineker - joaooleineker
#
# Nome do grupo no Canvas: RA3_7

import sys

from lexico import lerArquivo
#from sintatico import funcoesQueVamosUtilizar

def prepararEntradaSemantica(nome_arquivo):
    linhas_arquivo = []
    lerArquivo(nome_arquivo, linhas_arquivo)

    print("Arquivo carregado com sucesso.")
    print("Quantidade de linhas:", len(linhas_arquivo))

    return linhas_arquivo

def construirTabelaSimbolos(arvore_sintatica):
    pass

def verificarTipos(arvore_sintatica, tabela_simbolos):
    pass

def gerarArvoreAtribuida(arvore_sintatica, tabela_simbolos):
    pass

def gerarAssembly(arvore_atribuida):
    pass

def executarAnaliseSemantica(nome_arquivo):
    linhas_arquivo = prepararEntradaSemantica(nome_arquivo)

    # Devemos chamar o analisador lexico
    # Apos, devemos chamar o sintatico
    # Construir a tabela de simbolos
    # Depois, verificar tipos e gerar a arvore atribuida
    # Devemos gerar o assembly apenas se nao houver erros

    print("Analisador semântico iniciado.")

def main():
    if len(sys.argv) < 2:
        print("Uso: python semantico.py <arquivo_teste>")
        return

    nome_arquivo = sys.argv[1]
    executarAnaliseSemantica(nome_arquivo)

if __name__ == "__main__":
    main()

