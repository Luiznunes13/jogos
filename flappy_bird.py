import pygame
import random
import sys

# Inicialização
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Variáveis do jogo
clock = pygame.time.Clock()
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -8
PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_SPEED = 3
GROUND_HEIGHT = 50

# Fonte
font = pygame.font.SysFont(None, 36)

# Carregar imagem de fundo
try:
    background_img = pygame.image.load("background.png")
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    has_background = True
except:
    # Se não encontrar a imagem, usar fundo padrão
    has_background = False
    print("Imagem de fundo não encontrada. Usando fundo padrão.")

class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.radius = 15
        self.velocity = 0
        self.color = YELLOW
        
    def jump(self):
        self.velocity = JUMP_STRENGTH
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, BLACK, (self.x + 5, self.y - 5), 4)  # Olho
        pygame.draw.polygon(surface, RED, [(self.x - 10, self.y), (self.x, self.y + 5), (self.x - 10, self.y + 10)])  # Bico
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - GROUND_HEIGHT - 100)
        self.passed = False
        
    def update(self):
        self.x -= PIPE_SPEED
        
    def draw(self, surface):
        # Cano superior
        pygame.draw.rect(surface, GREEN, (self.x, 0, PIPE_WIDTH, self.height))
        pygame.draw.rect(surface, BLUE, (self.x - 5, self.height - 30, PIPE_WIDTH + 10, 30))
        
        # Cano inferior
        bottom_y = self.height + PIPE_GAP
        pygame.draw.rect(surface, GREEN, (self.x, bottom_y, PIPE_WIDTH, SCREEN_HEIGHT - bottom_y - GROUND_HEIGHT))
        pygame.draw.rect(surface, BLUE, (self.x - 5, bottom_y, PIPE_WIDTH + 10, 30))
        
    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        bottom_rect = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT - self.height - PIPE_GAP - GROUND_HEIGHT)
        return top_rect, bottom_rect

def draw_background(surface):
    """Desenha o fundo do jogo"""
    if has_background:
        surface.blit(background_img, (0, 0))
    else:
        # Fundo padrão com gradiente de céu
        surface.fill((135, 206, 235))  # Azul céu
        # Adicionar algumas nuvens simples
        for i in range(0, SCREEN_HEIGHT, 40):
            color_intensity = 200 + (i // 40) % 56
            pygame.draw.line(surface, (color_intensity, color_intensity, 255), (0, i), (SCREEN_WIDTH, i), 2)

def draw_ground(surface):
    pygame.draw.rect(surface, (139, 69, 19), (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
    pygame.draw.rect(surface, GREEN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, 10))

def show_game_over(surface, score):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))
    
    game_over_text = font.render("GAME OVER", True, RED)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press SPACE to restart", True, WHITE)
    
    surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

def main():
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH)]
    score = 0
    game_over = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_over:
                        bird.jump()
                    else:
                        # Reiniciar jogo
                        bird = Bird()
                        pipes = [Pipe(SCREEN_WIDTH)]
                        score = 0
                        game_over = False
        
        if not game_over:
            # Atualizar elementos
            bird.update()
            
            # Gerar novos canos
            if pipes[-1].x < SCREEN_WIDTH - 200:
                pipes.append(Pipe(SCREEN_WIDTH))
            
            # Atualizar canos
            for pipe in pipes[:]:
                pipe.update()
                
                # Remover canos fora da tela
                if pipe.x + PIPE_WIDTH < 0:
                    pipes.remove(pipe)
                
                # Verificar pontuação
                if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                    pipe.passed = True
                    score += 1
                
                # Verificar colisão
                bird_rect = bird.get_rect()
                top_rect, bottom_rect = pipe.get_rects()
                
                if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                    game_over = True
                
                # Verificar colisão com chão/teto
                if bird.y - bird.radius <= 0 or bird.y + bird.radius >= SCREEN_HEIGHT - GROUND_HEIGHT:
                    game_over = True
        
        # Desenhar elementos
        screen.fill(BLACK)
        
        # Desenhar fundo
        draw_background(screen)
        
        # Desenhar elementos do jogo
        for pipe in pipes:
            pipe.draw(screen)
        
        bird.draw(screen)
        draw_ground(screen)
        
        # Mostrar pontuação
        score_text = font.render(str(score), True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Mostrar game over se necessário
        if game_over:
            show_game_over(screen, score)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()