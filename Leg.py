import math

import pygame

from util import screen


def sign(x):
    if x == 0:
        return 1
    return abs(x) / x


class Leg:
    def __init__(self, origin, armLen, legDir=1):
        self.legDir = legDir
        self.origin = origin
        self.length = armLen
        self.middle = pygame.Vector2(self.origin.x, self.origin.y + self.length)
        self.end = pygame.Vector2(self.middle.x, self.middle.y + self.length)
        self.currentTarget = pygame.Vector2(self.middle.x, self.middle.y + self.length)

        self.target = pygame.Vector2(0,0)
        self.nextStep = pygame.Vector2(0,0)
        self.dragPos = pygame.Vector2(0, 0)

    def drawOn(self, surf):


        line_color = [5, 5, 5]
        point_color = [3, 1, 1]

        line_width = 2
        point_rad = 0

        # pygame.draw.circle(screen, "BLACK", self.origin, self.length*2 + point_rad, 5)

        # lines
        pygame.draw.line(surf, line_color, self.origin, self.middle, line_width)
        pygame.draw.line(surf, line_color, self.middle, self.end, line_width)

        # points
        pygame.draw.circle(surf, point_color, self.origin, point_rad)
        '''pygame.draw.circle(screen, point_color, self.middle, point_rad)
        pygame.draw.circle(screen, point_color, self.end, point_rad)'''

    def applyIK(self, target, speed=1):




        distX = (self.currentTarget.x - self.origin.x)
        distY = (self.currentTarget.y - self.origin.y)

        dist = math.sqrt(distX ** 2 + distY ** 2)

        if dist > self.length * 2:
            self.currentTarget = self.end

            dist = self.length * 2
        self.currentTarget.x += (target.x - self.end.x) * 0.25 * speed
        self.currentTarget.y += (target.y - self.end.y) * 0.25 * speed





        if distX != 0:
            initialAngle = math.atan(distY / distX)
        else:
            initialAngle = 1.57 * sign(distY)

        if distX < 0:

            negDir = -1
        else:
            negDir = 1

        elbowAngle = self.legDir * math.acos((dist / (self.length * 2))) + initialAngle
        self.end = pygame.Vector2(
            self.origin.x + negDir * math.cos(initialAngle) * dist,
            self.origin.y + negDir * math.sin(initialAngle) * dist
        )

        self.middle = pygame.Vector2(
            self.origin.x + negDir * math.cos(elbowAngle) * self.length,
            self.origin.y + negDir * math.sin(elbowAngle) * self.length
        )




    def snapToTarget(self, target):
        self.applyIK(target)
        self.currentTarget = target

    def moveToTarget(self, target, speed=1):
        self.applyIK(target, speed)

