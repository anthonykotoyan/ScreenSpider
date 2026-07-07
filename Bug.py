import math
import time
import random

import pygame

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

    LEG_STEP_OFFSETS = [
        (LEG_LENGTHS[0] * .8, LEG_LENGTHS[0] * 2.5),
        (LEG_LENGTHS[1], LEG_LENGTHS[1] * 2),
        (LEG_LENGTHS[2], LEG_LENGTHS[2] * 2),
        (LEG_LENGTHS[3], LEG_LENGTHS[3] * 2)
    ]

    LEG_STOP_OFFSETS = [
        (LEG_LENGTHS[0], LEG_LENGTHS[0] * 1.25),
        (LEG_LENGTHS[1] * 2, LEG_LENGTHS[2] / 3),
        (LEG_LENGTHS[2] * 2, -LEG_LENGTHS[2] / 2),
        (LEG_LENGTHS[3], -LEG_LENGTHS[3] * 1.25)
    ]

    LEG_VERTICAL_OFFSETS = [5, 3, -5, -8]

    UPPER_LOWER_X_PULL_IN_FACTOR = 5
    STOP_LEG_OFFSET = .8

    MAX_SPEED = 3
    ACCELERATION = .1
    STOP_RADIUS = 10

    # movement steering
    STEERING_FORCE = .28
    BRAKE_FORCE = .55
    ARRIVE_RADIUS = 170

    # speed penalty based on body angle vs movement angle
    FORWARD_SPEED_MULT = 1.0
    SIDE_SPEED_MULT = 0.55
    BACKWARD_SPEED_MULT = 0.25

    MIN_WAIT = 1
    MAX_WAIT = 4

    COLOR = (0, 0, 0)
    ABDOMEN_COLOR = (10, 4, 4)

    # turning
    TURN_DAMPING = 0.12
    MAX_TURN_SPEED = 4

    # wandering
    WANDER_MAX_ANGLE = 45
    WANDER_CHANGE_SPEED = 0.035
    WANDER_TARGET_CHANGE_CHANCE = 0.025
    WANDER_DISTANCE_FADE = 180

    # leg stepping
    STEP_THRESHOLD_MULT = 1.5
    FORCE_STEP_MULT = 2.2
    TURN_EPSILON = 0.01
    # ------------------

    mousePressPos = pygame.Vector2(0, 0)

    def __init__(self):
        self.pos = pygame.Vector2(
            random.randrange(40, WIDTH - 40),
            random.randrange(40, HEIGHT - 40)
        )

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

        self.wanderAmount = random.uniform(-1, 1)
        self.wanderTarget = random.uniform(-1, 1)

        self.moveFacingDir = pygame.Vector2(0, -1)

        self.size = max(self.width, self.height) * 10
        self.surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.center = pygame.Vector2(self.size / 2, self.size / 2)

        self.body_rect = pygame.Rect(
            self.center.x - self.width // 2,
            self.center.y - self.height // 2,
            self.width,
            self.height
        )

        self.abdomen_rect = pygame.Rect(
            self.center.x - Bug.ABDOMEN_WIDTH // 2,
            self.center.y + self.height // 3,
            Bug.ABDOMEN_WIDTH,
            Bug.ABDOMEN_HEIGHT
        )

        self.rightLegs = []
        self.leftLegs = []

        self._initLegs()

    def _initLegs(self):
        xPullIn = Bug.BODY_WIDTH / Bug.UPPER_LOWER_X_PULL_IN_FACTOR

        legLengths = list(Bug.LEG_LENGTHS)
        while len(legLengths) < Bug.NUM_LEGS_PER_SIDE:
            legLengths.append(legLengths[-1])

        for i in range(Bug.NUM_LEGS_PER_SIDE):
            isEdge = i == 0 or i == Bug.NUM_LEGS_PER_SIDE - 1
            xOffset = xPullIn if isEdge else 0
            length = legLengths[i]

            rLeg = Leg(
                pygame.Vector2(
                    self.center.x + self.width / 3.5 - xOffset,
                    self.center.y - Bug.LEG_VERTICAL_OFFSETS[i]
                ),
                length,
                -Bug.LEG_DIR[i]
            )

            rLeg.target = pygame.Vector2(
                rLeg.origin.x + Bug.LEG_STEP_OFFSETS[i][0],
                rLeg.origin.y + Bug.LEG_STEP_OFFSETS[i][1]
            )

            rLeg.nextStep = pygame.Vector2(
                rLeg.origin.x + Bug.LEG_STEP_OFFSETS[i][0],
                rLeg.origin.y - Bug.LEG_STEP_OFFSETS[i][1]
            )

            self.rightLegs.append(rLeg)

            lLeg = Leg(
                pygame.Vector2(
                    self.center.x - self.width / 2 + xOffset,
                    self.center.y - Bug.LEG_VERTICAL_OFFSETS[i]
                ),
                length,
                Bug.LEG_DIR[i]
            )

            lLeg.target = pygame.Vector2(
                lLeg.origin.x - Bug.LEG_STEP_OFFSETS[i][0],
                lLeg.origin.y - Bug.LEG_STEP_OFFSETS[i][1]
            )

            lLeg.nextStep = pygame.Vector2(
                lLeg.origin.x - Bug.LEG_STEP_OFFSETS[i][0],
                lLeg.origin.y - Bug.LEG_STEP_OFFSETS[i][1]
            )

            self.leftLegs.append(lLeg)

    def pickNewTarget(self):
        if time.time() >= self.nextMoveTime:
            self.targetPos = pygame.Vector2(
                random.randrange(40, WIDTH - 40),
                random.randrange(40, HEIGHT - 40)
            )

            self.nextMoveTime = time.time() + random.uniform(
                Bug.MIN_WAIT,
                Bug.MAX_WAIT
            )

    def faceDirection(self, direction, damping=TURN_DAMPING):
        if direction.length_squared() == 0:
            return

        targetDir = math.degrees(math.atan2(direction.y, direction.x)) + 90

        diff = (targetDir - self.dir + 180) % 360 - 180

        turnAmount = diff * damping

        if turnAmount > Bug.MAX_TURN_SPEED:
            turnAmount = Bug.MAX_TURN_SPEED
        elif turnAmount < -Bug.MAX_TURN_SPEED:
            turnAmount = -Bug.MAX_TURN_SPEED

        self.dir += turnAmount
        self.dir %= 360

    def moveDir(self, direction):
        if direction.length_squared() == 0:
            return

        direction = direction.normalize()

        desiredVel = direction * self.speed
        steering = desiredVel - self.vel

        if self.vel.length_squared() > self.speed * self.speed:
            maxForce = Bug.BRAKE_FORCE
        else:
            maxForce = Bug.STEERING_FORCE

        if steering.length_squared() > maxForce * maxForce:
            steering.scale_to_length(maxForce)

        self.vel += steering

        if self.vel.length_squared() > self.speed * self.speed:
            if self.speed <= 0:
                self.vel = pygame.Vector2(0, 0)
            else:
                self.vel.scale_to_length(self.speed)

        self.pos += self.vel

    def moveTo(self, pos):
        dist = pos - self.pos

        if dist.length_squared() == 0:
            self.vel = pygame.Vector2(0, 0)
            return

        distance = dist.length()

        if distance < self.stopRadius:
            self.vel = pygame.Vector2(0, 0)
            return

        targetDir = dist.normalize()

        if random.random() < Bug.WANDER_TARGET_CHANGE_CHANCE:
            self.wanderTarget = random.uniform(-1, 1)

        self.wanderAmount += (
            self.wanderTarget - self.wanderAmount
        ) * Bug.WANDER_CHANGE_SPEED

        wanderFade = min(distance / Bug.WANDER_DISTANCE_FADE, 1)

        wanderAngle = math.radians(
            self.wanderAmount * Bug.WANDER_MAX_ANGLE * wanderFade
        )

        cosA = math.cos(wanderAngle)
        sinA = math.sin(wanderAngle)

        moveDirection = pygame.Vector2(
            targetDir.x * cosA - targetDir.y * sinA,
            targetDir.x * sinA + targetDir.y * cosA
        )

        if moveDirection.length_squared() == 0:
            moveDirection = targetDir
        else:
            moveDirection = moveDirection.normalize()

        self.moveFacingDir = pygame.Vector2(moveDirection)

        bodyAngle = math.radians(self.dir)

        bodyForward = pygame.Vector2(
            math.sin(bodyAngle),
            -math.cos(bodyAngle)
        )

        moveDot = bodyForward.dot(moveDirection)
        moveDot = max(-1, min(1, moveDot))

        if moveDot >= 0:
            speedMult = Bug.SIDE_SPEED_MULT + (
                Bug.FORWARD_SPEED_MULT - Bug.SIDE_SPEED_MULT
            ) * moveDot
        else:
            speedMult = Bug.BACKWARD_SPEED_MULT + (
                Bug.SIDE_SPEED_MULT - Bug.BACKWARD_SPEED_MULT
            ) * (moveDot + 1)

        arriveMult = min(distance / Bug.ARRIVE_RADIUS, 1)

        self.speed = min(
            Bug.MAX_SPEED * arriveMult * speedMult,
            Bug.MAX_SPEED
        )

        self.moveDir(moveDirection)

    def draw(self):
        self.surf.fill((0, 0, 0, 0))

        for leg in self.rightLegs + self.leftLegs:
            leg.drawOn(self.surf)

        pygame.draw.ellipse(self.surf, self.color, self.body_rect)
        pygame.draw.ellipse(self.surf, self.abdomen_color, self.abdomen_rect)

        # fangs
        pygame.draw.line(
            self.surf,
            self.abdomen_color,
            (self.center.x - 4 - .5, self.center.y - self.height / 2 + 2),
            (self.center.x - 2 - .5, self.center.y - self.height / 2 - 3),
            2
        )

        pygame.draw.line(
            self.surf,
            self.abdomen_color,
            (self.center.x + 4 - .5, self.center.y - self.height / 2 + 2),
            (self.center.x + 2 - .5, self.center.y - self.height / 2 - 3),
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

        oldPos = pygame.Vector2(self.pos)
        oldDir = self.dir

        self.moveTo(target)

        self.faceDirection(self.moveFacingDir)

        self.updateLegPos(oldPos, oldDir)
        self.draw()

    def updateLegPos(self, oldPos, oldDir):
        centerMove = self.pos - oldPos
        turnAmount = abs((self.dir - oldDir + 180) % 360 - 180)

        isMoving = centerMove.length_squared() > 0
        isTurning = turnAmount > Bug.TURN_EPSILON

        if not isMoving and not isTurning:
            for i, rLeg in enumerate(self.rightLegs):
                rLeg.target = pygame.Vector2(
                    rLeg.origin.x + Bug.LEG_STOP_OFFSETS[i][0] * Bug.STOP_LEG_OFFSET,
                    rLeg.origin.y - Bug.LEG_STOP_OFFSETS[i][1] * Bug.STOP_LEG_OFFSET
                )
                rLeg.moveToTarget(rLeg.target, .5)

            for i, lLeg in enumerate(self.leftLegs):
                lLeg.target = pygame.Vector2(
                    lLeg.origin.x - Bug.LEG_STOP_OFFSETS[i][0] * Bug.STOP_LEG_OFFSET,
                    lLeg.origin.y - Bug.LEG_STOP_OFFSETS[i][1] * Bug.STOP_LEG_OFFSET
                )
                lLeg.moveToTarget(lLeg.target, .5)

            return

        oldAngle = math.radians(oldDir)
        newAngle = math.radians(-self.dir)

        if isMoving:
            angle = math.radians(-self.dir)

            localMove = pygame.Vector2(
                centerMove.x * math.cos(angle) - centerMove.y * math.sin(angle),
                centerMove.x * math.sin(angle) + centerMove.y * math.cos(angle)
            )

            reachDir = localMove.normalize() if localMove.length_squared() > 0 else pygame.Vector2(0, -1)
            speed = localMove.length()
        else:
            reachDir = pygame.Vector2(0, -1)
            speed = turnAmount

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

            # preserve right foot target through center movement and body rotation
            r_local = rLeg.target - self.center

            r_oldWorldTarget = oldPos + pygame.Vector2(
                r_local.x * math.cos(oldAngle) - r_local.y * math.sin(oldAngle),
                r_local.x * math.sin(oldAngle) + r_local.y * math.cos(oldAngle)
            )

            r_worldFromNewCenter = r_oldWorldTarget - self.pos

            rLeg.target = self.center + pygame.Vector2(
                r_worldFromNewCenter.x * math.cos(newAngle) - r_worldFromNewCenter.y * math.sin(newAngle),
                r_worldFromNewCenter.x * math.sin(newAngle) + r_worldFromNewCenter.y * math.cos(newAngle)
            )

            # preserve left foot target through center movement and body rotation
            l_local = lLeg.target - self.center

            l_oldWorldTarget = oldPos + pygame.Vector2(
                l_local.x * math.cos(oldAngle) - l_local.y * math.sin(oldAngle),
                l_local.x * math.sin(oldAngle) + l_local.y * math.cos(oldAngle)
            )

            l_worldFromNewCenter = l_oldWorldTarget - self.pos

            lLeg.target = self.center + pygame.Vector2(
                l_worldFromNewCenter.x * math.cos(newAngle) - l_worldFromNewCenter.y * math.sin(newAngle),
                l_worldFromNewCenter.x * math.sin(newAngle) + l_worldFromNewCenter.y * math.cos(newAngle)
            )

            rLeg.moveToTarget(rLeg.target)
            lLeg.moveToTarget(lLeg.target)

            if speed == 0:
                continue

            if isMoving:
                r_drag = (r_neutral - rLeg.target).dot(reachDir)
                l_drag = (l_neutral - lLeg.target).dot(reachDir)
            else:
                r_drag = (r_neutral - rLeg.target).length()
                l_drag = (l_neutral - lLeg.target).length()

            r_thresh = rLeg.length * Bug.STEP_THRESHOLD_MULT
            l_thresh = lLeg.length * Bug.STEP_THRESHOLD_MULT

            r_is_set1 = i % 2 == 0

            r_wants_step = r_drag > r_thresh
            l_wants_step = l_drag > l_thresh

            r_force = r_thresh * Bug.FORCE_STEP_MULT
            l_force = l_thresh * Bug.FORCE_STEP_MULT

            if isMoving:
                r_step_target = r_neutral + reachDir * r_thresh
                l_step_target = l_neutral + reachDir * l_thresh
            else:
                r_step_target = r_neutral
                l_step_target = l_neutral

            if r_wants_step and l_wants_step:
                if r_is_set1:
                    rLeg.target = r_step_target
                else:
                    lLeg.target = l_step_target

            else:
                if r_wants_step and (l_drag >= 0 or r_drag > r_force):
                    rLeg.target = r_step_target

                elif l_wants_step and (r_drag >= 0 or l_drag > l_force):
                    lLeg.target = l_step_target