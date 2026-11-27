import numpy as np
from PIL import Image, ImageFilter
from collections import deque
src = Image.open('img-000.png').convert('RGB')
a = np.asarray(src).astype(np.float32)/255
H,W = a.shape[:2]
y0=34; h=int(W/0.75); a=a[y0:y0+h]; H=a.shape[0]
r,g,b = a[...,0],a[...,1],a[...,2]
mx=a.max(2); mn=a.min(2); sat=(mx-mn)/(mx+1e-6); lum=a@np.array([.3,.59,.11])
white=(mn>0.86)&(mx-mn<0.08)
bg=np.zeros((H,W),bool); q=deque()
for x in range(W):
    q.append((0,x))
for y in range(H):
    q.append((y,0)); q.append((y,W-1))
while q:
    y,x=q.popleft()
    if bg[y,x] or not white[y,x]: continue
    bg[y,x]=True
    for dy,dx in((1,0),(-1,0),(0,1),(0,-1)):
        ny,nx=y+dy,x+dx
        if 0<=ny<H and 0<=nx<W and not bg[ny,nx] and white[ny,nx]: q.append((ny,nx))
subj=~bg
hair = subj & (lum<0.33) & (sat<0.6)
skin = subj & (r>g) & (g>b) & (sat>0.12) & (sat<0.55) & (lum>0.45)
tie = subj & (((r>0.55)&(g<0.6)&(b<0.35)&(sat>0.45)) | ((b>r+0.08)&(lum<0.45)))
shirt = subj & (mn>0.72) & ~skin
card = subj & ~hair & ~skin & ~tie & ~shirt
lab = np.zeros((H,W),np.uint8)  # 0 bg 1 hair 2 skin 3 shirt 4 card 5 tie
lab[card]=4; lab[shirt]=3; lab[skin]=2; lab[hair]=1; lab[tie]=5
np.save('lab.npy', lab); np.save('lum.npy', lum)
cols=np.array([(255,255,255),(30,20,30),(230,180,150),(220,220,230),(140,130,90),(220,130,40)],np.uint8)
Image.fromarray(cols[lab]).save('lab.png')
print(H,W)
