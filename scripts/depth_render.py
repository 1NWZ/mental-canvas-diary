import numpy as np,math
from PIL import Image,ImageOps
import diary as D

def depths(l,s,t):
 c=s['camera'];phase=2*math.pi*t/s['duration'];yaw=math.radians(c.get('yaw_start',0)+c.get('yaw_degrees',360)*(.5*math.sin(phase) if c.get('motion')=='swing' else (phase-.22*math.sin(2*phase))/(2*math.pi)));p=math.radians(c.get('pitch',6)+0*math.sin(phase));a=math.radians(l.get('ry',0));r=math.radians(l.get('rz',0))
 v=[]
 for u,y in [(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]:
  x=u*l['w'];y*=l['h'];xx=x*math.cos(r)-y*math.sin(r);yy=x*math.sin(r)+y*math.cos(r)
  x=xx*math.cos(a)+l['x'];y=yy+l['y'];z=-xx*math.sin(a)+l['z']
  zz=-math.sin(yaw)*x+math.cos(yaw)*z;v.append(math.sin(p)*y+math.cos(p)*zz)
 return v

def render(s,base,t,size=None,cache=None):
 w,h=s['width'],s['height'];canvas=np.array(Image.new('RGB',(w,h),s.get('background','#ffffff')));zb=np.full((h,w),-np.inf,dtype=np.float32);cache={} if cache is None else cache
 for l in s['layers']:
  q,_,back=D.project(l,s,t)
  if (l.get('side')=='front' and back) or (l.get('side')=='back' and not back):continue
  key=str(base/l.get('back',l['image']) if back else base/l['image'])
  if key not in cache:cache[key]=Image.open(key).convert('RGBA')
  tex=cache[key];tw,th=tex.size
  if back:tex=ImageOps.mirror(tex)
  x0=max(0,int(np.floor(q[:,0].min())));x1=min(w,int(np.ceil(q[:,0].max())));y0=max(0,int(np.floor(q[:,1].min())));y1=min(h,int(np.ceil(q[:,1].max())))
  if x1<=x0 or y1<=y0:continue
  dst=q-[x0,y0];A=[];B=[]
  for (x,y),(u,v) in zip(dst,[(0,0),(tw,0),(tw,th),(0,th)]):
   A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
  try:coef=np.linalg.solve(A,B)
  except np.linalg.LinAlgError:continue
  arr=np.asarray(tex.transform((x1-x0,y1-y0),Image.Transform.PERSPECTIVE,coef,Image.Resampling.BICUBIC))
  yy,xx=np.mgrid[:y1-y0,:x1-x0];xx=xx+.5;yy=yy+.5;de=coef[6]*xx+coef[7]*yy+1
  u=(coef[0]*xx+coef[1]*yy+coef[2])/de/tw;v=(coef[3]*xx+coef[4]*yy+coef[5])/de/th
  z=depths(l,s,t);zz=z[0]+(z[1]-z[0])*u+(z[3]-z[0])*v
  zview=zb[y0:y1,x0:x1];valid=(arr[:,:,3]>20)&(zz>zview)
  canvas[y0:y1,x0:x1][valid]=arr[:,:,:3][valid];zview[valid]=zz[valid]
 im=Image.fromarray(canvas)
 if size:im.thumbnail(size,Image.Resampling.LANCZOS)
 return im
