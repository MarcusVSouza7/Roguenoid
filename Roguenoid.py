import pygame
import sys
import random

# Inicializa todos os módulos do Pygame necessários para o funcionamento (vídeo, fontes, etc.)
pygame.init()

# =====================================================================
# CONFIGURAÇÕES GERAIS E CONSTANTES
# =====================================================================
LARGURA_TELA, ALTURA_TELA = 800, 600
# Taxa de quadros fixada em 60 para garantir que a física e a velocidade do jogo sejam consistentes em qualquer computador em que for executado
FPS = 60 

# Paleta de cores centralizada para facilitar alterações de design
# O uso de um dicionário mantém o código limpo e evita "magic numbers" no código
CORES = {
    "fundo": (15, 15, 25),
    "branco": (255, 255, 255),
    "barra": (0, 255, 255),      
    "bola": (255, 255, 255),     
    "texto": (220, 220, 220),
    "hp1": (255, 50, 150),       # Rosa: Indica blocos a 1 hit de serem destruídos
    "hp2": (200, 255, 0),        # Amarelo: Blocos com 2 hits
    "hp3": (0, 255, 150),        # Verde: Blocos com 3 hits
    "alerta": (255, 50, 50)      # Vermelho: Destaque para fim de jogo
}

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Roguenoid - Pygame Project")

# Fontes pré-carregadas. Usar 'Consolas' garante espaçamento monoespaçado
# o que evita que o texto fique "tremendo" na tela quando a pontuação muda rapidamente
fonte_placar = pygame.font.SysFont('Consolas', 24, bold=True)
fonte_titulo = pygame.font.SysFont('Consolas', 64, bold=True)
fonte_instrucoes = pygame.font.SysFont('Consolas', 24)
fonte_upgrades = pygame.font.SysFont('Consolas', 18)

# =====================================================================
# CLASSES (ORIENTAÇÃO A OBJETOS)
# =====================================================================

class Barra:
    """Controla o jogador (paddle). Isolada em classe para facilitar upgrades na largura."""
    def __init__(self, largura=120):
        self.largura = largura
        self.altura = 15
        self.velocidade = 8
        self.resetar_posicao()

    def resetar_posicao(self):
        # Centraliza a barra no eixo X e a fixa perto da base no eixo Y
        self.rect = pygame.Rect((LARGURA_TELA - self.largura) // 2, ALTURA_TELA - 40, self.largura, self.altura)

    def mover(self, teclas):
        # A movimentação ocorre diretamente por teclas pressionadas no loop (get_pressed),
        # decisão tomada para garantir movimento contínuo e fluido, diferente do evento KEYDOWN.
        if teclas[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocidade
        if teclas[pygame.K_RIGHT] and self.rect.right < LARGURA_TELA:
            self.rect.x += self.velocidade

    def desenhar(self, superficie):
        pygame.draw.rect(superficie, CORES["barra"], self.rect, border_radius=5)

class Bola:
    """Gerencia a física, colisões com paredes e posições precisas."""
    def __init__(self, x, y, vel_base=5.0, dano=1):
        self.raio = 8
        self.vel_base = vel_base
        self.dano = dano 
        self.rect = pygame.Rect(x, y, self.raio*2, self.raio*2)
        
        # DECISÃO TÉCNICA IMPORTANTE: 
        # Como a velocidade aumenta gradativamente a cada nível (ex: +0.3), usar apenas inteiros (rect.x/y)
        # faria o jogo arredondar valores e ignorar as casas decimais. Usar variáveis em float 
        # (pos_x, pos_y) garante que os incrementos fracionários funcionem corretamente.
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.vel_x = self.vel_base * random.choice([-1, 1])
        self.vel_y = self.vel_base # Começa movendo-se para baixo (Y positivo no Pygame)

    def mover(self):
        # 1. Atualiza a precisão matemática (float)
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        
        # 2. Converte para o motor de colisão e renderização (int)
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

        # Lógica de bounce nas bordas da tela:
        if self.rect.left <= 0:
            self.rect.left = 0
            self.pos_x = float(self.rect.x) # Ressincroniza o float para evitar bugs visuais
            self.vel_x = abs(self.vel_x)    # Força velocidade para a direita (+)
            
        elif self.rect.right >= LARGURA_TELA:
            self.rect.right = LARGURA_TELA
            self.pos_x = float(self.rect.x)
            self.vel_x = -abs(self.vel_x)   # Força velocidade para a esquerda (-)
            
        if self.rect.top <= 0:
            self.rect.top = 0
            self.pos_y = float(self.rect.y)
            self.vel_y = abs(self.vel_y)    # Força descer (+)

    def desenhar(self, superficie):
        pygame.draw.circle(superficie, CORES["bola"], self.rect.center, self.raio)

class Bloco:
    """Entidade destrutível. Possui HP (Vida) que influencia sua cor."""
    def __init__(self, x, y, hp):
        self.rect = pygame.Rect(x, y, 65, 25)
        self.hp = hp

    def desenhar(self, superficie):
        # O feedback visual é alterado dinamicamente de acordo com o HP restante
        if self.hp >= 3: cor = CORES["hp3"]
        elif self.hp == 2: cor = CORES["hp2"]
        else: cor = CORES["hp1"]
            
        pygame.draw.rect(superficie, cor, self.rect, border_radius=3)


# =====================================================================
# FUNÇÕES DE GERAÇÃO E LÓGICA
# =====================================================================

def criar_blocos(nivel):
    """
    Gera a matriz de blocos. A dificuldade é progressiva:
    Quanto maior o nível, maior a chance de aparecerem blocos mais resistentes.
    """
    blocos = []
    # Limita o máximo de linhas a 8 para não invadir o espaço do jogador
    linhas = min(3 + (nivel // 2), 8) 
    
    for linha in range(linhas):
        for coluna in range(10): # Grade fixa de 10 colunas
            hp = 1
            # Decisão de design: a progressão é controlada por probabilidade aleatória, 
            # não sendo linear. Isso cria variabilidade entre as partidas (fator Roguelike).
            if nivel > 2 and random.random() < (0.1 * nivel): hp = 2
            if nivel > 5 and random.random() < (0.05 * nivel): hp = 3
            
            blocos.append(Bloco(50 + coluna * 70, 60 + linha * 35, hp))
    return blocos

def gerar_bola_segura(vel_global, dano):
    """Garante que novas bolas nasçam longe da barra e das paredes."""
    x_aleatorio = random.randint(100, LARGURA_TELA - 100)
    return Bola(x_aleatorio, 350, vel_global, dano)

# Lista de dicionários agindo como banco para os Upgrades
UPGRADES = [
    {"id": "largura", "nome": "Extensão Cyber", "desc": "Sua barra fica mais larga."},
    {"id": "multiball", "nome": "Fragmentação", "desc": "Adiciona +1 Bola simultânea."},
    {"id": "dano", "nome": "Força Bruta", "desc": "Bolas causam +1 de dano."},
    {"id": "vida", "nome": "Backup", "desc": "Ganha +1 Vida máxima."},
    {"id": "multiplicador", "nome": "Overclock", "desc": "Multiplicador Base de Pontos +1."}
]


# =====================================================================
# LOOP PRINCIPAL E MÁQUINA DE ESTADOS
# =====================================================================
def main():
    relogio = pygame.time.Clock()
    
    # DECISÃO: Máquina de Estados (State Machine). 
    # Permite alternar entre telas lógicas no mesmo loop while.
    # 1: Jogando (Gameplay ativo)
    # 2: Tela de Upgrade (Após limpar a fase)
    # 3: Tela de Game Over (Após perder vidas)
    estado_atual = 1 

    # Variáveis permanentes: Estas não resetam ao morrer, sendo a base do sistema Roguelike.
    status_permanentes = {
        "largura_barra": 120, "qtd_bolas": 1, "dano_bolas": 1, "vidas_max": 3, "multiplicador": 1
    }

    # Variáveis da partida (Voltam ao estado inicial no Game Over)
    pontuacao = 0
    nivel = 1
    vel_bola_global = 5.0
    
    # Inicialização das entidades para o primeiro jogo
    vidas = status_permanentes["vidas_max"]
    barra = Barra(status_permanentes["largura_barra"])
    bolas = [gerar_bola_segura(vel_bola_global, status_permanentes["dano_bolas"]) for _ in range(status_permanentes["qtd_bolas"])]
    blocos = criar_blocos(nivel)
    opcoes_atuais = []

    while True:
        tela.fill(CORES["fundo"])

        # PROCESSAMENTO DE EVENTOS GERAIS
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if evento.type == pygame.KEYDOWN:
                
                # TRANSIÇÃO DE ESTADO: Mudar de Fase (Escolher Upgrade)
                if estado_atual == 2: 
                    escolha = None
                    if evento.key == pygame.K_1: escolha = 0
                    elif evento.key == pygame.K_2: escolha = 1
                    elif evento.key == pygame.K_3: escolha = 2
                    
                    if escolha is not None:
                        upg = opcoes_atuais[escolha]["id"]
                        
                        # Aplica os atributos ao inventário permanente
                        if upg == "largura": status_permanentes["largura_barra"] += 30
                        elif upg == "multiball": status_permanentes["qtd_bolas"] += 1
                        elif upg == "dano": status_permanentes["dano_bolas"] += 1
                        elif upg == "vida": 
                            status_permanentes["vidas_max"] += 1
                            vidas += 1
                        elif upg == "multiplicador": status_permanentes["multiplicador"] += 1
                        
                        # Incrementa a dificuldade matemática do jogo
                        nivel += 1
                        vel_bola_global = min(10.0, vel_bola_global + 0.3) 
                        blocos = criar_blocos(nivel)
                        
                        # Sincroniza objetos em tela com os novos status
                        barra.largura = status_permanentes["largura_barra"]
                        barra.resetar_posicao()
                        bolas = [gerar_bola_segura(vel_bola_global, status_permanentes["dano_bolas"]) for _ in range(status_permanentes["qtd_bolas"])]
                        estado_atual = 1 # Retorna o foco para o Gameplay

                # Reiniciar após Game Over sem fechar
                elif estado_atual == 3 and evento.key == pygame.K_r:
                    pontuacao = 0
                    nivel = 1
                    vel_bola_global = 5.0
                    
                    # Reconstrói os objetos aproveitando os upgrades adquiridos
                    vidas = status_permanentes["vidas_max"]
                    barra = Barra(status_permanentes["largura_barra"])
                    bolas = [gerar_bola_segura(vel_bola_global, status_permanentes["dano_bolas"]) for _ in range(status_permanentes["qtd_bolas"])]
                    blocos = criar_blocos(nivel)
                    estado_atual = 1 


        # ESTADO 1: LÓGICA DE GAMEPLAY E COLISÕES
        if estado_atual == 1:
            teclas = pygame.key.get_pressed()
            barra.mover(teclas)

            # Usar uma cópia da lista (bolas[:]) permite remover uma bola da lista original
            # sem quebrar a iteração do loop for.
            for bola in bolas[:]:
                bola.mover()

                # COLISÃO: Bola x Barra
                # 'vel_y > 0' impede que a bola fique presa dentro da barra (só rebate se estiver caindo)
                if bola.rect.colliderect(barra.rect) and bola.vel_y > 0:
                    bola.vel_y = -bola.vel_y
                    
                    # DECISÃO: Física Direcional. A bola muda seu ângulo no eixo X
                    # baseado na distância entre o seu centro e o centro da barra.
                    # Bater nas bordas da barra envia a bola em ângulos mais rasantes, exigindo habilidade.
                    distancia_centro = bola.rect.centerx - barra.rect.centerx
                    bola.vel_x = distancia_centro * 0.15

                # COLISÃO: Bola x Blocos
                for bloco in blocos[:]:
                    if bola.rect.colliderect(bloco.rect):
                        bloco.hp -= bola.dano 
                        bola.vel_y = -bola.vel_y 
                        
                        # Gerenciamento de morte do bloco e pontuação
                        if bloco.hp <= 0:
                            blocos.remove(bloco)
                            pontuacao += (10 * status_permanentes["multiplicador"])
                        
                        # 'break' previne que uma bola atravesse e destrua múltiplos blocos no mesmo frame
                        break 

                # Condição de perda de bola
                if bola.rect.top > ALTURA_TELA:
                    bolas.remove(bola)

            # Lógica de Vidas e Transição para Game Over (Estado 3)
            if len(bolas) == 0:
                vidas -= 1
                if vidas <= 0:
                    estado_atual = 3 # REQUISITO: Tela clara de Game Over
                else:
                    barra.resetar_posicao()
                    bolas = [gerar_bola_segura(vel_bola_global, status_permanentes["dano_bolas"]) for _ in range(status_permanentes["qtd_bolas"])]

            # Condição de Vitória da Fase
            if len(blocos) == 0:
                estado_atual = 2
                opcoes_atuais = random.sample(UPGRADES, 3)

            # RENDERIZAÇÃO GRÁFICA (Toda a atualização visual do Gameplay ocorre aqui)
            barra.desenhar(tela)
            for bola in bolas: bola.desenhar(tela)
            for bloco in blocos: bloco.desenhar(tela)

            # REQUISITO ATENDIDO: Pontuação mostrada na própria janela
            tela.blit(fonte_placar.render(f"SCORE: {pontuacao}", True, CORES["texto"]), (20, 10))
            tela.blit(fonte_placar.render(f"VIDAS: {vidas}", True, CORES["hp3"]), (20, 40))
            tela.blit(fonte_placar.render(f"NÍVEL: {nivel}", True, CORES["barra"]), (LARGURA_TELA - 150, 10))


        # ESTADO 2: TELA DE UPGRADES
        elif estado_atual == 2:
            txt_titulo = fonte_titulo.render("UPGRADE", True, CORES["hp3"])
            tela.blit(txt_titulo, txt_titulo.get_rect(center=(LARGURA_TELA//2, 80)))
            
            txt_sub = fonte_instrucoes.render("Escolha o próximo Upgrade (1, 2 ou 3):", True, CORES["branco"])
            tela.blit(txt_sub, txt_sub.get_rect(center=(LARGURA_TELA//2, 140)))

            # Loop para gerar dinamicamente os botões de opções com espaçamento calculado
            for i, opcao in enumerate(opcoes_atuais):
                rect_carta = pygame.Rect(LARGURA_TELA//2 - 250, 220 + (i * 110), 500, 90)
                pygame.draw.rect(tela, (30, 30, 45), rect_carta, border_radius=10)
                pygame.draw.rect(tela, CORES["barra"], rect_carta, 2, border_radius=10)
                
                tela.blit(fonte_placar.render(str(i+1), True, CORES["hp2"]), (rect_carta.x + 20, rect_carta.y + 30))
                tela.blit(fonte_instrucoes.render(opcao['nome'], True, CORES["hp1"]), (rect_carta.x + 60, rect_carta.y + 20))
                tela.blit(fonte_upgrades.render(opcao['desc'], True, CORES["texto"]), (rect_carta.x + 60, rect_carta.y + 50))

        # ESTADO 3: TELA DE GAME OVER
        elif estado_atual == 3:
            txt_titulo = fonte_titulo.render("GAME OVER", True, CORES["alerta"])
            tela.blit(txt_titulo, txt_titulo.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 - 60)))
            
            txt_pontos = fonte_instrucoes.render(f"Nível alcançado: {nivel} | Score final: {pontuacao}", True, CORES["texto"])
            tela.blit(txt_pontos, txt_pontos.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 + 10)))
            
            txt_rogue = fonte_upgrades.render("Seus upgrades foram mantidos para a próxima tentativa!", True, CORES["hp3"])
            tela.blit(txt_rogue, txt_rogue.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 + 45)))
            
            txt_restart = fonte_instrucoes.render("> Pressione [R] para reiniciar", True, CORES["hp2"])
            tela.blit(txt_restart, txt_restart.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2 + 85)))

        # Sincroniza o hardware do monitor com as renderizações calculadas acima
        pygame.display.flip()
        relogio.tick(FPS)

if __name__ == "__main__":
    main()
