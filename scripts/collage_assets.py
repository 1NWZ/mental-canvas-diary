from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
import numpy as np, math
from pathlib import Path
import diary as D
cream='#f0e9d9';red='#bb1635';lime='#e9fa32';ink='#30382e';pink='#dca4c0'

def mask(size,kind='torn',seed=1):
 w,h=size;im=Image.new('L',size);d=ImageDraw.Draw(im);rng=np.random.default_rng(seed)
 if kind in ['heart','star']:return D.shape_mask(size,kind)
 if kind=='oval':d.ellipse((8,8,w-8,h-8),fill=255)
 else:
  pts=[]
  # A slanted, genuinely irregular deckled paper edge, without a rectangular card silhouette.
  for x in np.linspace(.08,.94,28):pts.append((w*x,h*(.08+.02*math.sin(x*18)+rng.uniform(-.012,.012))))
  for y in np.linspace(.10,.86,24):pts.append((w*(.94+.025*math.sin(y*23)+rng.uniform(-.013,.013)),h*y))
  for x in np.linspace(.93,.09,28):pts.append((w*x,h*(.89+.04*math.sin(x*13)+rng.uniform(-.012,.012))))
  for y in np.linspace(.87,.09,24):pts.append((w*(.07+.03*math.sin(y*17)+rng.uniform(-.014,.014)),h*y))
  d.polygon(pts,fill=255)
 return im

def paper(size,col=cream,kind='torn',seed=1):
 w,h=size;c=np.array(Image.new('RGB',(1,1),col))[0,0];rng=np.random.default_rng(seed);rgb=np.uint8(np.clip(c+ rng.normal(0,1.9,(h,w,1)),0,255));im=Image.fromarray(rgb).convert('RGBA');im.putalpha(mask(size,kind,seed));return im

def crop(photo,box,size):
 w,h=photo.size;return ImageOps.fit(photo.crop(tuple(int(v*(w if j%2==0 else h)) for j,v in enumerate(box))),size,method=Image.Resampling.LANCZOS)

def outlined(im,color='white',stroke=15):
 # Broad paper-cut outline retains every original photographic pixel.
 im=im.convert('RGBA');im=ImageOps.expand(im,border=stroke+4,fill=(0,0,0,0));a=im.getchannel('A');rim=a.filter(ImageFilter.MaxFilter(2*stroke+1));bg=Image.new('RGBA',im.size,color);bg.putalpha(rim);bg.alpha_composite(im);return bg

def cutphoto(photo,box,size,kind='torn',color=cream,stroke=13):
 im=crop(photo,box,size);im.putalpha(mask(size,kind));return outlined(im,color,stroke)

def words(s,w=500,h=120,color=ink,bg=None,hand=True):
 im=Image.new('RGBA',(w,h),bg or (0,0,0,0));d=ImageDraw.Draw(im)
 path=Path('/System/Library/Fonts/Supplemental/SignPainter.ttc' if hand else '/System/Library/Fonts/Noteworthy.ttc')
 f=ImageFont.truetype(str(path),int(h*.66)) if path.exists() else D.font(int(h*.66))
 d.text((w/2,h/2),s,font=f,anchor='mm',fill=color);return im

def doodle(kind,col=red):
 im=Image.new('RGBA',(300,300));d=ImageDraw.Draw(im)
 if kind=='spark':
  for cx,cy,sz in [(145,145,100),(245,70,28),(65,240,25)]:
   pts=[(cx,cy-sz),(cx+sz*.13,cy-sz*.14),(cx+sz*.65,cy),(cx+sz*.12,cy+sz*.12),(cx,cy+sz),(cx-sz*.13,cy+sz*.13),(cx-sz*.65,cy),(cx-sz*.13,cy-sz*.13),(cx,cy-sz)]
   d.line(pts,fill=col,width=4,joint='curve')
 elif kind=='heart':
  pts=[]
  for t in np.linspace(0,2*math.pi,200):pts.append((150+7*16*math.sin(t)**3,155-7*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))))
  d.line(pts,fill=col,width=5,joint='curve');d.line([(60,250),(200,228)],fill=col,width=4)
 else:
  pts=[(30+i*1.1,150+45*math.sin(i*.032)) for i in range(220)];d.line(pts,fill=col,width=4);d.line([(232,125),(270,150),(242,168)],fill=col,width=4)
 return im

def gingham():
 im=paper((550,760),'#f7eedd',seed=5);o=Image.new('RGBA',im.size);d=ImageDraw.Draw(o)
 for x in range(0,550,65):d.rectangle((x,0,x+32,760),fill=(180,24,47,190))
 for y in range(0,760,65):d.rectangle((0,y,550,y+32),fill=(180,24,47,190))
 o=Image.alpha_composite(im,o);o.putalpha(im.getchannel('A'));return o
