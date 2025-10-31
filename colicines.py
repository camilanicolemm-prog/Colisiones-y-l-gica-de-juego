import pygame, sys, random, math

pygame.init()
WIDTH, HEIGHT = 960, 540
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini agar.io - Extendido")
CLOCK = pygame.time.Clock()
FPS = 60

WORLD_W, WORLD_H = 3000, 3000

def clamp(v, a, b): 
    return max(a, min(v, b))

def draw_grid(surf, camx, camy):
    surf.fill((18,20,26))
    color = (28,32,40)
    step = 64
    sx = -((camx) % step)
    sy = -((camy) % step)
    for x in range(int(sx), WIDTH, step):
        pygame.draw.line(surf, color, (x, 0), (x, HEIGHT))
    for y in range(int(sy), HEIGHT, step):
        pygame.draw.line(surf, color, (0, y), (WIDTH, y))

class food:
    __slots__ = ('x', 'y', 'r', 'col', 'vx', 'vy')

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.r = random.randint(3, 6)
        self.col = random.choice([
            (255, 173, 72), (170, 240, 170), (150, 200, 255),
            (255, 120, 160), (255, 220, 120)
        ])
        self.vx = 0.0
        self.vy = 0.0

    def draw(self, surf, camx, camy):
        pygame.draw.circle(surf, self.col, (int(self.x - camx), int(self.y - camy)), self.r)

class blob:
    def __init__(self, x, y, mass, color):
        self.x, self.y = x, y
        self.mass = mass
        self.color = color
        self.vx = 0.0
        self.vy = 0.0
        self.target = None
        self.alive = True
        self.split_timer = 0  # para fusionar luego

    @property
    def r(self):
        return max(6, int(math.sqrt(self.mass)))

    @property
    def speed(self):
        base = 260.0
        return max(60.0, base / (1.0 + 0.04 * self.r))

    def move_towards(self, tx, ty, dt):
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 1e-3:
            vx = (dx / dist) * self.speed
            vy = (dy / dist) * self.speed
        else:
            vx = vy = 0.0
        self.vx = self.vx * 0.85 + vx * 0.15
        self.vy = self.vy * 0.85 + vy * 0.15
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x = clamp(self.x, 0, WORLD_W)
        self.y = clamp(self.y, 0, WORLD_H)

    def draw(self, surf, camx, camy, outline=True):
        pygame.draw.circle(surf, self.color, (int(self.x - camx), int(self.y - camy)), self.r)
        if outline:
            pygame.draw.circle(surf, (255,255,255), (int(self.x - camx), int(self.y - camy)), self.r, 2)

class game:
    def __init__(self):
        self.reset()

    def reset(self):
        random.seed()
        self.player = blob(WORLD_W//2, WORLD_H//2, mass=600, color=(120,200,155))
        self.bots = []
        for _ in range(10):
            bx = random.randint(50, WORLD_W-50)
            by = random.randint(50, WORLD_H-50)
            mass = random.randint(200,900)
            col = random.choice([(255,144,120),(255,200,90),(170,240,170),(160,200,255),(255,120,180)])
            self.bots.append(blob(bx, by, mass, col))
        self.food = [food(random.randint(0, WORLD_W), random.randint(0, WORLD_H)) for _ in range(1000)]
        self.camx, self.camy = 0.0, 0.0
        self.time = 0.0
        self.state = "play"
        self.cells = [self.player]
        self.last_eject = 0

    def update_camera(self, dt):
        avgx = sum(b.x for b in self.cells) / len(self.cells)
        avgy = sum(b.y for b in self.cells) / len(self.cells)
        self.camx = avgx - WIDTH/2
        self.camy = avgy - HEIGHT/2
        self.camx = clamp(self.camx, 0, WORLD_W - WIDTH)
        self.camy = clamp(self.camy, 0, WORLD_H - HEIGHT)

    def update_cells(self, dt):
        mx, my = pygame.mouse.get_pos()
        tx = self.camx + mx
        ty = self.camy + my
        for c in self.cells:
            c.move_towards(tx, ty, dt)
            if c.split_timer > 0:
                c.split_timer -= dt

    def update_food_motion(self, dt):
        for f in self.food:
            f.x += f.vx * dt
            f.y += f.vy * dt
            f.vx *= 0.9
            f.vy *= 0.9

    def eat_food(self):
        for c in self.cells:
            pr = c.r
            px, py = c.x, c.y
            remaining = []
            for f in self.food:
                if (f.x - px)**2 + (f.y - py)**2 < (pr + f.r)**2:
                    c.mass += f.r * 0.9
                else:
                    remaining.append(f)
            self.food = remaining

    def split(self):
        if len(self.cells) >= 2:
            return
        c = self.player
        if c.mass < 400:
            return
        c.mass /= 2
        angle = random.random() * math.tau
        nx = c.x + math.cos(angle) * c.r * 2
        ny = c.y + math.sin(angle) * c.r * 2
        new_cell = blob(nx, ny, c.mass, c.color)
        new_cell.vx = math.cos(angle) * 500
        new_cell.vy = math.sin(angle) * 500
        new_cell.split_timer = 6.0
        self.cells.append(new_cell)

    def check_merge(self):
        if len(self.cells) < 2: 
            return
        c1, c2 = self.cells
        if c1.split_timer <= 0 and c2.split_timer <= 0:
            dx, dy = c2.x - c1.x, c2.y - c1.y
            if dx*dx + dy*dy < (c1.r + c2.r)**2:
                total_mass = c1.mass + c2.mass
                c1.mass = total_mass
                self.cells = [c1]

    def eject_mass(self):
        now = pygame.time.get_ticks() / 1000
        if now - self.last_eject < 0.5:
            return
        self.last_eject = now
        c = self.player
        if c.mass < 250:
            return
        loss = c.mass * 0.03
        c.mass -= loss
        mx, my = pygame.mouse.get_pos()
        tx, ty = self.camx + mx, self.camy + my
        dx, dy = tx - c.x, ty - c.y
        dist = math.hypot(dx, dy) + 1e-5
        f = food(c.x + dx/dist*c.r, c.y + dy/dist*c.r)
        f.vx = (dx / dist) * 350
        f.vy = (dy / dist) * 350
        self.food.append(f)

    def update(self, dt):
        if self.state != "play":
            return
        self.update_cells(dt)
        self.update_food_motion(dt)
        self.eat_food()
        self.check_merge()
        self.update_camera(dt)

    def draw(self):
        draw_grid(WINDOW, self.camx, self.camy)
        for f in self.food:
            f.draw(WINDOW, self.camx, self.camy)
        for c in self.cells:
            c.draw(WINDOW, self.camx, self.camy)
        font = pygame.font.SysFont(None, 24)
        pygame.draw.rect(WINDOW, (25,28,36), (10,10,300,60), border_radius=8)
        WINDOW.blit(font.render(f"Mass: {int(sum(c.mass for c in self.cells))}", True, (235,235,245)), (20,18))
        WINDOW.blit(font.render("[Q] split | [E] eject | [ESC] salir", True, (200,220,255)), (20,42))

    def run(self):
        running = True
        while running:
            dt = CLOCK.tick(FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False
                    elif e.key == pygame.K_q:
                        self.split()
                    elif e.key == pygame.K_e:
                        self.eject_mass()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

def main():
    g = game()
    g.run()

if __name__ == "__main__":
    main()
