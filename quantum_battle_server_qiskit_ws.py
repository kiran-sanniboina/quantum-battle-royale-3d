import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np, math, random, time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# ---------- Config ----------
SCREEN_W, SCREEN_H = 1600, 900
PLAYER_SPEED = 3.0
RADAR_RANGE = 400
SCAN_DURATION = 6.0
SCAN_COOLDOWN = 4.0
PULSE_SPEED = 8.0
NUM_BOTS = 10
FPS = 60
CANNON_SPEED = 90.0
ENEMY_FIRE_INTERVAL = 3.0
ENEMY_FIRE_CHANCE = 0.4
ENEMY_CANNON_SPEED = 70.0
PLAYER_MAX_HEALTH = 100
PLAYER_DAMAGE = 5
GRAVITY = 9.8
BOT_AREA_LIMIT = 250
SHIP_FLOAT_OFFSET = 5.0
class QuantumRadar:
    def __init__(self, reflection_coeff=0.8, noise_factor=0.05):
        self.simulator = AerSimulator()
        self.reflection_coeff = reflection_coeff
        self.noise_factor = noise_factor
    def scan(self, shots=512):
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        noise_model = NoiseModel()
        if self.noise_factor > 0:
            error_1q = depolarizing_error(self.noise_factor, 1)
            error_2q = depolarizing_error(self.noise_factor, 2)
            noise_model.add_all_qubit_quantum_error(error_1q, ['h'])
            noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])
        compiled = transpile(qc, self.simulator)
        result = self.simulator.run(compiled, shots=shots, noise_model=noise_model).result()
        counts = result.get_counts()
        c00 = counts.get('00', 0)
        c11 = counts.get('11', 0)
        p_corr = (c00 + c11) / shots
        total_corr = (self.reflection_coeff * p_corr) + (1 - self.reflection_coeff) / 2
        return total_corr
# ---------- Setup ----------
pygame.init()
pygame.display.set_mode((SCREEN_W, SCREEN_H), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Quantum Pirate 3D — Armada Edition ⚛️")
clock = pygame.time.Clock()
info_font = pygame.font.Font(None, 32)
victory_font = pygame.font.Font(None, 80)
flag_font = pygame.font.Font(None, 36)
pygame.mouse.set_visible(True)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_POSITION, [0, 200, 200, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.3, 1])
glClearColor(0.02, 0.05, 0.1, 1.0)
glMatrixMode(GL_PROJECTION)
gluPerspective(60, SCREEN_W / SCREEN_H, 1, 4000)
glMatrixMode(GL_MODELVIEW)

# ---------- Helpers ----------
def get_mouse_direction(mx, my, player_pos):
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    near = gluUnProject(mx, SCREEN_H - my, 0.0, modelview, projection, viewport)
    far = gluUnProject(mx, SCREEN_H - my, 1.0, modelview, projection, viewport)
    direction = np.array(far) - np.array(near)
    direction /= np.linalg.norm(direction)
    direction[1] = max(0.2, direction[1])
    direction /= np.linalg.norm(direction)
    return direction

def wave_height(x, z, t):
    return (
        math.sin(0.015 * x + t * 0.8) * 2.5 +
        math.cos(0.012 * z + t * 1.0) * 3.0 +
        math.sin(0.008 * (x + z) + t * 1.5) * 1.5 +
        math.sin(0.02 * (x - z) + t * 0.5) * 2.0
    )

def wave_normal(x, z, t):
    eps = 1.0
    hL = wave_height(x - eps, z, t)
    hR = wave_height(x + eps, z, t)
    hD = wave_height(x, z - eps, t)
    hU = wave_height(x, z + eps, t)
    n = np.array([hL - hR, 2.0, hD - hU])
    n /= np.linalg.norm(n)
    return n

def draw_sky():
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glBegin(GL_QUADS)
    glColor3f(0.05, 0.15, 0.3)
    glVertex3f(-4000, 2000, -4000)
    glVertex3f(4000, 2000, -4000)
    glColor3f(0.6, 0.8, 1.0)
    glVertex3f(4000, -500, 4000)
    glVertex3f(-4000, -500, 4000)
    glEnd()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def draw_ocean(time_offset, player_pos):
    glPushMatrix()
    tile_size = 150
    half_tiles = 6
    glDisable(GL_LIGHTING)
    glBegin(GL_QUADS)
    for i in range(-half_tiles, half_tiles + 1):
        for j in range(-half_tiles, half_tiles + 1):
            cx = player_pos[0] + i * tile_size
            cz = player_pos[2] + j * tile_size
            for (x, z) in [
                (cx - tile_size / 2, cz - tile_size / 2),
                (cx - tile_size / 2, cz + tile_size / 2),
                (cx + tile_size / 2, cz + tile_size / 2),
                (cx + tile_size / 2, cz - tile_size / 2)
            ]:
                y = wave_height(x, z, time_offset * 2)
                c = 0.5 + 0.5 * math.sin(0.002 * (x + z + time_offset * 30))
                glColor3f(0.0 + 0.05*c, 0.25 + 0.4*c, 0.5 + 0.4*c)
                glVertex3f(x, y, z)
    glEnd()
    glEnable(GL_LIGHTING)
    glPopMatrix()

# ---------- Ships ----------
def draw_pirate_ship(size=1.0, color=(0.5, 0.3, 0.1), flag=False, enemy=False):
    glPushMatrix()
    glScalef(size, size, size)
    glBegin(GL_QUAD_STRIP)
    glColor3f(*color)
    for i in range(-10, 11):
        x = i
        z = math.cos(i * 0.2) * 3
        glVertex3f(x, 0, z)
        glVertex3f(x, 3, z)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(color[0]*1.2, color[1]*1.2, color[2]*1.2)
    glVertex3f(-10,3,-3); glVertex3f(10,3,-3)
    glVertex3f(10,3,3); glVertex3f(-10,3,3)
    glEnd()
    glColor3f(0.4,0.25,0.1)
    glBegin(GL_QUADS)
    glVertex3f(-0.3,3,0); glVertex3f(0.3,3,0)
    glVertex3f(0.3,15,0); glVertex3f(-0.3,15,0)
    glEnd()
    glColor3f(0.9,0.9,0.9)
    glBegin(GL_TRIANGLES)
    glVertex3f(0.3,15,0); glVertex3f(7,9,0); glVertex3f(0.3,3,0)
    glEnd()
    if flag:
        if enemy:
            glColor3f(0.8,0.1,0.1)
        else:
            glColor3f(0,0,0)
        glBegin(GL_QUADS)
        glVertex3f(0.3,15,0)
        glVertex3f(3 if enemy else 4,14,0)
        glVertex3f(3 if enemy else 4,12.5,0)
        glVertex3f(0.3,12.5,0)
        glEnd()
    glPopMatrix()

class Ship:
    def __init__(self, x, y, z, color, size=1.0, speed=1.0, is_player=False):
        self.pos = np.array([x, y, z], float)
        self.vel = np.array([random.uniform(-1,1),0,random.uniform(-1,1)]) * speed
        self.color = color; self.size = size
        self.is_player = is_player; self.alive = True
        self.visible = is_player
        self.last_fire_time = 0
    def update(self, dt):
        if not self.alive: return
        self.pos += self.vel * dt * 30
        for i in (0, 2):
            if abs(self.pos[i]) > BOT_AREA_LIMIT:
                self.vel[i] *= -1
    def draw(self, t):
        if not self.alive or (not self.visible and not self.is_player): return
        y = wave_height(self.pos[0], self.pos[2], t*2) + SHIP_FLOAT_OFFSET
        n = wave_normal(self.pos[0], self.pos[2], t*2)
        roll = -math.degrees(math.asin(n[0]*0.4))
        pitch = math.degrees(math.asin(n[2]*0.4))
        glPushMatrix()
        glTranslatef(self.pos[0], y, self.pos[2])
        glRotatef(pitch,1,0,0)
        glRotatef(roll,0,0,1)
        glRotatef(180,0,1,0)
        draw_pirate_ship(size=self.size, color=self.color, flag=True, enemy=not self.is_player)
        glPopMatrix()
# ---------- Ship Setup ----------
player = Ship(0,0,0,(0.6,0.4,0.2), size=3.0, speed=0, is_player=True)
grid_size = int(math.ceil(math.sqrt(NUM_BOTS)))
spacing = ((BOT_AREA_LIMIT * 2) / grid_size) * 2.0
bots = []
for i in range(grid_size):
    for j in range(grid_size):
        if len(bots) >= NUM_BOTS: break
        x = -BOT_AREA_LIMIT + i * spacing + spacing / 2
        z = -BOT_AREA_LIMIT/2 + j * spacing + spacing / 2 + 150
        bots.append(Ship(x, 0, z, (0.4,0.2,0.1), size=2.0, speed=random.uniform(0.3,0.7)))

# ---------- Cannonballs ----------
class Cannonball:
    def __init__(self,pos,dir,speed=CANNON_SPEED,is_enemy=False):
        self.pos=np.array(pos,float)
        self.vel=dir*speed
        self.active=True
        self.is_enemy=is_enemy
    def update(self,dt):
        self.vel[1]-=GRAVITY*dt*5
        self.pos+=self.vel*dt
        if self.pos[1]<-100 or abs(self.pos[0])>1500 or abs(self.pos[2])>1500:
            self.active=False
    def draw(self):
        if not self.active:return
        glColor3f(1,0.2,0.2) if self.is_enemy else glColor3f(1,0.8,0.2)
        glPushMatrix(); glTranslatef(*self.pos)
        q=gluNewQuadric(); gluSphere(q,3,12,12)
        gluDeleteQuadric(q); glPopMatrix()

# ---------- Effects ----------
class Explosion:
    def __init__(self,pos): self.pos=np.array(pos); self.r,self.alpha,self.active=5,1.0,True
    def update(self): self.r+=10; self.alpha-=0.06; self.active=self.alpha>0
    def draw(self): 
        if not self.active:return
        glColor4f(1.0,0.6,0.1,self.alpha)
        glPushMatrix(); glTranslatef(*self.pos)
        q=gluNewQuadric(); gluSphere(q,self.r,16,16)
        gluDeleteQuadric(q); glPopMatrix()

class Smoke:
    def __init__(self,pos):
        self.pos=np.array(pos,float)
        self.r=4; self.alpha=1.0; self.active=True
        self.vel=np.array([random.uniform(-0.3,0.3),random.uniform(0.8,1.2),random.uniform(-0.3,0.3)])
    def update(self):
        self.pos+=self.vel; self.r+=0.4; self.alpha-=0.02; self.active=self.alpha>0
    def draw(self):
        if not self.active:return
        glColor4f(0.4,0.4,0.4,self.alpha)
        glPushMatrix(); glTranslatef(*self.pos)
        q=gluNewQuadric(); gluSphere(q,self.r,8,8)
        gluDeleteQuadric(q); glPopMatrix()

class Splash:
    def __init__(self,pos):
        self.pos=np.array(pos,float); self.alpha=1.0; self.radius=3; self.active=True
    def update(self):
        self.radius+=3; self.alpha-=0.04; self.active=self.alpha>0
    def draw(self):
        if not self.active:return
        glDisable(GL_DEPTH_TEST)
        glColor4f(0.5,0.8,1.0,self.alpha)
        glBegin(GL_LINE_LOOP)
        for i in range(32):
            t=2*math.pi*i/32
            glVertex3f(self.pos[0]+math.cos(t)*self.radius,self.pos[1],self.pos[2]+math.sin(t)*self.radius)
        glEnd(); glEnable(GL_DEPTH_TEST)

# ---------- Radar Pulse ----------
class Pulse:
    def __init__(self,center):
        self.center=np.array(center,float); self.r=1.0; self.alpha=0.7; self.active=True
    def update(self): self.r+=PULSE_SPEED; self.alpha-=0.01; self.active=self.alpha>0
    def draw(self):
        if not self.active:return
        glDisable(GL_DEPTH_TEST)
        glColor4f(0,1,0,self.alpha)
        glBegin(GL_LINE_LOOP)
        for i in range(256):
            t=2*math.pi*i/256
            glVertex3f(self.center[0]+math.cos(t)*self.r,2.0,self.center[2]+math.sin(t)*self.r)
        glEnd(); glEnable(GL_DEPTH_TEST)

def draw_radar_range(center, radius):
    glDisable(GL_DEPTH_TEST)
    glColor4f(0, 1, 0, 0.3)
    glBegin(GL_LINE_LOOP)
    for i in range(256):
        t = 2 * math.pi * i / 256
        glVertex3f(center[0] + math.cos(t) * radius, 2.0, center[2] + math.sin(t) * radius)
    glEnd()
    glEnable(GL_DEPTH_TEST)

# ---------- State ----------
cannonballs=[]; explosions=[]; smokes=[]; splashes=[]; pulses=[]
targets_destroyed=0; hud_opacity=0.0; radar_active=False; last_scan_time=0; victory=False
player_health=PLAYER_MAX_HEALTH; quantum_prob = 0.0

# ---------- Main Loop ----------
running=True
while running:
    dt=clock.tick(FPS)/1000.0; now=time.time(); detected=0
    for e in pygame.event.get():
        if e.type==QUIT:running=False
        if e.type==MOUSEBUTTONDOWN and e.button==1 and not victory:
            mx,my=pygame.mouse.get_pos()
            dir=get_mouse_direction(mx,my,player.pos)
            cannonballs.append(Cannonball(player.pos.copy()+np.array([0,10,0]),dir))
        if e.type==KEYDOWN and e.key==K_q and not victory:
            if now-last_scan_time>SCAN_COOLDOWN:
                last_scan_time=now; radar_active=True
                pulses.append(Pulse(player.pos.copy()))

                # Quantum radar scan
                qradar = QuantumRadar(reflection_coeff=0.8, noise_factor=0.05)
                quantum_corr = qradar.scan()
                quantum_prob = quantum_corr

                if quantum_corr > 0.55:
                    for b in bots:
                        if b.alive and np.linalg.norm(b.pos - player.pos) <= RADAR_RANGE:
                            b.visible = True; detected += 1
                else:
                    for b in bots: b.visible = False

    keys=pygame.key.get_pressed()
    if keys[K_ESCAPE]:running=False
    if not victory:
        if keys[K_w]:player.pos[2]-=PLAYER_SPEED
        if keys[K_s]:player.pos[2]+=PLAYER_SPEED
        if keys[K_a]:player.pos[0]-=PLAYER_SPEED
        if keys[K_d]:player.pos[0]+=PLAYER_SPEED

    # Radar fade
    if radar_active:
        if now-last_scan_time>SCAN_DURATION:
            radar_active=False
            for b in bots:b.visible=False
    hud_opacity=min(1.0,hud_opacity+dt*2.5) if radar_active else max(0.0,hud_opacity-dt*1.5)

    # Ship AI
    for b in bots:
        b.update(dt)
        if b.alive and now-b.last_fire_time>ENEMY_FIRE_INTERVAL and random.random()<ENEMY_FIRE_CHANCE:
            b.last_fire_time=now
            dir = player.pos - b.pos + np.random.uniform(-30,30,3)
            dir[1]=max(5,dir[1]); dir/=np.linalg.norm(dir)
            cannonballs.append(Cannonball(b.pos.copy()+np.array([0,10,0]),dir,ENEMY_CANNON_SPEED,is_enemy=True))

    # Cannonballs
    new_cballs=[]
    for c in cannonballs:
        c.update(dt); hit=False
        if not c.is_enemy:
            for b in bots:
                if b.alive and np.linalg.norm(c.pos-b.pos)<30:
                    b.alive=False; explosions.append(Explosion(b.pos)); smokes.append(Smoke(b.pos))
                    c.active=False; hit=True; targets_destroyed+=1
        else:
            if np.linalg.norm(c.pos-player.pos)<40 and player_health>0:
                player_health=max(0,player_health-PLAYER_DAMAGE)
                explosions.append(Explosion(player.pos)); c.active=False; hit=True
        sea=wave_height(c.pos[0],c.pos[2],now*2)
        if not hit and c.pos[1]<=sea+1:
            splashes.append(Splash([c.pos[0],sea+2,c.pos[2]])); c.active=False
        if c.active:new_cballs.append(c)
    cannonballs=new_cballs

    for arr in [explosions,smokes,splashes,pulses]:
        for obj in arr: obj.update()
        arr[:]=[o for o in arr if o.active]

    alive=sum(1 for b in bots if b.alive)
    if alive==0 and not victory:
        victory=True; print("🏆 Victory! All enemies sunk!")

    # ---------- Rendering ----------
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(player.pos[0],200,player.pos[2]+400,player.pos[0],0,player.pos[2],0,1,0)
    draw_sky(); draw_ocean(now,player.pos)

    for c in cannonballs:c.draw()
    player.draw(now)
    for b in bots:
        if b.alive and b.visible:b.draw(now)
    for e in explosions:e.draw()
    for s in smokes:s.draw()
    for sp in splashes:sp.draw()
    for p in pulses:p.draw()
    if radar_active: draw_radar_range(player.pos, RADAR_RANGE)

    # ---------- HUD ----------
    glDisable(GL_LIGHTING)
    surf=pygame.display.get_surface()
    surf.blit(info_font.render("W/A/S/D Move | Mouse Click Fire | Q Quantum Radar | ESC Quit",True,(0,255,0)),(20,10))
    surf.blit(flag_font.render("☠",True,(255,255,255)),(SCREEN_W//2+10,SCREEN_H//2-80))

    # Health bar
    pygame.draw.rect(surf,(100,0,0),(20,50,200,20))
    pygame.draw.rect(surf,(0,255,0),(20,50,int(200*(player_health/PLAYER_MAX_HEALTH)),20))
    surf.blit(info_font.render(f"Health: {player_health}",True,(255,255,255)),(230,48))

    # Quantum radar HUD
    if hud_opacity>0:
        alpha=int(255*hud_opacity)
        x,y=SCREEN_W-270,15
        box=pygame.Surface((260,115),pygame.SRCALPHA)
        pygame.draw.rect(box,(0,40,0,int(180*hud_opacity)),(0,0,260,115),border_radius=8)
        pygame.draw.rect(box,(0,255,0,alpha),(0,0,260,115),2,border_radius=8)
        surf.blit(box,(x-10,y-5))
        hud_font=pygame.font.Font(None,30)
        for i,line in enumerate([
            f"⚛ Quantum Correlation: {int(quantum_prob*100)}%",
            f"🎯 Detected: {detected}",
            f"💥 Destroyed: {targets_destroyed}",
            f"🚢 Alive: {alive}"]):
            surf.blit(hud_font.render(line,True,(0,255,0)),(x,y+i*28))

    # Victory overlay
    if victory:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))
        glow = int((math.sin(now * 3) + 1) * 127)
        victory_text = victory_font.render("🏴‍☠️ VICTORY! ALL ENEMIES SUNK!", True, (255, glow, 0))
        rect = victory_text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
        surf.blit(victory_text, rect)
        small_font = pygame.font.Font(None, 40)
        tip_text = small_font.render("Press ESC to return to port...", True, (255, 255, 255))
        tip_rect = tip_text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 80))
        surf.blit(tip_text, tip_rect)

    glEnable(GL_LIGHTING)
    pygame.display.flip()

pygame.quit()
print("[System] Simulation ended cleanly.")
