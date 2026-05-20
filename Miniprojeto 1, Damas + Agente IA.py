# coding: utf-8
# Miniprojeto 1, Damas + Agente IA

import pygame
from pygame.locals import *
import copy
import random

pygame.init()

# VARIÁVEIS DE VALOR CONSTANTE
LARGURA = 800
ALTURA = 600

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA = (100, 100, 100)
VERMELHO = (120, 0, 0)
VERDE_ESCURO = (0, 120, 0)
VERDE_CLARO = (0, 255, 0)
VERMELHO_CLARO = (255, 0, 0)
AZUL = (0, 0, 255)
COR_FUNDO = (54, 54, 54)
COR_TABULEIRO = (0, 31, 0)

# INICIANDO PROGRAMAÇÃO DO DISPLAY
display = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Jogo de Damas com IA')
pygame.font.init()
clock = pygame.time.Clock()

class Jogo:
    def __init__(self, modo='PvP'):
        self.status = 'Jogando'
        self.turno = 1
        self.jogadores = ('x', 'o')
        self.modo_de_jogo = modo  # 'PvP' ou 'PvE'
        self.cedula_selecionada = None
        self.pulando = False
        self.matriz_jogadores = [['x','-','x','-','x','-','x','-'],
                                 ['-','x','-','x','-','x','-','x'],
                                 ['x','-','x','-','x','-','x','-'],
                                 ['-','-','-','-','-','-','-','-'],
                                 ['-','-','-','-','-','-','-','-'],
                                 ['-','o','-','o','-','o','-','o'],
                                 ['o','-','o','-','o','-','o','-'],
                                 ['-','o','-','o','-','o','-','o']]

    def avalia_clique(self, pos):
        if self.modo_de_jogo == 'PvE' and self.jogadores[self.turno % 2] == 'x':
            return

        turno = self.turno % 2
        if self.status == "Jogando":
            linha, coluna = linha_clicada(pos), coluna_clicada(pos)
            if self.cedula_selecionada:
                movimento = self.is_movimento_valido(self.jogadores[turno], self.cedula_selecionada, linha, coluna)
                if movimento[0]:
                    self.jogar(self.jogadores[turno], self.cedula_selecionada, linha, coluna, movimento[1])
                elif linha == self.cedula_selecionada[0] and coluna == self.cedula_selecionada[1]:
                    movs = self.movimento_obrigatorio(self.cedula_selecionada)
                    if movs[0] == []:
                        if self.pulando:
                            self.pulando = False
                            self.proximo_turno()
                    self.cedula_selecionada = None
            else:
                if self.matriz_jogadores[linha][coluna].lower() == self.jogadores[turno]:
                    self.cedula_selecionada = [linha, coluna]

    def is_movimento_valido(self, jogador, localizacao_cedula, linha_destino, coluna_destino):
        linha_originaria = localizacao_cedula[0]
        coluna_originaria = localizacao_cedula[1]
        obrigatorios = self.todos_obrigatorios()

        if obrigatorios != {}:
            if (linha_originaria, coluna_originaria) not in obrigatorios:
                return False, None
            elif [linha_destino, coluna_destino] not in obrigatorios[(linha_originaria, coluna_originaria)]:
                return False, None

        movimento, pulo = self.movimentos_possiveis(localizacao_cedula)
        if [linha_destino, coluna_destino] in movimento:
            if pulo:
                if len(pulo) == 1:
                    return True, pulo[0]
                else:
                    for i in range(len(pulo)):
                        if abs(pulo[i][0] - linha_destino) == 1 and abs(pulo[i][1] - coluna_destino) == 1:
                            return True, pulo[i]
            if self.pulando:
                return False, None
            return True, None
        return False, None

    def todos_obrigatorios(self):
        todos = {}
        for r in range(len(self.matriz_jogadores)):
            for c in range(len(self.matriz_jogadores[r])):
                ob, pulos = self.movimento_obrigatorio((r, c))
                if ob != []:
                    todos[(r, c)] = ob
        return todos
        
    def existe_possivel(self):
        for l in range(len(self.matriz_jogadores)):
            for c in range(len(self.matriz_jogadores[l])):
                if self.movimentos_possiveis((l, c))[0]:
                    return True
        return False

    def movimento_obrigatorio(self, localizacao_cedula):
        obrigatorios = []
        posicao_cedula_pulada = []

        l = localizacao_cedula[0]
        c = localizacao_cedula[1]

        jogador = self.jogadores[self.turno % 2]
        index = self.jogadores.index(jogador)
        array = [jogador.lower(), jogador.upper(), '-']

        if self.matriz_jogadores[l][c].islower() and self.matriz_jogadores[l][c] == jogador and self.turno % 2 == index:
            if l > 0:
                if c < 7:
                    if self.matriz_jogadores[l - 1][c + 1].lower() not in array:
                        l_x = l - 1
                        l_c = c + 1
                        if l_x - 1 >= 0 and l_c + 1 <= 7:
                            if self.matriz_jogadores[l_x - 1][l_c + 1] == '-':
                                obrigatorios.append([l_x - 1, l_c + 1])
                                posicao_cedula_pulada.append((l_x, l_c))
                if c > 0:
                    if self.matriz_jogadores[l - 1][c - 1].lower() not in array:
                        l_x = l - 1
                        l_c = c - 1
                        if l_x - 1 >= 0 and l_c - 1 >= 0:
                            if self.matriz_jogadores[l_x - 1][l_c - 1] == '-':
                                obrigatorios.append([l_x - 1, l_c - 1])
                                posicao_cedula_pulada.append((l_x, l_c))
            if l < 7:
                if c < 7:
                    if self.matriz_jogadores[l + 1][c + 1].lower() not in array:
                        l_x = l + 1
                        l_c = c + 1
                        if l_x + 1 <= 7 and l_c + 1 <= 7:
                            if self.matriz_jogadores[l_x + 1][l_c + 1] == '-':
                                obrigatorios.append([l_x + 1, l_c + 1])
                                posicao_cedula_pulada.append((l_x, l_c))
                if c > 0:
                    if self.matriz_jogadores[l + 1][c - 1].lower() not in array:
                        l_x = l + 1
                        l_c = c - 1
                        if l_x + 1 <= 7 and l_c - 1 >= 0:
                            if self.matriz_jogadores[l_x + 1][l_c - 1] == '-':
                                obrigatorios.append([l_x + 1, l_c - 1])
                                posicao_cedula_pulada.append((l_x, l_c))

        elif self.matriz_jogadores[l][c].isupper() and self.matriz_jogadores[l][c] == jogador.upper() and self.turno % 2 == index:
            if not self.pulando and (jogador.lower() == 'x' and l != 7) or (jogador.lower() == 'o' and l != 0):
                conta_linha = l
                conta_coluna = c
                while True:
                    if conta_linha - 1 < 0 or conta_coluna - 1 < 0: break
                    else:
                        if self.matriz_jogadores[conta_linha - 1][conta_coluna - 1] not in array:
                            l_x = conta_linha - 1
                            l_c = conta_coluna - 1
                            if l_x - 1 >= 0 and l_c - 1 >= 0:
                                if self.matriz_jogadores[l_x - 1][l_c - 1] == '-':
                                    posicao_cedula_pulada.append((l_x, l_c))
                                    while True:
                                        if l_x - 1 < 0 or l_c - 1 < 0: break
                                        else:
                                            if self.matriz_jogadores[l_x - 1][l_c - 1] == '-':
                                                obrigatorios.append([l_x - 1, l_c - 1])
                                            else: break
                                        l_x -= 1
                                        l_c -= 1
                            break
                    conta_linha -= 1
                    conta_coluna -= 1

                conta_linha = l
                conta_coluna = c
                while True:
                    if conta_linha - 1 < 0 or conta_coluna + 1 > 7: break
                    else:
                        if self.matriz_jogadores[conta_linha - 1][conta_coluna + 1] not in array:
                            l_x = conta_linha - 1
                            l_c = conta_coluna + 1
                            if l_x - 1 >= 0 and l_c + 1 <= 7:
                                if self.matriz_jogadores[l_x - 1][l_c + 1] == '-':
                                    posicao_cedula_pulada.append((l_x, l_c))
                                    while True:
                                        if l_x - 1 < 0 or l_c + 1 > 7: break
                                        else:
                                            if self.matriz_jogadores[l_x - 1][l_c + 1] == '-':
                                                obrigatorios.append([l_x - 1, l_c + 1])
                                            else: break
                                        l_x -= 1
                                        l_c += 1
                            break
                    conta_linha -= 1
                    conta_coluna += 1

                conta_linha = l
                conta_coluna = c
                while True:
                    if conta_linha + 1 > 7 or conta_coluna + 1 > 7: break
                    else:
                        if self.matriz_jogadores[conta_linha + 1][conta_coluna + 1] not in array:
                            l_x = conta_linha + 1
                            l_c = conta_coluna + 1
                            if l_x + 1 <= 7 and l_c + 1 <= 7:
                                if self.matriz_jogadores[l_x + 1][l_c + 1] == '-':
                                    posicao_cedula_pulada.append((l_x, l_c))
                                    while True:
                                        if l_x + 1 > 7 or l_c + 1 > 7: break
                                        else:
                                            if self.matriz_jogadores[l_x + 1][l_c + 1] == '-':
                                                obrigatorios.append([l_x + 1, l_c + 1])
                                            else: break
                                        l_x += 1
                                        l_c += 1
                            break
                    conta_linha += 1
                    conta_coluna += 1

                conta_linha = l
                conta_coluna = c
                while True:
                    if conta_linha + 1 > 7 or conta_coluna - 1 < 0: break
                    else:
                        if self.matriz_jogadores[conta_linha + 1][conta_coluna - 1] not in array:
                            l_x = conta_linha + 1
                            l_c = conta_coluna - 1
                            if l_x + 1 <= 7 and l_c - 1 >= 0:
                                if self.matriz_jogadores[l_x + 1][l_c - 1] == '-':
                                    posicao_cedula_pulada.append((l_x, l_c))
                                    while True:
                                        if l_x + 1 > 7 or l_c - 1 < 0: break
                                        else:
                                            if self.matriz_jogadores[l_x + 1][l_c - 1] == '-':
                                                obrigatorios.append([l_x + 1, l_c - 1])
                                            else: break
                                        l_x += 1
                                        l_c -= 1
                            break
                    conta_linha += 1
                    conta_coluna -= 1

        return obrigatorios, posicao_cedula_pulada

    def movimentos_possiveis(self, localizacao_cedula):
        movimentos, pulos = self.movimento_obrigatorio(localizacao_cedula)

        if movimentos == []:
            linha_atual = localizacao_cedula[0]
            coluna_atual = localizacao_cedula[1]

            if self.matriz_jogadores[linha_atual][coluna_atual].islower():
                if self.matriz_jogadores[linha_atual][coluna_atual] == 'o':
                    if linha_atual > 0:
                        if coluna_atual < 7:
                            if self.matriz_jogadores[linha_atual - 1][coluna_atual + 1] == '-':
                                movimentos.append([linha_atual - 1, coluna_atual + 1])
                        if coluna_atual > 0:
                            if self.matriz_jogadores[linha_atual - 1][coluna_atual - 1] == '-':
                                movimentos.append([linha_atual - 1, coluna_atual - 1])
                elif self.matriz_jogadores[linha_atual][coluna_atual] == 'x':
                    if linha_atual < 7:
                        if coluna_atual < 7:
                            if self.matriz_jogadores[linha_atual + 1][coluna_atual + 1] == '-':
                                movimentos.append([linha_atual + 1, coluna_atual + 1])
                        if coluna_atual > 0:
                            if self.matriz_jogadores[linha_atual + 1][coluna_atual - 1] == '-':
                                movimentos.append(