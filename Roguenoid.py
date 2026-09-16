import pygame
import sys
import random

pygame.init()

# CONFIGURAÇÕES GERAIS E CONSTANTES
LARGURA_TELA, ALTURA_TELA = 800, 600
FPS = 60 # Define a taxa de quadros por segundo do jogo

# Dicionário contendo a paleta de cores do jogo (Padrão RGB)
CORES = {
    "fundo": (15, 15, 25),
    "branco": (255, 255, 255),
    "barra": (0, 255, 255),      # Ciano
    "bola": (255, 255, 255),     # Branco
    "texto": (220, 220, 220),
    "hp1": (255, 50, 150),       # Rosa (Blocos fracos)
    "hp2": (200, 255, 0),        # Amarelo (Blocos médios)
    "hp3": (0, 255, 150),        # Verde (Blocos fortes)
    "alerta": (255, 50, 50)      # Vermelho (Game Over)
}

# Configuração da janela principal do jogo
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Roguenoid")

# Carregamento das fontes usadas na interface (HUD e Menus)
fonte_placar = pygame.font.SysFont('Consolas', 24, bold=True)
fonte_titulo = pygame.font.SysFont('Consolas', 64, bold=True)
fonte_instrucoes = pygame.font.SysFont('Consolas', 24)
fonte_upgrades = pygame.font.SysFont('Consolas', 18)

# CLASSES DO JOGO
class Barra:
    def __init__(self, largura=120):
        self.largura = largura
        self.altura = 15
        self.velocidade = 8
        self.resetar_posicao()

    def resetar_posicao(self):
        self.rect = pygame.Rect((LARGURA_TELA - self.largura) // 2, ALTURA_TELA - 40, self.largura, self.altura)

    def mover(self, teclas):
        if teclas[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocidade
        if teclas[pygame.K_RIGHT] and self.rect.right < LARGURA_TELA:
            self.rect.x += self.velocidade

    def desenhar(self, superficie):
        pygame.draw.rect(superficie, CORES["barra"], self.rect, border_radius=5)

class Bola:
    def __init__(self, x, y, vel_base=5.0, dano=1):
        self.raio = 8
        self.vel_base = vel_base
        self.dano = dano # Quanto de vida (HP) a bola tira do bloco por batida
        self.rect = pygame.Rect(x, y, self.raio*2, self.raio*2)
        
        # Variáveis float para garantir aumento progressivo de velocidade
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        # Sorteia se a bola começa indo para a esquerda (-1) ou direita (1)
        self.vel_x = self.vel_base * random.choice([-1, 1])
        self.vel_y = self.vel_base # Começa caindo (Y positivo)

    def mover(self):
        # Atualiza a posição decimal
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        
        # Repassa para o rect (que lida com os inteiros da tela)
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

        # Lógica de colisão com as paredes esquerda e direita
        if self.rect.left <= 0:
            self.rect.left = 0
            self.pos_x = float(self.rect.x) # Sincroniza a posição decimal
            self.vel_x = abs(self.vel_x) # Inverte para positivo (vai para direita)
        elif self.rect.right >= LARGURA_TELA:
            self.rect.right = LARGURA_TELA
            self.pos_x = float(self.rect.x)
            self.vel_x = -abs(self.vel_x) # Inverte para negativo (vai para esquerda)
            
        # Lógica de colisão com o teto
        if self.rect.top <= 0:
            self.rect.top = 0
            self.pos_y = float(self.rect.y)
            self.vel_y = abs(self.vel_y) # Inverte para descer

    def desenhar(self, superficie):
        pygame.draw.circle(superficie, CORES["bola"], self.rect.center, self.raio)

class Bloco:
    def __init__(self, x, y, hp):
        self.rect = pygame.Rect(x, y, 65, 25)
        self.hp = hp # Pontos de vida do bloco

    def desenhar(self, superficie):
        # Define a cor do bloco com base na sua vida atual
        if self.hp >= 3:
            cor = CORES["hp3"]
        elif self.hp == 2:
            cor = CORES["hp2"]
        else:
            cor = CORES["hp1"]
            
        pygame.draw.rect(superficie, cor, self.rect, border_radius=3)


# FUNÇÕES AUXILIARES DO JOGO
def criar_blocos(nivel):
    blocos = []
    linhas = min(3 + (nivel // 2), 8) # Aumenta a quantidade de linhas conforme o nível
    
    for linha in range(linhas):
        for coluna in range(10): # 10 blocos por linha
            hp = 1
            # Probabilidade de surgir blocos com HP 2 ou 3 baseada no nível atual
            if nivel > 2 and random.random() < (0.1 * nivel): hp = 2
            if nivel > 5 and random.random() < (0.05 * nivel): hp = 3
            
            # Adiciona o bloco na lista calculando sua posição X e Y na tela
            blocos.append(Bloco(50 + coluna * 70, 60 + linha * 35, hp))
    return blocos

def gerar_bola_segura(vel_global, dano):
    x_aleatorio = random.randint(100, LARGURA_TELA - 100)
    y_seguro = 350 
    return Bola(x_aleatorio, y_seguro, vel_global, dano)

# Lista com todos os upgrades disponíveis no jogo
UPGRADES = [
    {"id": "largura", "nome": "Extensão Cyber", "desc": "Sua barra fica mais larga."},
    {"id": "multiball", "nome": "Fragmentação", "desc": "Adiciona +1 Bola simultânea."},
    {"id": "dano", "nome": "Força Bruta", "desc": "Bolas causam +1 de dano."},
    {"id": "vida", "nome": "Backup do Sistema", "desc": "Ganha +1 Vida máxima."},
    {"id": "multiplicador", "nome": "Overclock", "desc": "Multiplicador Base de Pontos +1."}
]


# LOOP PRINCIPAL DO JOGO
def main():
    relogio = pygame.time.Clock() # Controlador de FPS
    estado_atual = 1 # 1: Jogando, 2: Tela de Upgrade, 3: Tela de Game Over

    # --- PROGRESSÃO PERMANENTE (SISTEMA ROGUELITE) ---
    # Estes status não são zerados no Game Over.
    status_permanentes = {
        "largura_barra": 120,
        "qtd_bolas": 1,
        "dano_bolas": 1,
        "vidas_max": 3,
        "multiplicador": 1
    }

    # Atributos da partida (resetam ao morrer)
    pontuacao = 0
    nivel = 1
    vel_bola_global = 5.0
    
    # Instancia os objetos usando os status armazenados
    vidas = status_permanentes["vidas_max"]
    barra = Barra(status_permanentes["largura_barra"])
    bolas = [gerar_bola_segura(vel_bola_global, status_permanentes["dano_bolas"]) for _ in range(status_permanentes["qtd_bolas"])]
    blocos = criar_blocos(nivel)
    opcoes_atuais = []

    # Loop infinito que mantém o jogo rodando
    while True:
        tela.fill(CORES["fundo"]) # Limpa a tela a cada frame

        # --- TRATAMENTO DE EVENTOS ---
        for evento in pygame.event.get():
            # Evento de fechar a janela
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Captura de teclas pressionadas soltas (menus)
            if evento.type == pygame.KEYDOWN:
                
                # SE ESTIVER NA TELA DE UPGRADE
                if estado_atual == 2: 
                    escolha = None
                    if evento.key == pygame.K_1: escolha = 0
                    elif evento.key == pygame.K_2: escolha = 1
                    elif evento.key == pygame.K_3: escolha = 2
                    
                    if escolha is not None:
                        upg = opcoes_atuais[escolha]["id"]
                        
                        # Aplica os upgrades no dicionário permanente
                        if upg == "largura": 
                            status_permanentes["largura_barra"] += 30
                        elif upg == "multiball": 
                            status_permanentes["qtd_bolas"] += 1
                        elif upg == "dano": 
                            status_permanentes["dano_bolas"] += 1
                        elif upg == "vida": 
                            status_permanentes["vidas_max"] += 1
                            vidas += 1
                        elif upg == "multiplicador": 
                            status_permanentes["multiplicador"] += 1
                        
                        # Prepara a próxima fase
                        nivel += 1
                        vel_bola_global = min(10.0, vel_bola_global + 0.3) # Aumenta a dificuldade
                        blocos = criar_blocos(nivel)
                        
                        # Atualiza as entidades para a nova fase
                        barra.largura = status_permanentes["largura_barra"]
                        barra.resetar_posicao()
                        bolas = [gerar_bola_segura(vel_bola_global, status_permanentes["dano_bolas"]) for _ in range(status_permanentes["qtd_bolas"])]
                        
                        estado_atual = 1 # Volta para o jogo

                # SE ESTIVER NA TELA DE GAME OVER E APERTAR [R]
                elif estado_atual == 3 and evento.key == pygame.K_r:
                    # Reseta apenas o progresso da fase
                    pontuacao = 0
                    nivel = 1
                    vel_bola_global = 5.0
                    
                    # Reconstrói os objetos puxando a força permanente guardada
                    vidas = status_permanentes["vidas_max"]
                    barra = Barra(status_permanentes["largura_barra"])
                    bolas = [gerar_bola_segura(vel_bola_global, status_permanentes["dano_bolas"]) for _ in range(status_permanentes["qtd_bolas"])]
                    blocos = criar_blocos(nivel)
                    
                    estado_atual = 1 # Reinicia o jogo

        # ESTADO 1: JOGANDO
        if estado_atual == 1:
            # Pega as teclas pressionadas simultaneamente para movimentação suave
            teclas = pygame.key.get_pressed()
            barra.mover(teclas)

            # Lógica para cada bola em campo (permite multiballs)
            for bola in bolas[:]:
                bola.mover()

                # Colisão Bola x Barra
                if bola.rect.colliderect(barra.rect) and bola.vel_y > 0:
                    bola.vel_y = -bola.vel_y # Rebate para cima
                    
                    # Física simples: Muda o ângulo da bola no eixo X dependendo de onde bateu na barra
                    # Bater nas pontas joga a bola mais rápido para os lados.
                    distancia_centro = bola.rect.centerx - barra.rect.centerx
                    bola.vel_x = distancia_centro * 0.15

                # Colisão Bola x Blocos
                for bloco in blocos[:]:
                    if bola.rect.colliderect(bloco.rect):
                        bloco.hp -= bola.dano # Tira o HP do bloco baseado no dano da bola
                        bola.vel_y = -bola.vel_y # Rebate
                        
                        # Se o bloco zerou a vida, é destruído
                        if bloco.hp <= 0:
                            blocos.remove(bloco)
                            pontuacao += (10 * status_permanentes["multiplicador"])
                        break # O break evita que a bola quebre vários blocos no mesmo milissegundo atravessando eles

                # Verifica se a bola caiu da tela (passou do chão)
                if bola.rect.top > ALTURA_TELA:
                    bolas.remove(bola)

            # Se todas as bolas caírem, perde uma vida
            if len(bolas) == 0:
                vidas -= 1
                if vidas <= 0:
                    estado_atual = 3 # Fim de jogo
                else:
                    barra.resetar_posicao()
                    # Renasce todas as bolas que o jogador possui
                    bolas = [gerar_bola_segura(vel_bola_global, status_permanentes["dano_bolas"]) for _ in range(status_permanentes["qtd_bolas"])]

            # Condição de Vitória da Fase (Se limpar todos os blocos)
            if len(blocos) == 0:
                estado_atual = 2
                # Sorteia 3 opções de upgrade aleatórias para o jogador escolher. Corrigido!
                opcoes_atuais = random.sample(UPGRADES, 3)

            # Renderização dos objetos do jogo na tela
            barra.desenhar(tela)
            for bola in bolas: bola.desenhar(tela)
            for bloco in blocos: bloco.desenhar(tela)

            # Renderização da Interface (HUD)
            tela.blit(fonte_placar.render(f"SCORE: {pontuacao}", True, CORES["texto"]), (20, 10))
            tela.blit(fonte_placar.render(f"VIDAS: {vidas}", True, CORES["hp3"]), (20, 40))
            tela.blit(fonte_placar.render(f"NÍVEL: {nivel}", True, CORES["barra"]), (LARGURA_TELA - 150, 10))

        # ESTADO 2: TELA DE UPGRADE
        elif estado_atual == 2:
            txt_titulo = fonte_titulo.render("UPGRADE", True, CORES["hp3"])
            tela.blit(txt_titulo, txt_titulo.get_rect(center=(LARGURA_TELA//2, 80)))
            
            txt_sub = fonte_instrucoes.render("Escolha o próximo Upgrade (1, 2 ou 3):", True, CORES["branco"])
            tela.blit(txt_sub, txt_sub.get_rect(center=(LARGURA_TELA//2, 140)))

            # Desenha os 3 "Cards" de upgrade na tela
            for i, opcao in enumerate(opcoes_atuais):
                rect_carta = pygame.Rect(LARGURA_TELA//2 - 250, 220 + (i * 110), 500, 90)
                pygame.draw.rect(tela, (30, 30, 45), rect_carta, border_radius=10)
                pygame.draw.rect(tela, CORES["barra"], rect_carta, 2, border_radius=10)
                
                # Textos de cada card
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

        # Atualiza a tela física e regula a velocidade do jogo
        pygame.display.flip()
        relogio.tick(FPS)

if __name__ == "__main__":
    main()
