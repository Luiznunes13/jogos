import pygame
import random
import math
import json
import os

# Inicialização do Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaga Clone")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)

# Configurações do jogo
FPS = 60
clock = pygame.time.Clock()

# Estados do jogo
MENU = 0
PLAYING = 1
GAME_OVER = 2
HIGH_SCORES = 3
ENTER_NAME = 4

# Dificuldades
DIFFICULTIES = {
    "Fácil": {"enemy_speed": 1, "bullet_frequency": 0.005, "enemy_health": 1},
    "Médio": {"enemy_speed": 2, "bullet_frequency": 0.01, "enemy_health": 1},
    "Difícil": {"enemy_speed": 3, "bullet_frequency": 0.015, "enemy_health": 2}
}

# Arquivo de scores
SCORES_FILE = "high_scores.json"

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(GREEN)
        # Desenhando a nave do jogador
        pygame.draw.polygon(self.image, GREEN, [(20, 0), (0, 30), (40, 30)])
        pygame.draw.polygon(self.image, CYAN, [(20, 5), (5, 25), (35, 25)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 5
        self.shoot_cooldown = 0
        
    def update(self):
        # Movimento
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
            
        # Recarregando tiro
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
    def shoot(self):
        if self.shoot_cooldown == 0:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            self.shoot_cooldown = 10

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type=0, difficulty="Médio"):
        super().__init__()
        self.enemy_type = enemy_type
        self.difficulty = difficulty
        self.image = pygame.Surface((30, 30))
        
        # Desenhando diferentes tipos de inimigos
        if enemy_type == 0:  # Inimigo básico
            pygame.draw.circle(self.image, RED, (15, 15), 12)
            pygame.draw.circle(self.image, YELLOW, (15, 15), 8)
            self.points = 10
        elif enemy_type == 1:  # Inimigo médio
            pygame.draw.polygon(self.image, PURPLE, [(15, 0), (0, 30), (30, 30)])
            pygame.draw.polygon(self.image, BLUE, [(15, 5), (5, 25), (25, 25)])
            self.points = 20
        else:  # Inimigo chefe
            pygame.draw.rect(self.image, RED, (0, 0, 30, 30))
            pygame.draw.rect(self.image, YELLOW, (5, 5, 20, 20))
            pygame.draw.circle(self.image, RED, (15, 15), 5)
            self.points = 50
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = DIFFICULTIES[difficulty]["enemy_speed"]
        self.speed_y = 0
        self.shoot_cooldown = random.randint(60, 180)
        self.move_pattern = random.choice(['straight', 'zigzag', 'dive'])
        self.original_x = x
        self.time = 0
        self.health = DIFFICULTIES[difficulty]["enemy_health"]
        
    def update(self):
        self.time += 1
        
        # Padrões de movimento
        if self.move_pattern == 'straight':
            self.rect.x += self.speed_x
        elif self.move_pattern == 'zigzag':
            self.rect.x += self.speed_x
            self.rect.y += math.sin(self.time * 0.1) * 2
        elif self.move_pattern == 'dive' and self.time > 100:
            self.rect.y += 3
            if self.rect.y > SCREEN_HEIGHT:
                self.kill()
                
        # Mudar direção nas bordas
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.speed_x *= -1
            self.rect.y += 20
            
        # Atirar
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0 and random.random() < DIFFICULTIES[self.difficulty]["bullet_frequency"]:
            self.shoot()
            self.shoot_cooldown = random.randint(60, 180)
            
    def shoot(self):
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 5
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 30
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.lifetime = 20
        
    def update(self):
        self.lifetime -= 1
        self.size += 2
        self.image = pygame.Surface((self.size, self.size))
        alpha = int(255 * (self.lifetime / 20))
        color = (255, 255 - (20 - self.lifetime) * 10, 0)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.lifetime <= 0:
            self.kill()

# Grupos de sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Funções para gerenciar scores
def load_high_scores():
    try:
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_high_scores(scores):
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=2)

def add_high_score(name, score):
    scores = load_high_scores()
    scores.append({"name": name, "score": score})
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:10]  # Manter apenas top 10
    save_high_scores(scores)
    return scores

def is_high_score(score):
    scores = load_high_scores()
    return len(scores) < 10 or score > min(s["score"] for s in scores) if scores else True

# Funções de desenho dos menus
def draw_menu(screen, font, small_font, selected_difficulty):
    screen.fill(BLACK)
    
    # Título
    title = font.render("GALAGA CLONE", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
    
    # Opções de dificuldade
    y_start = 250
    for i, difficulty in enumerate(DIFFICULTIES.keys()):
        color = GREEN if difficulty == selected_difficulty else WHITE
        text = small_font.render(f"{i+1}. {difficulty}", True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_start + i * 40))
    
    # Instruções
    instructions = [
        "Use 1, 2, 3 para selecionar dificuldade",
        "Pressione ENTER para jogar",
        "Pressione H para ver High Scores",
        "",
        "Controles:",
        "Setas: Mover nave",
        "Espaço: Atirar"
    ]
    
    y = 400
    for instruction in instructions:
        text = small_font.render(instruction, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
        y += 25

def draw_high_scores(screen, font, small_font):
    screen.fill(BLACK)
    
    title = font.render("TOP 10 SCORES", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    
    scores = load_high_scores()
    
    if not scores:
        no_scores = small_font.render("Nenhum score ainda!", True, WHITE)
        screen.blit(no_scores, (SCREEN_WIDTH // 2 - no_scores.get_width() // 2, 200))
    else:
        y_start = 150
        for i, score_data in enumerate(scores):
            position = f"{i+1:2d}."
            name = score_data["name"]
            score = score_data["score"]
            text = small_font.render(f"{position} {name:<15} {score:>8}", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_start + i * 30))
    
    back_text = small_font.render("Pressione ESC para voltar", True, GREEN)
    screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 500))

def draw_enter_name(screen, font, small_font, player_name, score):
    screen.fill(BLACK)
    
    title = font.render("NOVO HIGH SCORE!", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
    
    score_text = font.render(f"Sua pontuação: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 200))
    
    name_prompt = small_font.render("Digite seu nome:", True, WHITE)
    screen.blit(name_prompt, (SCREEN_WIDTH // 2 - name_prompt.get_width() // 2, 280))
    
    # Caixa de texto
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 150, 320, 300, 40), 2)
    name_text = font.render(player_name, True, WHITE)
    screen.blit(name_text, (SCREEN_WIDTH // 2 - 145, 325))
    
    instruction = small_font.render("Pressione ENTER para confirmar", True, GREEN)
    screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 400))

# Criando jogador
player = Player()
all_sprites.add(player)

# Variáveis do jogo
score = 0
lives = 3
level = 1
game_state = MENU
selected_difficulty = "Médio"
player_name = ""
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

def create_enemy_wave(level, difficulty):
    enemies.empty()
    rows = 3 + level // 2
    cols = 8
    for row in range(rows):
        for col in range(cols):
            x = 100 + col * 70
            y = 50 + row * 50
            enemy_type = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
            if level > 3 and random.random() < 0.1:
                enemy_type = 2  # Mais chefes em níveis altos
            enemy = Enemy(x, y, enemy_type, difficulty)
            all_sprites.add(enemy)
            enemies.add(enemy)

def reset_game():
    global score, lives, level, game_state
    score = 0
    lives = 3
    level = 1
    game_state = PLAYING
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    enemy_bullets.empty()
    explosions.empty()
    player = Player()
    all_sprites.add(player)
    create_enemy_wave(level, selected_difficulty)
    return player

# Loop principal do jogo
running = True
while running:
    # Manter a taxa de quadros
    clock.tick(FPS)
    
    # Processando eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == MENU:
                if event.key == pygame.K_1:
                    selected_difficulty = "Fácil"
                elif event.key == pygame.K_2:
                    selected_difficulty = "Médio"
                elif event.key == pygame.K_3:
                    selected_difficulty = "Difícil"
                elif event.key == pygame.K_RETURN:
                    player = reset_game()
                elif event.key == pygame.K_h:
                    game_state = HIGH_SCORES
            
            elif game_state == HIGH_SCORES:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
            
            elif game_state == PLAYING:
                if event.key == pygame.K_SPACE:
                    player.shoot()
            
            elif game_state == GAME_OVER:
                if event.key == pygame.K_r:
                    game_state = MENU
            
            elif game_state == ENTER_NAME:
                if event.key == pygame.K_RETURN:
                    if player_name.strip():
                        add_high_score(player_name.strip(), score)
                        player_name = ""
                        game_state = HIGH_SCORES
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 15 and event.unicode.isprintable():
                        player_name += event.unicode
    
    # Lógica do jogo baseada no estado
    if game_state == PLAYING:
        # Atualizando
        all_sprites.update()
        
        # Verificando colisões - tiros do jogador com inimigos
        hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
        for bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                enemy.health -= 1
                if enemy.health <= 0:
                    score += enemy.points
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(explosion)
                    explosions.add(explosion)
                    enemy.kill()
        
        # Verificando colisões - tiros dos inimigos com o jogador
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if hits:
            lives -= 1
            explosion = Explosion(player.rect.centerx, player.rect.centery)
            all_sprites.add(explosion)
            explosions.add(explosion)
            if lives <= 0:
                if is_high_score(score):
                    game_state = ENTER_NAME
                else:
                    game_state = GAME_OVER
        
        # Verificando colisões - inimigos com o jogador
        hits = pygame.sprite.spritecollide(player, enemies, True)
        if hits:
            lives -= 1
            explosion = Explosion(player.rect.centerx, player.rect.centery)
            all_sprites.add(explosion)
            explosions.add(explosion)
            if lives <= 0:
                if is_high_score(score):
                    game_state = ENTER_NAME
                else:
                    game_state = GAME_OVER
        
        # Verificando se todos os inimigos foram derrotados
        if len(enemies) == 0:
            level += 1
            create_enemy_wave(level, selected_difficulty)
    
    # Desenhando baseado no estado
    if game_state == MENU:
        draw_menu(screen, font, small_font, selected_difficulty)
    
    elif game_state == HIGH_SCORES:
        draw_high_scores(screen, font, small_font)
    
    elif game_state == ENTER_NAME:
        draw_enter_name(screen, font, small_font, player_name, score)
    
    elif game_state == PLAYING:
        screen.fill(BLACK)
        
        # Desenhando estrelas de fundo
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        # Desenhando sprites
        all_sprites.draw(screen)
        
        # Desenhando UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (10, 50))
        
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 150, 10))
        
        diff_text = small_font.render(f"Dificuldade: {selected_difficulty}", True, WHITE)
        screen.blit(diff_text, (SCREEN_WIDTH - 200, 50))
    
    elif game_state == GAME_OVER:
        screen.fill(BLACK)
        
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = small_font.render("Pressione R para voltar ao menu", True, WHITE)
        final_score_text = font.render(f"Pontuação Final: {score}", True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))
    
    # Atualizando a tela
    pygame.display.flip()

# Encerrando o Pygame
pygame.quit()