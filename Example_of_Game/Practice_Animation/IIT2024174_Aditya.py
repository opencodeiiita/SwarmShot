import pygame
import sys

pygame.init()

W, H = 800, 600

BGC = (255, 255, 255)

s = pygame.display.set_mode((W, H))
pygame.display.set_caption("Sprite Animation Practice")

f = pygame.time.Clock()

class C:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = 4

        self.ss = pygame.image.load("Sprites/Sprites_Pet/PET_Racoon.png").convert_alpha()

        self.fi = 0
        self.ft = 0
        self.fd = 10

        self.o = "down"
        self.s = "down_idle"
        self.sf = self.e()

    def e(self):
        f = {
            "up_idle": [self.ss.subsurface((i * 32, 96, 32, 32)) for i in range(4)],
            "up_move": [self.ss.subsurface((i * 32, 352, 32, 32)) for i in range(4)],
            "down_idle": [self.ss.subsurface((i * 32, 0, 32, 32)) for i in range(4)],
            "down_move": [self.ss.subsurface((i * 32, 160, 32, 32)) for i in range(4)],
            "left_idle": [self.ss.subsurface((i * 32, 64, 32, 32)) for i in range(4)],
            "left_move": [self.ss.subsurface((i * 32, 224, 32, 32)) for i in range(4)],
            "right_idle": [self.ss.subsurface((i * 32, 32, 32, 32)) for i in range(4)],
            "right_move": [self.ss.subsurface((i * 32, 288, 32, 32)) for i in range(4)],
        }
        return f

    def u(self, k):
        if k[pygame.K_UP]:
            self.y -= self.v
            self.s = "up_move"
        elif k[pygame.K_DOWN]:
            self.y += self.v
            self.s = "down_move"
        elif k[pygame.K_LEFT]:
            self.x -= self.v
            self.s = "left_move"
        elif k[pygame.K_RIGHT]:
            self.x += self.v
            self.s = "right_move"
        else:
            if "up" in self.s:
                self.s = "up_idle"
            elif "down" in self.s:
                self.s = "down_idle"
            elif "left" in self.s:
                self.s = "left_idle"
            elif "right" in self.s:
                self.s = "right_idle"

        self.ft += 1
        if self.ft >= self.fd:
            self.ft = 0
            self.fi = (self.fi + 1) % len(self.sf[self.s])

    def d(self, s):
        i = pygame.transform.scale(self.sf[self.s][self.fi], (128, 128))
        s.blit(i, (self.x, self.y))

def m():
    c = C(W // 2, H // 2)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        k = pygame.key.get_pressed()
        c.u(k)

        s.fill(BGC)
        c.d(s)

        pygame.display.flip()
        f.tick(60)

if __name__ == "__main__":
    m()
