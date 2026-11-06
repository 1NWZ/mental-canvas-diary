#!/usr/bin/env python3
"""将 1–3 张素材组成立体剪贴页，输出可编辑场景、离线 HTML、PNG 与可选 MP4/GIF。"""
import argparse, base64, io, json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]

def font(size, path=None):
    candidates = [path] if path else []
    candidates += ['/System/Library/Fonts/PingFang.ttc', '/System/Library/Fonts/Hiragino Sans GB.ttc', '/System/Library/Fonts/STHeiti Medium.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/System/Library/Fonts/Supplemental/Georgia.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for p in candidates:
        if p and Path(p).exists(): return ImageFont.truetype(p, size)
    return ImageFont.load_default(size=size)

def shape_mask(size, shape):
    w,h=size; im=Image.new('L',size);d=ImageDraw.Draw(im)
    if shape=='heart':
        pts=[]
        for t in np.linspace(0,2*math.pi,250):
            x=16*math.sin(t)**3; y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
            pts.append((w*(.5+x/34),h*(.48-y/32)))
        d.polygon(pts,fill=255)
    elif shape=='star':
        d.polygon([(w/2+math.sin(i*math.pi/5)*w*(.48 if i%2==0 else .23),h/2-math.cos(i*math.pi/5)*h*(.48 if i%2==0 else .23)) for i in range(10)],fill=255)
    else: d.rectangle((1,1,w-2,h-2),fill=255)
    return im

def material(size,style,seed=1):
    w,h=size;rng=np.random.default_rng(seed)
    color=np.array([39,66,100] if style=='denim' else [227,217,189])
    noise=rng.normal(0,3,(h,w,1))
    rgb=np.clip(np.tile(color,(h,w,1))+noise,0,255).astype('uint8')
    im=Image.fromarray(rgb).convert('RGBA');d=ImageDraw.Draw(im)
    if style=='denim':
        for x in range(0,w,4):d.line((x,0,x-w,h), fill=(155,174,190,55),width=1)
        for x in range(35,w,95):
            d.rectangle((x,0,x+15,h),fill=(170,179,176,130));d.line((x+22,0,x+22,h),fill=(228,222,197,180),width=3)
        for y in range(35,h,95):
            d.rectangle((0,y,w,y+15),fill=(170,179,176,130));d.line((0,y+22,w,y+22),fill=(228,222,197,180),width=3)
    im.putalpha(255)
    return im

def save_texture(im,out,name):
    p=out/'textures'/f'{name}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p);return str(p.relative_to(out))

def make_scene(photos,out,style,title,font_path=None):
    out.mkdir(parents=True,exist_ok=True); layers=[]; paper='denim' if style=='denim' else 'paper'
    def layer(im,name,x,y,z,w,h,ry=0,rz=0):
        p=save_texture(im,out,name)
        layers.append(dict(id=name,image=p,back=p,x=x,y=y,z=z,w=w,h=h,ry=ry,rz=rz))
    # 三翼围绕同一中轴，每翼独立平面；贴片随所属页一起变换。
    for i in range(3):
        angle=[-35,85,205][i];a=math.radians(angle)
        def onpage(im,name,u,v,depth,w,h,rz=0):
            layer(im,name,math.cos(a)*u+math.sin(a)*depth,v,-math.sin(a)*u+math.cos(a)*depth,w,h,angle,rz)
            if depth>0:
                layers[-1]['side']='front'
                layer(im,name+'-reverse',math.cos(a)*u-math.sin(a)*depth,v,-math.sin(a)*u-math.cos(a)*depth,w,h,angle,rz)
                layers[-1]['side']='back'
        board=material((380,510),paper,10+i)
        if style=='birthday':board.putalpha(shape_mask(board.size,'heart'))
        else:
            d=ImageDraw.Draw(board)
            for y in range(12,500,14):
                for x in [10,370]: d.line((x,y,x,y+7), fill='#dfdabd',width=2)
            for x in range(12,370,14):
                for y in [10,500]:d.line((x,y,x+7,y),fill='#dfdabd',width=2)
        onpage(board,f'page-{i}',145,20,0,290,390)
        # 单张素材只在主面出现完整照片，其余两面使用同一来源的细节裁片。
        src=photos[i%len(photos)]
        photo=ImageOps.exif_transpose(Image.open(src)).convert('RGB')
        if len(photos)<3 and i>=len(photos):
            w,h=photo.size
            candidates=[photo.crop((x*w,y*h,(x+.6)*w,(y+.6)*h)) for y in [0,.2,.4] for x in [0,.2,.4]]
            # 优先选择有实际内容的细节，语义和人脸裁切仍需视觉复核。
            candidates.sort(key=lambda im:float(np.asarray(im.resize((48,48))).std(axis=(0,1)).mean()),reverse=True)
            photo=candidates[0 if i%2 else 2]
        photo=ImageOps.fit(photo,(300,340),centering=(.5,.42)).convert('RGBA')
        mask=shape_mask(photo.size,'heart' if style=='birthday' else 'rect');photo.putalpha(mask)
        frame=Image.new('RGBA',(320,360),'#a43b24' if style=='birthday' else '#eee9da')
        if style=='birthday':frame.putalpha(shape_mask(frame.size,'heart'))
        frame.alpha_composite(photo,(10,10))
        onpage(frame,f'photo-{i}',155,0,12,225,254,[-6,5,-3][i])
        tag=Image.new('RGBA',(360,74),(0,0,0,0));d=ImageDraw.Draw(tag)
        d.text((180,37),title if i==0 else ['','little moments','keep this day'][i],anchor='mm',fill='#233c57' if style=='denim' else '#751f32',font=font(30,font_path))
        onpage(tag,f'caption-{i}',145,-213,16,270,56,-3)
        sticker=material((150,150),'paper',20+i); sticker.paste('#789045' if style=='denim' else '#933346',(0,0,150,150));sticker.putalpha(shape_mask(sticker.size,'star' if style=='denim' else 'heart'))
        d=ImageDraw.Draw(sticker);d.text((75,70),'✦' if i%2 else '•',font=font(42,font_path),anchor='mm',fill='#e8dfb4')
        onpage(sticker,f'sticker-{i}',275,140,34,100,100,12)
        note=material((220,95),'paper',30+i);d=ImageDraw.Draw(note);d.text((110,47),['dear diary','a day to keep','with love'][i],anchor='mm',font=font(25,font_path),fill='#593839')
        onpage(note,f'note-{i}',115,156,24,165,71,-7)
    return dict(width=720,height=960,background='#ffffff',duration=8,fps=24,source_photos=[str(p.resolve()) for p in photos],style=style,camera=dict(distance=1250,focal=1250,yaw_start=-20,yaw_degrees=360,pitch=6,zoom=.93),layers=layers)

def project(layer,scene,t):
    c=scene['camera'];phase=2*math.pi*t/scene['duration']
    yaw=math.radians(c.get('yaw_start',0)+c.get('yaw_degrees',360)*(.5*math.sin(phase) if c.get('motion')=='swing' else (phase-.22*math.sin(2*phase))/(2*math.pi)))
    pitch=math.radians(c.get('pitch',6)+0*math.sin(phase))
    a=math.radians(layer.get('ry',0)); r=math.radians(layer.get('rz',0))
    points=np.array([[-.5,-.5,0],[.5,-.5,0],[.5,.5,0],[-.5,.5,0]])*np.array([layer['w'],layer['h'],1])
    rz=np.array([[math.cos(r),-math.sin(r),0],[math.sin(r),math.cos(r),0],[0,0,1]])
    ry=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
    cy=np.array([[math.cos(yaw),0,math.sin(yaw)],[0,1,0],[-math.sin(yaw),0,math.cos(yaw)]])
    cx=np.array([[1,0,0],[0,math.cos(pitch),-math.sin(pitch)],[0,math.sin(pitch),math.cos(pitch)]])
    camera=cx@cy
    world=points@rz.T@ry.T+np.array([layer['x'],layer['y'],layer['z']])
    view=world@camera.T;den=c['distance']-view[:,2]
    if min(den)<40:raise ValueError('图层越过相机近裁面，请增加 distance 或缩小图层。')
    zoom=c.get('zoom',1)
    xy=view[:,:2]*(c['focal']*zoom/den[:,None])+[scene['width']/2,scene['height']/2]
    back=(camera@ry@np.array([0,0,1]))[2]<0
    return xy,float(view[:,2].mean()),back

def render(scene,base,t,size=None,cache=None):
    from depth_render import render as depth_render
    return depth_render(scene,base,t,size=size,cache=cache)


def html(scene,base):
    payload=json.loads(json.dumps(scene))
    for l in payload['layers']:
        for key in ['image','back']:
            if key in l:l[key]='data:image/png;base64,'+base64.b64encode((base/l[key]).read_bytes()).decode()
    template=(ROOT/'assets/player.html').read_text()
    (base/'diary.html').write_text(template.replace('__SCENE__',json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')

def validate(scene,base):
    if not 1<=len(scene.get('source_photos',[]))<=3:raise ValueError('原始照片必须为 1–3 张；衍生裁片不另计。')
    if not 1<=scene['duration']<=60 or not 1<=scene['fps']<=60:raise ValueError('时长应为 1–60 秒，帧率应为 1–60。')
    if any(not isinstance(scene[k],int) or scene[k]<2 or scene[k]%2 for k in ['width','height']):raise ValueError('画幅宽高必须为不小于 2 的偶数。')
    if not scene['layers']:raise ValueError('场景没有图层。')
    for l in scene['layers']:
        if l['w']<=0 or l['h']<=0:raise ValueError('图层尺寸必须为正。')
        for k in ['image','back']:
            if k in l and not (base/l[k]).is_file():raise ValueError(f'图层文件不存在：{l[k]}')
    for t in np.linspace(0,scene['duration'],24):
        for l in scene['layers']:project(l,scene,t)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--photos',nargs='+',type=Path);p.add_argument('--scene',type=Path)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--style',choices=['birthday','denim'],default='denim')
    p.add_argument('--title',default='little joy');p.add_argument('--font');p.add_argument('--duration',type=float);p.add_argument('--fps',type=int)
    p.add_argument('--video',action='store_true');p.add_argument('--gif',action='store_true')
    args=p.parse_args()
    if bool(args.scene)==bool(args.photos):p.error('请仅提供 --photos 或 --scene。')
    if args.photos and not 1<=len(args.photos)<=3:p.error('只接受 1–3 张原始照片。')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    if args.scene:
        scene=json.loads(args.scene.read_text());base=args.scene.resolve().parent
        # 将场景资产复制到新输出目录，使交付可以独立使用。
        for i,l in enumerate(scene['layers']):
            for k in ['image','back']:
                if k in l:l[k]=save_texture(Image.open(base/l[k]).convert('RGBA'),out,f'layer-{i}-{k}')
    else:scene=make_scene(args.photos,out,args.style,args.title,args.font)
    if args.duration is not None:scene['duration']=args.duration
    if args.fps is not None:scene['fps']=args.fps
    validate(scene,out);(out/'scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2),encoding='utf-8');html(scene,out)
    cache={};render(scene,out,0,cache=cache).save(out/'cover.png')
    sheet=Image.new('RGB',(960,640),'#eeeeee')
    for i in range(8):
        shot=render(scene,out,i*scene['duration']/8,size=(240,300),cache=cache);sheet.paste(shot,((i%4)*240+(240-shot.width)//2,(i//4)*320))
    sheet.save(out/'contact-sheet.jpg')
    if args.video:
        try:import av
        except ImportError:raise SystemExit('MP4 导出需要 PyAV：python -m pip install av；HTML 和封面已生成。')
        with av.open(str(out/'diary.mp4'),'w') as container:
            stream=container.add_stream('libx264',rate=scene['fps']);stream.width=scene['width'];stream.height=scene['height'];stream.pix_fmt='yuv420p';stream.options={'crf':'19'}
            for i in range(round(scene['duration']*scene['fps'])):
                frame=av.VideoFrame.from_image(render(scene,out,i/scene['fps'],cache=cache))
                for packet in stream.encode(frame):container.mux(packet)
            for packet in stream.encode():container.mux(packet)
    if args.gif:
        frames=[render(scene,out,i/12,size=(360,480),cache=cache) for i in range(round(scene['duration']*12))]
        frames[0].save(out/'diary.gif',save_all=True,append_images=frames[1:],duration=83,loop=0,optimize=False)
    print(f'已生成：{out}')
if __name__=='__main__':main()
