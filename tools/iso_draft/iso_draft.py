"""Bản nháp isometric 2:1 của màn 1 từ dữ liệu thật: nền + nước chiếu iso, vật thể billboard sắp theo độ sâu,
đội + Biến Thể + nón nhìn, khối tường đá và cabin gỗ để thấy chiều cao, phủ HUD v11 bóc từ ảnh chụp."""
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT='/home/user/LastGreenArea/'
SC='/tmp/claude-0/-home-user-LastGreenArea/e1e1a971-c3c2-54a5-94b5-045467fd14f4/scratchpad/'
L=json.load(open(ROOT+'public/data/levels/level1.json'))
atlas=json.load(open(ROOT+'public/data/atlas.json'))
pages={t['image']:Image.open(ROOT+'public/assets/'+t['image']).convert('RGBA') for t in atlas['textures']}
frames={f['filename']:(t['image'],f) for t in atlas['textures'] for f in t['frames']}
def sprite(id):
    img,f=frames[id]; r=f['frame']; a=f.get('anchor',{'x':0.5,'y':1.0})
    im=pages[img].crop((r['x'],r['y'],r['x']+r['w'],r['y']+r['h']))
    return im,(a['x']*r['w'],a['y']*r['h'])

# ---------- nền top-down (đất + nước khung 0) ----------
ground=Image.open(ROOT+'public/assets/maps/level1_ground.png').convert('RGBA')
water=Image.open(ROOT+'public/assets/maps/level1_water.png').convert('RGBA'); W=L['water']
ground.alpha_composite(water.crop((0,0,W['w'],W['h'])),(W['x'],W['y']))

# ---------- phép chiếu ----------
U0,V0=880,462          # tâm vùng thế giới
CX,CY=400,236          # tâm trên khung 800×450
def iso(u,v,z=0.0):
    return CX+(u-U0)-(v-V0), CY+((u-U0)+(v-V0))*0.5-z
def inv(sx,sy):
    du=(sx-CX)*0.5+(sy-CY); dv=(sy-CY)-(sx-CX)*0.5
    return U0+du, V0+dv

# nền: lấy mẫu song tuyến rồi lượng tử về bảng màu của chính vùng nền (giữ chất pixel Cainos)
G=np.array(ground).astype(np.float32); GH,GW=G.shape[:2]
ys,xs=np.mgrid[0:450,0:800].astype(np.float32)
u=U0+(xs-CX)*0.5+(ys-CY); v=V0+(ys-CY)-(xs-CX)*0.5
u=np.clip(u,0,GW-2); v=np.clip(v,0,GH-2)
x0=np.floor(u).astype(int); y0=np.floor(v).astype(int); fx=(u-x0)[...,None]; fy=(v-y0)[...,None]
samp=(G[y0,x0]*(1-fx)*(1-fy)+G[y0,x0+1]*fx*(1-fy)+G[y0+1,x0]*(1-fx)*fy+G[y0+1,x0+1]*fx*fy)
base=Image.fromarray(np.clip(samp,0,255).astype(np.uint8),'RGBA').convert('RGB')
pal=ground.crop((U0-300,V0-260,U0+300,V0+260)).convert('RGB').quantize(colors=96,method=Image.Quantize.MEDIANCUT)
base=base.quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA')
canvas=base

# ---------- khối iso (tường đá / cabin) ----------
def face_left(tex,length,h,shade=1.0):
    """mặt có pháp tuyến +v: u tăng → sx +1, sy +0.5. Trả (ảnh, dx, dy) đặt tại iso(u0,v1,0) góc trái dưới."""
    t=tex.resize((length,h),Image.NEAREST)
    out=Image.new('RGBA',(length,h+length//2+1),(0,0,0,0))
    out=t.transform(out.size,Image.AFFINE,(1,0,0,-0.5,1,0),Image.NEAREST)  # (x,y)→(x, y-0.5x)
    # cắt ngoài hình bình hành
    m=Image.new('L',out.size,0); d=ImageDraw.Draw(m); d.polygon([(0,h),(length,h+length*0.5),(length,length*0.5),(0,0)],fill=255)
    out.putalpha(m)
    if shade!=1: out=Image.fromarray((np.array(out)*np.array([shade,shade,shade,1])).astype(np.uint8))
    return out,(0,-h)
def face_right(tex,length,h,shade=0.78):
    """mặt có pháp tuyến +u: v tăng → sx -1, sy +0.5. Đặt góc phải dưới tại iso(u1,v0,0)... trả ảnh với gốc = iso(u1,v1,0) trái dưới."""
    t=tex.resize((length,h),Image.NEAREST)
    out=t.transform((length,h+length//2+1),Image.AFFINE,(-1,0,length,0.5,1,-0.5*length),Image.NEAREST)
    m=Image.new('L',out.size,0); d=ImageDraw.Draw(m); d.polygon([(0,h+length*0.5),(length,h),(length,0),(0,length*0.5)],fill=255)
    out.putalpha(m)
    out=Image.fromarray((np.array(out)*np.array([shade,shade,shade,1])).astype(np.uint8))
    return out,(0,-h-length*0.5)
def block(canvas,u0,v0,u1,v1,h,tex_l,tex_r,top=None,roof=None):
    """vẽ khối từ (u0,v0)-(u1,v1) cao h. top: màu nóc phẳng; roof: (cao mái, màu sáng, màu tối) mái dốc hai bên theo trục u."""
    # mặt trái (v=v1), mặt phải (u=u1)
    fl,(dx,dy)=face_left(tex_l,u1-u0,h); sx,sy=iso(u0,v1); canvas.alpha_composite(fl,(int(sx+dx),int(sy+dy)))
    fr,(dx,dy)=face_right(tex_r,v1-v0,h); sx,sy=iso(u1,v1); canvas.alpha_composite(fr,(int(sx+dx),int(sy+dy)))
    d=ImageDraw.Draw(canvas)
    if roof:
        rh,c1,c2=roof; vm=(v0+v1)/2
        far=[iso(u0,v0,h),iso(u1,v0,h),iso(u1,vm,h+rh),iso(u0,vm,h+rh)]
        near=[iso(u0,vm,h+rh),iso(u1,vm,h+rh),iso(u1,v1,h),iso(u0,v1,h)]
        d.polygon(far,fill=c2); d.polygon(near,fill=c1)
        # ván mái
        for k in range(1,6):
            t=k/6; d.line([iso(u0,vm+(v1-vm)*t,h+rh*(1-t)),iso(u1,vm+(v1-vm)*t,h+rh*(1-t))],fill=tuple(max(0,c-18) for c in c1),width=1)
        d.line([iso(u0,vm,h+rh),iso(u1,vm,h+rh)],fill=(60,48,34),width=2)
        # đầu hồi (tam giác) ở mặt phải u=u1
        d.polygon([iso(u1,v0,h),iso(u1,v1,h),iso(u1,vm,h+rh)],fill=tuple(int(c*0.78) for c in top))
    elif top:
        d.polygon([iso(u0,v0,h),iso(u1,v0,h),iso(u1,v1,h),iso(u0,v1,h)],fill=top)
    # viền cạnh
    for a,b in ((iso(u0,v1,0),iso(u0,v1,h)),(iso(u1,v1,0),iso(u1,v1,h)),(iso(u1,v0,0),iso(u1,v0,h))):
        d.line([a,b],fill=(40,36,30),width=1)

stone=Image.open(ROOT+'assets/tiles/cainos/wall.png').convert('RGBA').crop((32,208,160,256))
# ván gỗ: lấy từ mặt cầu trong nền
planks=ground.crop((L['bridge'][0]+8,L['bridge'][1]+8,L['bridge'][0]+72,L['bridge'][1]+40))
# bóng đổ khối
def shadow(canvas,u0,v0,u1,v1,h):
    sh=Image.new('RGBA',canvas.size,(0,0,0,0)); d=ImageDraw.Draw(sh)
    d.polygon([iso(u0,v1),iso(u1,v1),iso(u1+h*0.7,v1+h*0.7),iso(u0+h*0.7,v1+h*0.7)],fill=(20,24,14,70))
    d.polygon([iso(u1,v0),iso(u1,v1),iso(u1+h*0.7,v1+h*0.7),iso(u1+h*0.7,v0+h*0.7)],fill=(20,24,14,70))
    canvas.alpha_composite(sh)

# ---------- vật thể ----------
objs=[]
for o in L['objects']:
    objs.append((o['id'],o['x'],o['y']))
# dọn chỗ cho cabin và tường
CABIN=(900,296,1000,356); RUIN=(1000,560,1070,580)
def inside(x,y,r,m=24): return r[0]-m<=x<=r[2]+m and r[1]-m<=y<=r[3]+m
objs=[o for o in objs if not inside(o[1],o[2],CABIN,44) and not inside(o[1],o[2],RUIN)]
team=[('char/hung/di-xuong/0',690,452),('char/duong/di-xuong/0',728,448),('char/son/di-xuong/0',690,492),('char/ny/di-xuong/0',726,490)]
zomb=('enemy/ke-lang-thang/le-buoc-trai/0',846,452)
items=[('item/da-khac-ky-hieu',800,521),('item/da-nem',760,470)]

# bóng tròn dưới chân nhân vật
def foot_shadow(canvas,u,v,rx=12):
    sh=Image.new('RGBA',canvas.size,(0,0,0,0)); d=ImageDraw.Draw(sh); sx,sy=iso(u,v)
    d.ellipse((sx-rx,sy-rx*0.5,sx+rx,sy+rx*0.5),fill=(20,24,14,90)); canvas.alpha_composite(sh)

# nón nhìn (tọa độ thế giới → iso)
def cone(canvas,u,v,face,angle,rng,near):
    lay=Image.new('RGBA',canvas.size,(0,0,0,0)); d=ImageDraw.Draw(lay)
    for r,col in ((rng,(222,96,48,70)),(near,(232,120,60,120))):
        pts=[iso(u,v-12)]
        for k in range(25):
            a=math.radians(-angle/2+angle*k/24); pts.append(iso(u+face*math.cos(a)*r, v-12+math.sin(a)*r))
        d.polygon(pts,fill=col)
    canvas.alpha_composite(lay)

# thứ tự vẽ: khối + vật thể theo sy
draw_list=[]
for id,x,y in objs: draw_list.append((iso(x,y)[1],'spr',(id,x,y)))
for id,x,y in team: draw_list.append((iso(x,y)[1],'char',(id,x,y)))
draw_list.append((iso(zomb[1],zomb[2])[1],'char',zomb))
for id,x,y in items: draw_list.append((iso(x,y)[1]-6,'item',(id,x,y)))
draw_list.append((iso(CABIN[2],CABIN[3])[1],'cabin',None)); draw_list.append((iso(RUIN[2],RUIN[3])[1],'ruin',None))
draw_list.sort(key=lambda t:t[0])
# bóng và nón vẽ trước
shadow(canvas,*CABIN,52); shadow(canvas,*RUIN,34)
cone(canvas,zomb[1],zomb[2],-1,L['stealth']['vision']['angle'],L['stealth']['vision']['range'],L['stealth']['vision']['near'])
for _,kind,data in draw_list:
    if kind=='cabin':
        block(canvas,*CABIN,52,planks,planks,top=(92,70,46),roof=(22,(96,86,58),(70,62,42)))
        # cửa + cửa sổ trên mặt trái
        d=ImageDraw.Draw(canvas); dx,dy=iso(CABIN[0]+34,CABIN[3]); d.rectangle((dx-5,dy-26,dx+5,dy),fill=(52,38,24)); d.rectangle((dx-5,dy-26,dx+5,dy),outline=(36,28,18))
        wx,wy=iso(CABIN[0]+70,CABIN[3]); d.rectangle((wx-6,wy-36,wx+6,wy-26),fill=(150,170,165)); d.rectangle((wx-6,wy-36,wx+6,wy-26),outline=(40,32,22))
    elif kind=='ruin':
        block(canvas,*RUIN,34,stone,stone,top=(138,134,118))
    else:
        id,x,y=data; im,(ax,ay)=sprite(id)
        if kind=='char': foot_shadow(canvas,x,y,10 if 'enemy' in id else 11)
        if kind=='spr' and ('tree' in id or 'conifer' in id): foot_shadow(canvas,x,y,22)
        sx,sy=iso(x,y); canvas.alpha_composite(im,(int(sx-ax),int(sy-ay)))

# ---------- HUD bóc từ ảnh chụp v11 ----------
A=np.array(Image.open(SC+'world_clean.png').convert('RGB')).astype(int); B=np.array(Image.open(SC+'hud2_bridge.png').convert('RGBA')).astype(int)
diff=(np.abs(A-B[...,:3]).max(-1)>6)
mask=np.zeros_like(diff); mask[:232,:]=True; mask[738:,:]=True; mask[200:372,1180:]=True
hud=B.copy(); hud[...,3]=np.where(diff&mask,255,0)
hud_im=Image.fromarray(hud.astype(np.uint8),'RGBA').filter(ImageFilter.MaxFilter(3))
hud_im=Image.fromarray(np.where((np.array(hud_im)[...,3:4]>0),np.array(hud_im),np.array(hud_im)).astype(np.uint8),'RGBA')
hud_alpha=np.array(hud_im)[...,3]
hud_rgb=B[...,:3].astype(np.uint8); hud_final=np.dstack([hud_rgb,hud_alpha]); hud_im=Image.fromarray(hud_final,'RGBA')

big=canvas.resize((1600,900),Image.NEAREST); big.alpha_composite(hud_im)
big.save('iso_draft_hud.png'); canvas.resize((1600,900),Image.NEAREST).save('iso_draft_clean.png')
# cận cảnh 1:1 vùng cầu + cabin
canvas.crop((150,60,650,340)).resize((1500,840),Image.NEAREST).save('iso_closeup.png')
# so sánh cạnh nhau với top-down hiện tại
td=Image.open(SC+'hud2_bridge.png').convert('RGBA')
cmp=Image.new('RGBA',(1600,2*900+60),(36,34,28,255)); d=ImageDraw.Draw(cmp)
from PIL import ImageFont
f=ImageFont.truetype(ROOT+'assets/fonts/BeVietnamPro-SemiBold.ttf',24)
d.text((12,8),'Top-down 3/4 hiện tại',font=f,fill=(235,228,210)); cmp.paste(td,(0,40))
d.text((12,948),'Bản nháp isometric 2:1 (cùng vùng bản đồ, cùng sprite, HUD v11)',font=f,fill=(235,228,210)); cmp.paste(big,(0,980))
cmp.save('iso_vs_topdown.png'); print('ok')
