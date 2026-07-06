import ctypes
import ctypes.wintypes
import pygame

def get_mouse_pos():
    pt = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pygame.Vector2(pt.x, pt.y)

def get_mouse_pressed():
    return ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000 != 0  # left click

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)