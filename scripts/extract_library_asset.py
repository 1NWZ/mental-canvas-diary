"""从授权素材整页中裁出单件；仅清除与裁片边界连通的背景。"""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageOps

def extract(source,box,background='keep',threshold=24):
 im=Image.open(source).convert('RGBA');w,h=im.size
 im=im.crop(tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(box)))
 if background!='keep':
  a=np.asarray(im);rgb=a[:,:,:3]
  bg=(rgb.max(2)<threshold) if background=='black' else (rgb.min(2)>255-threshold)
  # Pad with background so all four borders are seeded; interior whites/blacks remain intact.
  m=ImageOps.expand(Image.fromarray(np.uint8(bg)*255),border=1,fill=255)
  ImageDraw.floodfill(m,(0,0),128,thresh=0)
  exterior=np.asarray(m)[1:-1,1:-1]==128
  alpha=a[:,:,3].copy();alpha[exterior]=0;im.putalpha(Image.fromarray(alpha))
 bbox=im.getbbox()
 if bbox:im=im.crop(bbox)
 return im
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('output');p.add_argument('--box',nargs=4,type=float,required=True);p.add_argument('--background',choices=['keep','white','black'],default='keep');p.add_argument('--threshold',type=int,default=24);a=p.parse_args()
 if not (0<=a.box[0]<a.box[2]<=1 and 0<=a.box[1]<a.box[3]<=1):p.error('box 必须为 0–1 的左上右下坐标')
 Path(a.output).parent.mkdir(parents=True,exist_ok=True);extract(a.source,a.box,a.background,a.threshold).save(a.output)
