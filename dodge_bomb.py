import random
import time
import os
import sys
import pygame as pg
WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))
def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if obj_rct.left < 0 or obj_rct.right > WIDTH:
        yoko = False
    if obj_rct.top < 0 or obj_rct.bottom > HEIGHT:
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    ovl = pg.Surface((WIDTH, HEIGHT))
    ovl.set_alpha(200)
    ovl.fill((0, 0, 0))
    screen.blit(ovl, (0, 0))

    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255 ,255, 255))
    txt_rct = txt.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
    screen.blit(txt, (WIDTH//2 - 150, HEIGHT//2 - 40))

    sad_img = pg.image.load("fig/8.png")
    sad_img = pg.transform.rotozoom(sad_img, 0, 2.0)
    left_sad_rct = sad_img.get_rect(center=(txt_rct.left - sad_img.get_width()//2 - 20, txt_rct.centery)) # テキストの左端から少し離して配置
    screen.blit(sad_img, left_sad_rct)    
    right_sad_rct = sad_img.get_rect(center=(txt_rct.right + sad_img.get_width()//2 + 20, txt_rct.centery)) # テキストの右端から少し離して配置
    screen.blit(sad_img, right_sad_rct)

    pg.display.update()
    time.sleep(5)


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5, +5
    kk_rct.center = 300, 200
    clock = pg.time.Clock()
    tmr = 0
    DELTA = {
        pg.K_UP:    (0, -5),
        pg.K_DOWN:  (0, +5),
        pg.K_LEFT:  (-5, 0),
        pg.K_RIGHT: (+5, 0)
    }

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for k, delta in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += delta[0]
                sum_mv[1] += delta[1]
        kk_rct.move_ip(sum_mv)
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(bb_img, bb_rct)
        screen.blit(kk_img, kk_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
