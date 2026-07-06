import pygame
import win32api
import win32con
import win32gui

from Bug import Bug
from util import screen, WIDTH, HEIGHT

pygame.display.set_caption("Screen Bug")


hwnd = pygame.display.get_wm_info()["window"]

win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, WIDTH, HEIGHT, 0)

style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
win32gui.SetWindowLong(
    hwnd,
    win32con.GWL_EXSTYLE,
    style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
)

win32gui.SetLayeredWindowAttributes(
    hwnd, win32api.RGB(255, 0, 255), 0, win32con.LWA_COLORKEY
)

TRANSPARENT = (255, 0, 255)
BLACK = (0, 0, 0)



clock = pygame.time.Clock()
bugs = []
for i in range(1):
    bugs.append(Bug())


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:   # Press ESC to quit
                pygame.quit()
                exit()


    screen.fill(TRANSPARENT)
    for i in range(len(bugs)):
        bugs[i].update()



    pygame.display.flip()
    clock.tick(60)