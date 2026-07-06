import math
import time
import random

from Leg import Leg
from util import *


class Bug:
    # ---- settings ----
    BODY_WIDTH = 10
    BODY_HEIGHT = 14
    ABDOMEN_WIDTH = 12
    ABDOMEN_HEIGHT = 14
    NUM_LEGS_PER_SIDE = 4
    LEG_LENGTHS = [6, 6, 6, 10]
    LEG_DIR = [-1, -1, 1, 1]
    LEG_STEP_OFFSETS = [(LEG_LENGTHS[0]*.8, LEG_LENGTHS[0]*2.5),
                        (LEG_LENGTHS[1], LEG_LENGTHS[1]*2),
                        (LEG_LENGTHS[2], LEG_LENGTHS[2]*2),
                        (LEG_LENGTHS[3], LEG_LENGTHS[3]*2)
                        ]
    LEG_STOP_OFFSETS = [(LEG_LENGTHS[0], LEG_LENGTHS[0]*1.25),
                        (LEG_LENGTHS[1]*2, LEG_LENGTHS[2]/3),
                        (LEG_LENGTHS[2]*2,-LEG_LENGTHS[2]/2),
                        (LEG_LENGTHS[3], -LEG_LENGTHS[3]*1.25)
                        ]
    LEG_VERTICAL_OFFSETS = [5,3,-5,-8]
    UPPER_LOWER_X_PULL_IN_FACTOR = 5
    STOP_LEG_OFFSET = .8
    MAX_SPEED = 5
    ACCELERATION = 1
    STOP_RADIUS = 60
    MIN_WAIT = 3
    MAX_WAIT = 10
    COLOR = (0, 0, 0)
    ABDOMEN_COLOR = (10, 4, 4)
    # ------------------

    mousePressPos = pygame.Vector2(0, 0)

    def __init__(self):
        self.pos = pygame.Vector2(random.randrange(40, WIDTH - 40), random.randrange(40, HEIGHT - 40))
        self.vel = pygame.Vector2(0, 0)
        self.speed = Bug.MAX_SPEED
        self.acc = Bug.ACCELERATION
        self.dir = 0
        self.width = Bug.BODY_WIDTH
        self.height = Bug.BODY_HEIGHT
        self.color = Bug.COLOR
        self.abdomen_color = Bug.ABDOMEN_COLOR

        self.stopRadius = Bug.STOP_RADIUS

        self.targetPos = pygame.Vector2(self.pos)
        self.nextMoveTime = time.time() + random.uniform(Bug.MIN_WAIT, Bug.MAX_WAIT)

        self.size = max(self.width, self.height) * 10
        self.surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.center = pygame.Vector2(self.size / 2, self.size / 2)

        self.body_rect = pygame.Rect(self.center.x - self.width // 2,
                                     self.center.y - self.height // 2,
                                     self.width, self.height)

        self.abdomen_rect = pygame.Rect(self.center.x - Bug.ABDOMEN_WIDTH // 2,
                                        self.center.y + self.height // 3,
                                        Bug.ABDOMEN_WIDTH, Bug.ABDOMEN_HEIGHT)

        self.rightLegs = []
        self.leftLegs = []
        self._initLegs()

    def _initLegs(self):
        xPullIn = Bug.BODY_WIDTH / Bug.UPPER_LOWER_X_PULL_IN_FACTOR
        legLengths = list(Bug.LEG_LENGTHS)
        while len(legLengths) < Bug.NUM_LEGS_PER_SIDE:
            legLengths.append(legLengths[-1])

        for i in range(Bug.NUM_LEGS_PER_SIDE):
            isEdge = (i == 0 or i == Bug.NUM_LEGS_PER_SIDE - 1)
            xOffset = xPullIn if isEdge else 0
            length = legLengths[i]

            rLeg = Leg(pygame.Vector2(self.center.x + self.width / 3.5 - xOffset, self.center.y-Bug.LEG_VERTICAL_OFFSETS[i]), length, -Bug.LEG_DIR[i])
            rLeg.target = pygame.Vector2(rLeg.origin.x + Bug.LEG_STEP_OFFSETS[i][0], rLeg.origin.y + Bug.LEG_STEP_OFFSETS[i][1])
            rLeg.nextStep = pygame.Vector2(rLeg.origin.x + Bug.LEG_STEP_OFFSETS[i][0], rLeg.origin.y - Bug.LEG_STEP_OFFSETS[i][1])
            self.rightLegs.append(rLeg)

            lLeg = Leg(pygame.Vector2(self.center.x - self.width / 2 + xOffset, self.center.y-Bug.LEG_VERTICAL_OFFSETS[i]), length, Bug.LEG_DIR[i])
            lLeg.target = pygame.Vector2(lLeg.origin.x - Bug.LEG_STEP_OFFSETS[i][0], lLeg.origin.y - Bug.LEG_STEP_OFFSETS[i][1])
            lLeg.nextStep = pygame.Vector2(lLeg.origin.x - Bug.LEG_STEP_OFFSETS[i][0], lLeg.origin.y - Bug.LEG_STEP_OFFSETS[i][1])
            self.leftLegs.append(lLeg)

    def pickNewTarget(self):
        if time.time() >= self.nextMoveTime:
            self.targetPos = pygame.Vector2(random.randrange(40, WIDTH - 40), random.randrange(40, HEIGHT - 40))
            self.nextMoveTime = time.time() + random.uniform(Bug.MIN_WAIT, Bug.MAX_WAIT)

    def faceDirection(self):
        if self.vel.length() > 0:
            self.dir = math.degrees(math.atan2(self.vel.y, self.vel.x)) + 90

    def moveTo(self, pos):
        dist = (pos - self.pos)
        if dist.length() == 0:
            return

        normDist = dist.normalize()
        self.vel += normDist * self.acc
        self.speed = Bug.MAX_SPEED * math.sqrt(dist.magnitude() / (WIDTH / 2))

        if self.vel.magnitude() >= self.speed:
            self.vel = normDist * self.speed

        if dist.magnitude() >= self.stopRadius:
            self.pos += self.vel
        else:
            self.vel = pygame.Vector2(0, 0)

    def draw(self):
        self.surf.fill((0, 0, 0, 0))

        for leg in self.rightLegs + self.leftLegs:
            leg.drawOn(self.surf)

        pygame.draw.ellipse(self.surf, self.color, self.body_rect)
        pygame.draw.ellipse(self.surf, self.abdomen_color, self.abdomen_rect)

        # fangs
        pygame.draw.line(
            self.surf,
            self.color,
            (self.center.x - 4 - .5, self.center.y - self.height / 2 + 2),
            (self.center.x - 2 - .5, self.center.y - self.height / 2 - 3),
            2
        )

        pygame.draw.line(
            self.surf,
            self.color,
            (self.center.x + 4 -.5, self.center.y - self.height / 2 + 2),
            (self.center.x + 2 -.5, self.center.y - self.height / 2 - 3),
            2
        )

        rotated = pygame.transform.rotate(self.surf, -self.dir)
        rect = rotated.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        screen.blit(rotated, rect)

    @staticmethod
    def setMousePressPos():
        if get_mouse_pressed():
            Bug.mousePressPos = get_mouse_pos()

    def update(self):
        self.pickNewTarget()
        Bug.setMousePressPos()
        target = Bug.mousePressPos if get_mouse_pressed() else self.targetPos
        self.moveTo(target)
        self.faceDirection()
        self.updateLegPos()
        self.draw()

    def updateLegPos(self):
        if self.vel.length() == 0:
            for i, rLeg in enumerate(self.rightLegs):
                rLeg.moveToTarget(pygame.Vector2(
                    rLeg.origin.x + Bug.LEG_STOP_OFFSETS[i][0] * Bug.STOP_LEG_OFFSET,
                    rLeg.origin.y - Bug.LEG_STOP_OFFSETS[i][1] * Bug.STOP_LEG_OFFSET
                ), .5)
            for i, lLeg in enumerate(self.leftLegs):
                lLeg.moveToTarget(pygame.Vector2(
                    lLeg.origin.x - Bug.LEG_STOP_OFFSETS[i][0] * Bug.STOP_LEG_OFFSET,
                    lLeg.origin.y - Bug.LEG_STOP_OFFSETS[i][1] * Bug.STOP_LEG_OFFSET
                ), .5)
            return


        angle = math.radians(self.dir)
        rotatedVel = pygame.Vector2(
            self.vel.x * math.cos(angle) + self.vel.y * math.sin(angle),
            -self.vel.x * math.sin(angle) + self.vel.y * math.cos(angle)
        )

        speed = rotatedVel.length()
        reachDir = rotatedVel.normalize() if speed > 0 else pygame.Vector2(0, 0)

        for i in range(len(self.rightLegs)):
            rLeg = self.rightLegs[i]
            lLeg = self.leftLegs[i]


            r_neutral = pygame.Vector2(
                rLeg.origin.x + Bug.LEG_STOP_OFFSETS[i][0] * Bug.STOP_LEG_OFFSET,
                rLeg.origin.y - Bug.LEG_STOP_OFFSETS[i][1] * Bug.STOP_LEG_OFFSET
            )
            l_neutral = pygame.Vector2(
                lLeg.origin.x - Bug.LEG_STOP_OFFSETS[i][0] * Bug.STOP_LEG_OFFSET,
                lLeg.origin.y - Bug.LEG_STOP_OFFSETS[i][1] * Bug.STOP_LEG_OFFSET
            )


            rLeg.target -= rotatedVel
            lLeg.target -= rotatedVel

            rLeg.moveToTarget(rLeg.target)
            lLeg.moveToTarget(lLeg.target)

            if speed == 0:
                continue

            r_drag = (r_neutral - rLeg.target).dot(reachDir)
            l_drag = (l_neutral - lLeg.target).dot(reachDir)


            r_thresh = rLeg.length * 1.5
            l_thresh = lLeg.length * 1.5

            r_is_set1 = (i % 2 == 0)

            r_wants_step = (r_drag > r_thresh)
            l_wants_step = (l_drag > l_thresh)


            r_force = r_thresh * 2.2
            l_force = l_thresh * 2.2


            if r_wants_step and l_wants_step:
                if r_is_set1:
                    rLeg.target = r_neutral + (reachDir * r_thresh)
                else:
                    lLeg.target = l_neutral + (reachDir * l_thresh)
            else:

                if r_wants_step and (l_drag >= 0 or r_drag > r_force):
                    rLeg.target = r_neutral + (reachDir * r_thresh)

                elif l_wants_step and (r_drag >= 0 or l_drag > l_force):
                    lLeg.target = l_neutral + (reachDir * l_thresh)