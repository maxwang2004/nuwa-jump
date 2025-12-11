import pygame
import random
import sys

# --- Constants ---
WIDTH, HEIGHT = 480, 640
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -12

# PHYSICS CONSTANTS
# Absolute max height is 144px (v^2 / 2g). We cap generation at 135 for safety.
MAX_JUMP_HEIGHT = 135 
MIN_PLATFORM_GAP = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
GREY_OUTLINE = (100, 100, 100)
AO_LEG_COLOR = (107, 142, 35)

# ORDER: 0:Blue, 1:White, 2:Yellow, 3:Red, 4:Green
STONE_COLORS = [
    (30, 144, 255),  
    (255, 255, 255), 
    (255, 215, 0),   
    (220, 20, 60),   
    (50, 205, 50)    
]

# --- Asset Loader ---
assets = {}

def load_assets():
    try:
        assets['nuwa'] = pygame.transform.scale(pygame.image.load('nuwa.png'), (40, 50))
        assets['platform'] = pygame.transform.scale(pygame.image.load('platform.png'), (80, 20))
        assets['bg'] = pygame.transform.scale(pygame.image.load('bg.png'), (WIDTH, HEIGHT))
        assets['meteor'] = pygame.transform.scale(pygame.image.load('meteor.png'), (30, 60))
        assets['ao_leg'] = pygame.transform.scale(pygame.image.load('ao_leg.png'), (30, 40))
        for i in range(5):
            assets[f'stone_{i}'] = pygame.transform.scale(pygame.image.load(f'stone_{i}.png'), (24, 24))
    except Exception as e:
        print(f"Could not load custom sprites: {e}. Using shapes.")

# --- Helper: Text Wrap ---
def draw_text_multiline(surface, text, pos, font, color, max_width):
    words = [word.split(' ') for word in text.splitlines()]
    space = font.size(' ')[0]
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]
                y += word_height
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]
        y += word_height

# --- Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if 'nuwa' in assets:
            self.image = assets['nuwa'].convert_alpha()
            self.original_image = self.image
        else:
            self.image = pygame.Surface((30, 40))
            self.image.fill((255, 105, 180))
            self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 100)
        self.vel_y = 0

    def update(self):
        self.vel_y += GRAVITY
        dx = 0
        dy = self.vel_y

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx = -5
            self.image = pygame.transform.flip(self.original_image, True, False)
        if key[pygame.K_RIGHT]:
            dx = 5
            self.image = self.original_image

        if self.rect.left + dx > WIDTH: self.rect.right = 0
        if self.rect.right + dx < 0: self.rect.left = WIDTH

        self.rect.x += dx
        self.rect.y += dy

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w):
        super().__init__()
        if 'platform' in assets:
            self.image = pygame.transform.scale(assets['platform'], (w, 20)).convert_alpha()
        else:
            self.image = pygame.Surface((w, 10))
            self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Stone(pygame.sprite.Sprite):
    def __init__(self, x, y, color_index):
        super().__init__()
        self.color_index = color_index
        key = f'stone_{color_index}'
        if key in assets:
            self.image = assets[key].convert_alpha()
        else:
            self.image = pygame.Surface((15, 15))
            self.image.fill(STONE_COLORS[color_index])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y - 25)

class AoLeg(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        if 'ao_leg' in assets:
            self.image = assets['ao_leg'].convert_alpha()
        else:
            self.image = pygame.Surface((20, 40))
            self.image.fill(AO_LEG_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y - 30)

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if 'meteor' in assets:
            self.image = assets['meteor'].convert_alpha()
        else:
            self.image = pygame.Surface((30,30))
            self.image.fill((255, 50, 0))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - 30)
        self.rect.y = random.randint(-600, -50) 
        self.speed = random.randint(3, 7)

    def update(self, scroll):
        self.rect.y += self.speed + scroll
        if self.rect.y > HEIGHT:
            self.kill()

# --- Main Functions ---

def draw_tilted_background(screen, scroll_y):
    if 'bg' in assets:
        bg_img = assets['bg']
        rel_y = (scroll_y * 0.5) % HEIGHT 
        rel_x = (scroll_y * 0.2) % WIDTH 
        screen.blit(bg_img, (rel_x - WIDTH, rel_y - HEIGHT))
        screen.blit(bg_img, (rel_x, rel_y - HEIGHT))
        screen.blit(bg_img, (rel_x - WIDTH, rel_y))
        screen.blit(bg_img, (rel_x, rel_y))
    else:
        screen.fill((20, 20, 60))

def show_home_screen(screen, font, lore_font):
    screen.fill(BLACK)
    if 'bg' in assets: screen.blit(assets['bg'], (0,0))
    s = pygame.Surface((WIDTH - 40, HEIGHT - 80))
    s.set_alpha(220)
    s.fill(BLACK)
    screen.blit(s, (20, 40))

    title = font.render("Nuwa: Patching the Sky", True, GOLD)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

    lore_text = (
        "The conflict between Gonggong and Zhurong has shattered the heavens.\n\n"
        "You are Nuwa, creator deity and mother of humanity.\n\n"
        "Ascend to gather:\n"
        "1. The Five Colored Stones\n"
        "2. The Leg of the Great Turtle Ao\n\n"
        "Only then can you restore the cosmic pillars.\n\n"
        "Press SPACE to Ascend."
    )
    
    draw_text_multiline(screen, lore_text, (40, 120), lore_font, WHITE, WIDTH - 60)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Nuwa Jump")
    clock = pygame.time.Clock()
    
    load_assets()
    
    font = pygame.font.SysFont('Arial', 30, bold=True)
    lore_font = pygame.font.SysFont('Arial', 18)
    # Smaller font for the Leg label to fit inside the box
    small_font = pygame.font.SysFont('Arial', 14, bold=True)
    
    show_home_screen(screen, font, lore_font)

    player = Player()
    platform_group = pygame.sprite.Group()
    stone_group = pygame.sprite.Group()
    leg_group = pygame.sprite.Group() 
    meteor_group = pygame.sprite.Group()

    start_plat = Platform(WIDTH // 2 - 40, HEIGHT - 100, 80)
    platform_group.add(start_plat)
    player.rect.bottom = start_plat.rect.top
    player.rect.centerx = start_plat.rect.centerx

    # Initial Platforms
    for i in range(1, 8):
        p_w = random.randint(70, 100)
        p_x = random.randint(0, WIDTH - p_w)
        p_y = HEIGHT - 100 - (i * 90)
        p = Platform(p_x, p_y, p_w)
        platform_group.add(p)

    total_scroll = 0
    collected_stones = set()
    has_ao_leg = False
    game_over = False
    won = False
    
    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and (game_over or won):
                    game_loop()
                    return

        if not game_over and not won:
            player.update()

            scroll = 0
            if player.rect.y < HEIGHT // 2:
                scroll = (HEIGHT // 2) - player.rect.y
                player.rect.y += scroll 
                total_scroll += scroll

            if len(platform_group) < 15:
                highest_plat = min(platform_group, key=lambda x: x.rect.y)
                prev_x = highest_plat.rect.centerx # Use center for easier calc
                
                p_w = random.randint(60, 90)
                
                # --- PHYSICS CONSTRAINT LOGIC ---
                # We randomly pick a vertical gap first
                gap_y = random.randint(MIN_PLATFORM_GAP, 110) # 110 is conservative max
                
                # Calculate Max Horizontal Distance allowed for this specific Vertical Gap
                # Linear approximation of Jump Arc:
                # If Gap_Y is 0 (same height), we can jump far (~200px)
                # If Gap_Y is MAX (135), we can jump 0px horizontally.
                # Formula: Max_X = (Max_Height - Gap_Y) * Scale_Factor
                
                # We calculate 'allowable' X deviation
                max_dx_allowed = (MAX_JUMP_HEIGHT - gap_y) * 1.5 
                # e.g. Gap 50 -> (135-50)*1.5 = 127px reach.
                # e.g. Gap 100 -> (135-100)*1.5 = 52px reach.
                
                # Clamp max_dx to screen bounds logic
                dist_x = random.randint(0, int(max_dx_allowed))
                direction = random.choice([-1, 1])
                
                p_x_center = prev_x + (dist_x * direction)
                
                # Keep strictly inside screen
                if p_x_center < (p_w // 2): p_x_center = p_w // 2
                if p_x_center > WIDTH - (p_w // 2): p_x_center = WIDTH - (p_w // 2)
                
                # Convert back to top-left coord for class
                p_x = p_x_center - (p_w // 2)
                p_y = highest_plat.rect.y - gap_y
                
                p = Platform(p_x, p_y, p_w)
                platform_group.add(p)

                # --- SPAWN LOGIC ---
                rng = random.randint(1, 100)
                
                if not has_ao_leg and len(leg_group) == 0 and rng > 98:
                    leg = AoLeg(p.rect.centerx, p.rect.y)
                    leg_group.add(leg)
                
                elif rng > 90: 
                    visible_stones = {s.color_index for s in stone_group}
                    candidates = [i for i in range(5) if i not in collected_stones and i not in visible_stones]
                    if candidates:
                        s = Stone(p.rect.centerx, p.rect.y, random.choice(candidates))
                        stone_group.add(s)

            if random.randint(0, 100) < 1 + (total_scroll // 1500): 
                m = Meteor()
                if abs(m.rect.x - player.rect.x) > 60:
                    meteor_group.add(m)

            for sprite in platform_group:
                sprite.rect.y += scroll
                if sprite.rect.top >= HEIGHT: sprite.kill()
            for sprite in stone_group:
                sprite.rect.y += scroll
                if sprite.rect.top >= HEIGHT: sprite.kill()
            for sprite in leg_group:
                sprite.rect.y += scroll
                if sprite.rect.top >= HEIGHT: sprite.kill()
            meteor_group.update(scroll)

            if player.vel_y > 0:
                hits = pygame.sprite.spritecollide(player, platform_group, False)
                if hits:
                    lowest_hit = hits[0]
                    if player.rect.bottom < lowest_hit.rect.bottom: 
                        player.rect.bottom = lowest_hit.rect.top
                        player.vel_y = JUMP_STRENGTH
            
            stone_hits = pygame.sprite.spritecollide(player, stone_group, True)
            for s in stone_hits:
                collected_stones.add(s.color_index)
            
            leg_hits = pygame.sprite.spritecollide(player, leg_group, True)
            if leg_hits:
                has_ao_leg = True

            if pygame.sprite.spritecollide(player, meteor_group, False):
                game_over = True 

            if player.rect.top > HEIGHT:
                game_over = True
            
            if len(collected_stones) == 5 and has_ao_leg and total_scroll > 3000:
                won = True

        # --- Drawing ---
        draw_tilted_background(screen, total_scroll)
        platform_group.draw(screen)
        stone_group.draw(screen)
        leg_group.draw(screen)
        meteor_group.draw(screen)
        screen.blit(player.image, player.rect)

        # UI
        if won:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(WHITE)
            screen.blit(overlay, (0,0))
            text = font.render("SKY PATCHED", True, BLACK)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 20))
        elif game_over:
            text = font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
            sub = lore_font.render("Space to Retry", True, WHITE)
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 40))
        else:
            # HUD
            hud_y = 10
            hud_x_start = 10
            slot_size = 24 # Slightly bigger for visibility
            padding = 6
            
            # Draw Stones
            for i in range(5):
                x_pos = hud_x_start + (i * (slot_size + padding))
                rect = (x_pos, hud_y, slot_size, slot_size)
                if i in collected_stones:
                    pygame.draw.rect(screen, STONE_COLORS[i], rect)
                    pygame.draw.rect(screen, WHITE, rect, 2)
                else:
                    pygame.draw.rect(screen, GREY_OUTLINE, rect, 2)

            # Draw Leg Slot (Fixed Alignment)
            leg_x = hud_x_start + (5 * (slot_size + padding)) + 15
            leg_width = 40
            leg_rect = (leg_x, hud_y, leg_width, slot_size)
            
            if has_ao_leg:
                pygame.draw.rect(screen, AO_LEG_COLOR, leg_rect)
                pygame.draw.rect(screen, WHITE, leg_rect, 2)
                label = small_font.render("LEG", True, WHITE)
                # Center Text in Rect
                text_rect = label.get_rect(center=(leg_x + leg_width//2, hud_y + slot_size//2))
                screen.blit(label, text_rect)
            else:
                pygame.draw.rect(screen, GREY_OUTLINE, leg_rect, 2)
                label = small_font.render("?", True, GREY_OUTLINE)
                text_rect = label.get_rect(center=(leg_x + leg_width//2, hud_y + slot_size//2))
                screen.blit(label, text_rect)

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()