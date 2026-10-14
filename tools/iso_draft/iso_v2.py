"""Bản nháp iso v2: tile pixel iso thật (Yar iso-64x64, CC BY 3.0) qua cainos_grade + sprite LPC của game + HUD v11."""
import sys, json, math
sys.path.insert(0,'/home/user/LastGreenArea/art')
from maps.grade import cainos_grade
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT='/home/user/LastGreenArea/'; SC='/tmp/claude-0/-home-user-LastGreenArea/e1e1a971-c3c2-54a5-94b5-045467fd14f4/scratchpad/'
P='/home/user/iso/phaser/public/3.55/assets/tilemaps/iso/'
import os
GRADE=os.environ.get('GRADE','1')=='1'; TAG='grade' if GRADE else 'orig'
OUT=Image.open(P+'iso-64x64-outside.png').convert('RGBA'); BLD=Image.open(P+'iso-64x64-building.png').convert('RGBA')
if GRADE: OUT=cainos_grade(OUT,0.85); BLD=cainos_grade(BLD,0.85)
def T(sheet,idx,w=1,h=1):
    c,r=idx%10,idx//10; return sheet.crop((c*64,r*64,c*64+64*w,r*64+64*h))
atlas=json.load(open(ROOT+'public/data/atlas.json'))
pages={t['image']:Image.open(ROOT+'public/assets/'+t['image']).convert('RGBA') for t in atlas['textures']}
frames={f['filename']:(t['image'],f) for t in atlas['textures'] for f in t['frames']}
ANIM=json.load(open(ROOT+'data/anim_core.json'))['meta']; CORE=Image.open(ROOT+'assets/characters/anim_core.png').convert('RGBA'); WAND=Image.open(ROOT+'assets/enemies/wanderer_walk_knockdown.png').convert('RGBA')
NAMES={'duong':'Dương','hung':'Hùng','ny':'Ny','son':'Sơn'}
def sprite(id):
    if not GRADE:  # màu gốc: lấy khung 0 'Đi xuống' từ sheet bàn giao, neo chân (32,60)
        if id.startswith('char/'):
            nm=NAMES[id.split('/')[1]]; row=[i for i,(c,a,n) in enumerate(ANIM) if c==nm and a=='Đi xuống'][0]
            return CORE.crop((0,row*64,64,row*64+64)),(32,60)
        if id.startswith('enemy/'): return WAND.crop((0,0,64,64)),(32,60)
    img,f=frames[id]; r=f['frame']; a=f.get('anchor',{'x':0.5,'y':1.0})
    return pages[img].crop((r['x'],r['y'],r['x']+r['w'],r['y']+r['h'])),(a['x']*r['w'],a['y']*r['h'])

# ---- phân loại ô bờ nước: cạnh nào là đất (N=trên-trái, E=trên-phải, S=dưới-phải, W=dưới-trái)
def edge_land(tile):
    a=np.array(tile).astype(int); res={}
    cx,cy=32,48
    for name,(dx,dy) in {'N':(-1,-0.5),'E':(1,-0.5),'S':(1,0.5),'W':(-1,0.5)}.items():
        # điểm giữa cạnh = tâm + hướng*(tỉ lệ) ; cạnh N: từ (0,48) tới (32,32) → trung điểm (16,40)
        pts={'N':[(8+k*2,44-k) for k in range(12)],'E':[(40+k*2,32+k) for k in range(12)],'S':[(40+k*2,64-k-1) for k in range(12)],'W':[(8+k*2,52+k) for k in range(12)]}[name]
        blue=0; n=0
        for x,y in pts:
            x=min(63,max(0,x)); y=min(63,max(0,y)); r,g,b,al=a[y,x]
            if al<10: continue
            n+=1; blue+= 1 if (b>r+15 and b>g-10) else 0
        res[name]= (n==0) or (blue/n<0.5)
    return res
RAW=Image.open(P+'iso-64x64-outside.png').convert('RGBA')
shore={}
for idx in list(range(80,84))+list(range(86,96))+[100,101,102]:
    m=edge_land(T(RAW,idx)); key=''.join(k for k in 'NESW' if m[k]); shore.setdefault(key,idx)
print('shore masks:',shore)

# ---- bản đồ 18×18
N=36; LO=-12
WATER=85
grass=lambda rng: rng.choice([1,1,1,1,1,1,4,10,11,13,14,16,17,20,22,23])
rng=np.random.default_rng(7)
water=np.zeros((N,N),bool)
for j in range(N):
    for i in range(N):
        if 10<=i+LO<=11: water[j,i]=True
bridge={(10,8),(11,8)}
ridge={(i,1) for i in range(-12,9)}|{(i,-3) for i in range(12,24)}
canvas=Image.new('RGBA',(800,450),(0,0,0,0))
CX,CY=400,40
def scr(i,j): return CX+(i-j)*32, CY+(i+j)*16
def paste_tile(im,i,j,w=1,h=1):
    x,y=scr(i,j); canvas.alpha_composite(im,(int(x-32),int(y-48-(h-1)*64+(w-1)*0)))  # ô 64×64: tâm hình thoi (32,48)
def mask_at(j,i):
    def land(jj,ii): return not (0<=jj<N and 0<=ii<N and water[jj,ii])
    m=''
    if land(j-1,i): m+='N'   # j-1 = cạnh trên-trái
    if land(j,i+1): m+='E'
    if land(j+1,i): m+='S'
    if land(j,i-1): m+='W'
    return m
for s in range(2*N-1):
    for jj in range(N):
        ii=s-jj
        if not 0<=ii<N: continue
        i,j=ii+LO,jj+LO
        if (i,j) in bridge: paste_tile(T(OUT,WATER),i,j); paste_tile(T(BLD,50),i,j); continue
        if water[jj,ii]:
            m=mask_at(jj,ii)
            idx=shore.get(m, WATER)
            paste_tile(T(OUT,idx),i,j)
        else:
            paste_tile(T(OUT,int(grass(rng))),i,j)
# ---- vật thể (billboard) theo độ sâu
objs=[]
for i,j in ridge: objs.append((i,j,T(OUT,74 if i%3 else 77),'tile'))
pine=lambda k: T(OUT,122+k,1,2); tree=lambda k: T(OUT,140+k,1,2); bigtree=T(OUT,147,3,2); bush=lambda k: T(OUT,[120,121,126,127,128,129][k])
rock=lambda k: T(OUT,[50,51,52,56,59][k]); log=T(OUT,124); tuft=lambda k: T(OUT,110+k)
placements=[(2.5,3,'pine',0),(4,2.6,'pine',1),(6.5,2.8,'tree',0),(1,5,'tree',2),(3.2,6.5,'pine',1),(0.8,8.5,'tree',0),(2,11,'pine',0),(4.5,12.5,'tree',2),(7,13,'pine',1),(1.5,14.5,'tree',0),(14,3,'tree',2),(16,5,'pine',0),(15.5,12,'tree',0),(13.5,15,'pine',1),(16.5,14.5,'tree',2),
            (5.5,8.2,'bush',0),(6.2,9.8,'bush',2),(8.3,5.5,'bush',3),(3.6,9.6,'bush',4),(13.2,7.5,'bush',1),(14.6,9.2,'bush',5),(8.8,12.8,'bush',0),
            (7.5,4.2,'rock',0),(2.2,8.2,'rock',3),(13.4,11.6,'rock',4),(9.2,10.6,'log',0),(4.2,4.8,'tuft',1),(6.8,11.4,'tuft',4),(12.8,13.4,'tuft',6)]
for i,j,k,v in placements:
    im={'pine':pine,'tree':tree,'bush':bush,'rock':rock,'tuft':tuft}.get(k,lambda v:log)(v)
    objs.append((i,j,im,'tall' if k in('pine','tree') else 'tile'))
objs.append((5.5,4.5,bigtree,'big'))
# chòi đá: tường có cửa (48) + mái (29)
hut=(14,5.5)
# đội + Biến Thể
team=[('char/hung/di-xuong/0',6.0,8.9),('char/duong/di-xuong/0',6.6,8.4),('char/son/di-xuong/0',6.1,9.6),('char/ny/di-xuong/0',6.7,9.2)]
zomb=('enemy/ke-lang-thang/le-buoc-trai/0',8.6,8.0)
def ordered():
    L=[]
    for i,j,im,kind in objs: L.append((i+j,'obj',(i,j,im,kind)))
    for id,i,j in team: L.append((i+j,'char',(id,i,j)))
    L.append((zomb[1]+zomb[2],'char',zomb)); L.append((hut[0]+hut[1]+0.5,'hut',None))
    return sorted(L,key=lambda t:t[0])
# bóng + nón nhìn trước
def ellipse(i,j,rx,alpha=90):
    lay=Image.new('RGBA',canvas.size,(0,0,0,0)); x,y=scr(i,j); ImageDraw.Draw(lay).ellipse((x-rx,y-rx*0.5,x+rx,y+rx*0.5),fill=(20,24,14,alpha)); canvas.alpha_composite(lay)
def cone(i,j,face,angle=100,rng_=2.25,near=1.0):
    lay=Image.new('RGBA',canvas.size,(0,0,0,0)); d=ImageDraw.Draw(lay)
    for r,col in ((rng_,(222,96,48,70)),(near,(232,120,60,120))):
        pts=[scr(i,j)]
        for k in range(25):
            a=math.radians(-angle/2+angle*k/24); pts.append(scr(i+face*math.cos(a)*r, j+math.sin(a)*r*(-face)))
        d.polygon(pts,fill=col)
    canvas.alpha_composite(lay)
for id,i,j in team: ellipse(i,j,11)
ellipse(zomb[1],zomb[2],10); cone(zomb[1],zomb[2],-1)
for _,kind,data in ordered():
    if kind=='obj':
        i,j,im,k=data; x,y=scr(i,j)
        if k=='tall': canvas.alpha_composite(im,(int(x-32),int(y-48-64)))
        elif k=='big': canvas.alpha_composite(im,(int(x-96),int(y-48-64)))
        else: canvas.alpha_composite(im,(int(x-32),int(y-48)))
    elif kind=='char':
        id,i,j=data; im,(ax,ay)=sprite(id); x,y=scr(i,j); canvas.alpha_composite(im,(int(x-ax),int(y-ay)))
    elif kind=='hut':
        x,y=scr(*hut); canvas.alpha_composite(T(BLD,48),(int(x-32),int(y-48))); canvas.alpha_composite(T(BLD,5),(int(x-32),int(y-48-26)))
# ---- HUD
A=np.array(Image.open(SC+'world_clean.png').convert('RGB')).astype(int); B=np.array(Image.open(SC+'hud2_bridge.png').convert('RGBA')).astype(int)
diff=(np.abs(A-B[...,:3]).max(-1)>6); mask=np.zeros_like(diff); mask[:232,:]=True; mask[738:,:]=True; mask[200:372,1180:]=True
hud=np.dstack([B[...,:3].astype(np.uint8),np.where(diff&mask,255,0).astype(np.uint8)]); hud_im=Image.fromarray(hud,'RGBA').filter(ImageFilter.MaxFilter(3))
hud_im=Image.fromarray(np.dstack([B[...,:3].astype(np.uint8),np.array(hud_im)[...,3]]),'RGBA')
big=canvas.resize((1600,900),Image.NEAREST); clean=big.copy(); big.alpha_composite(hud_im)
big.save(f'iso_v2_{TAG}_hud.png'); clean.save(f'iso_v2_{TAG}_clean.png'); canvas.crop((150,90,650,370)).resize((1500,840),Image.NEAREST).save(f'iso_v2_{TAG}_closeup.png'); print('ok',TAG)
