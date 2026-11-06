#!/usr/bin/env python3
"""一次启动豆包分析→Seedream独立素材制作。由skill代理调用，不要求用户手工传递提示词。"""
import argparse,json,subprocess,sys,socket,datetime,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--brief',type=Path,required=True)
    ap.add_argument('--image-instruction',type=Path,required=True,help='限定本次独立素材编辑目标，防止生成整套海报')
    ap.add_argument('--photo',type=Path,action='append',required=True)
    ap.add_argument('--reference',type=Path,action='append',default=[])
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    for p in [a.brief,a.image_instruction,*a.photo,*a.reference]:
        if not p.is_file():ap.error('缺少输入文件：'+str(p))
    if a.out.exists():ap.error('输出目录已存在，使用新目录避免重复调用')
    # Detect transport availability before uploading images or making billable requests.
    try:socket.getaddrinfo('ark.cn-beijing.volces.com',443)
    except OSError:
        print('BLOCKED_NETWORK：当前运行环境无法解析方舟域名；未调用模型。需要可访问方舟的运行环境，修改提示词或API密钥不能解决此问题。',file=sys.stderr)
        return 2
    a.out.mkdir(parents=True);inputs=a.out/'inputs';inputs.mkdir()
    copies=[]
    for i,p in enumerate([*a.photo,*a.reference]):
        dest=inputs/(str(i)+p.suffix);shutil.copy2(p,dest);copies.append(dest)
    client=ROOT/'scripts/call_models.py'
    call=[sys.executable,str(client),'plan','--input',str(a.brief),'--out',str(a.out/'plan.txt')]
    for p in copies:call+=['--reference',str(p)]
    subprocess.run(call,check=True)
    # Carry the actual model result into image editing while keeping the requested asset scope.
    prompt=a.image_instruction.read_text()+'\n\n以下为豆包基于本轮原图与图库返回的设计上下文，只完成上文限定的独立素材，不扩展成整张海报：\n'+(a.out/'plan.txt').read_text()
    (a.out/'image-prompt.txt').write_text(prompt)
    call=[sys.executable,str(client),'image','--input',str(a.out/'image-prompt.txt'),'--out',str(a.out/'asset.png')]
    # First supplied photo is the edit target; additional photos inform planning only.
    for p in [copies[0],*copies[len(a.photo):]]:call+=['--reference',str(p)]
    subprocess.run(call,check=True)
    (a.out/'status.json').write_text(json.dumps({'status':'model_assets_ready','visual_review':'pending','final_animation':'pending'},ensure_ascii=False))
    print('双模型素材已返回。代理继续检查人物和透明边、合成差异化页面、渲染并验收；尚不能称为最终成片。')
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except subprocess.CalledProcessError as e:sys.exit(e.returncode)
