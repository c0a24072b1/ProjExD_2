import random
import time
import os
import sys
import math
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
    screen.blit(txt, txt_rct)
    sad_img = pg.image.load("fig/8.png")
    sad_img = pg.transform.rotozoom(sad_img, 0, 2.0)
    left_sad_rct = sad_img.get_rect(center=(txt_rct.left - sad_img.get_width()//2 - 20, txt_rct.centery)) 
    screen.blit(sad_img, left_sad_rct)     
    right_sad_rct = sad_img.get_rect(center=(txt_rct.right + sad_img.get_width()//2 + 20, txt_rct.centery)) 
    screen.blit(sad_img, right_sad_rct)
    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_accs = [a for a in range(1, 11)]
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r)) 
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs
    
def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    original_img = pg.image.load("fig/3.png") 
    kk_img_left = pg.transform.rotozoom(original_img, 0, 0.9)
    kk_img_right = pg.transform.flip(kk_img_left, True, False) 
    kk_imgs = {
        (0, 0): kk_img_left, 
        (+5, 0): kk_img_right, 
        (-5, 0): kk_img_left,
        (0, -5): pg.transform.rotozoom(kk_img_right, 90, 1.0),
        (0, +5): pg.transform.rotozoom(kk_img_right, -90, 1.0), 
        (+5, -5): pg.transform.rotozoom(kk_img_right, 45, 1.0), 
        (-5, -5): pg.transform.rotozoom(kk_img_left, -45, 1.0),
        (+5, +5): pg.transform.rotozoom(kk_img_right,-45, 1.0),
        (-5, +5): pg.transform.rotozoom(kk_img_left, 45, 1.0), 
    }
    return kk_imgs.get(sum_mv, kk_img_left)

def calc_orientation(org_rct: pg.Rect, dst_rct: pg.Rect, current_speed: tuple[float, float]) -> tuple[float, float]:
    """
    爆弾RectからこうかとんRectへの方向ベクトルを計算する。
    距離が300未満の場合は、慣性を優先し現在の速度を維持する。
    """
    diff_x = dst_rct.centerx - org_rct.centerx
    diff_y = dst_rct.centery - org_rct.centery
    distance = math.sqrt(diff_x**2 + diff_y**2)

    if distance < 300:
        return current_speed

    if distance == 0:
        return 0, 0
    
    norm = math.sqrt(diff_x**2 + diff_y**2)
    return diff_x / norm, diff_y / norm

def main() -> None:
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")     
    kk_img = get_kk_img((0, 0)) 
    kk_rct = kk_img.get_rect() 
    kk_rct.center = 300, 200
    
    bb_imgs, bb_accs = init_bb_imgs()
    bombs = []
    num_bombs = 1
    for i in range(num_bombs): 
        bb_rct = bb_imgs[0].get_rect()
        bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        vx = random.choice([-1, 1])
        vy = random.choice([-1, 1])
        bombs.append({"rct": bb_rct, "vx": vx, "vy": vy, "img": bb_imgs[0]})

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
        
        kk_img = get_kk_img(tuple(sum_mv)) 
        kk_rct.move_ip(sum_mv)
        
        if kk_rct.left < 0: kk_rct.left = 0
        if kk_rct.right > WIDTH: kk_rct.right = WIDTH
        if kk_rct.top < 0: kk_rct.top = 0
        if kk_rct.bottom > HEIGHT: kk_rct.bottom = HEIGHT

        idx = min(tmr // 500, 9) 
        current_bb_img = bb_imgs[idx] 
        current_acc = bb_accs[idx]

        for bomb in bombs: 
            vx, vy = calc_orientation(bomb["rct"], kk_rct, (bomb["vx"], bomb["vy"]))
            bomb["vx"], bomb["vy"] = vx, vy

            base_speed = math.sqrt(50)
            actual_vx = bomb["vx"] * base_speed * current_acc
            actual_vy = bomb["vy"] * base_speed * current_acc
            
            bomb["rct"].move_ip(actual_vx, actual_vy)
            
            yoko, tate = check_bound(bomb["rct"])
            if not yoko:
                bomb["vx"] *= -1
            if not tate:
                bomb["vy"] *= -1
            
            screen.blit(current_bb_img, bomb["rct"])
            
            if kk_rct.colliderect(bomb["rct"]): 
                gameover(screen)
                return

        screen.blit(kk_img, kk_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()