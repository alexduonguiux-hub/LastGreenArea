"""Tải nội dung thật của các file con trỏ Git LFS trong clone thưa qua media.githubusercontent.com (proxy chỉ mở GitHub)."""
import os, subprocess, sys, concurrent.futures as cf
roots=sys.argv[1:]
jobs=[]
for root in roots:
    if not os.path.isdir(root+'/.git'): continue
    url=subprocess.run(['git','-C',root,'remote','get-url','origin'],capture_output=True,text=True).stdout.strip()
    br=subprocess.run(['git','-C',root,'rev-parse','--abbrev-ref','HEAD'],capture_output=True,text=True).stdout.strip()
    repo=url.replace('https://github.com/','').removesuffix('.git')
    for dp,_,fs in os.walk(root):
        if '.git' in dp: continue
        for f in fs:
            p=os.path.join(dp,f)
            if os.path.getsize(p)>300: continue
            try: head=open(p,'rb').read(40)
            except: continue
            if head.startswith(b'version https://git-lfs'):
                rel=os.path.relpath(p,root)
                size=int([l for l in open(p) if l.startswith('size ')][0].split()[1])
                jobs.append((p,f'https://media.githubusercontent.com/media/{repo}/{br}/{rel}',size))
print(len(jobs),'lfs files')
def fetch(j):
    p,u,size=j
    from urllib.parse import quote
    u='/'.join(quote(s) if i>2 else s for i,s in enumerate(u.split('/')))
    r=subprocess.run(['curl','-sS','-L','--max-time','120','-o',p+'.tmp','-w','%{http_code}',u],capture_output=True,text=True)
    ok=r.stdout=='200' and os.path.getsize(p+'.tmp')==size
    if ok: os.replace(p+'.tmp',p)
    else:
        if os.path.exists(p+'.tmp'): os.remove(p+'.tmp')
    return ok,p,r.stdout
ok=0; bad=[]
with cf.ThreadPoolExecutor(4) as ex:
    for res in ex.map(fetch,jobs):
        if res[0]: ok+=1
        else: bad.append(res)
print('ok',ok,'bad',len(bad)); print('\n'.join(f'{b[2]} {b[1]}' for b in bad[:10]))
