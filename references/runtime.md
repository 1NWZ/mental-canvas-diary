# 运行、场景编辑与局限

## 环境与命令

Python 3.10+，依赖见 `scripts/requirements.txt`。Pillow、numpy 用于投影与渲染；PyAV 用于 MP4 编码。先检查现有环境，缺失时再安装，不固定用户机器路径。离线 HTML 无 CDN 依赖。

```bash
python -m pip install -r /完整路径/mental-canvas-diary/scripts/requirements.txt
python /完整路径/mental-canvas-diary/scripts/diary.py \
  --photos /路径/照片1.jpg /路径/照片2.jpg \
  --style birthday --title "把今天收藏" --out /输出路径/我的手帐 --video
```

`--style birthday` 是心形贺卡，`denim` 是牛仔布贴。`--gif` 额外生成小尺寸动图。`--duration 8 --fps 24` 控制时长和帧率。中文字体可用 `--font /路径/中文字体.ttf` 指定。默认尝试系统字体，输出后必须检查文字。默认视频无音频。

脚本不自动调用图像模型；代理先生成／整理 PNG，再将 PNG 路径写进场景。透明图层保留 alpha。自动预设只作技术起步，交付前按 effect-library.md 改造风格；三翼结构中，每页基于一张来源照片或同源细节，必须人工视觉复核人脸裁切。

## 编辑场景后重新输出

```bash
python /完整路径/mental-canvas-diary/scripts/diary.py \
  --scene /输出路径/我的手帐/scene.json \
  --out /输出路径/我的手帐-调整 --video
```

建议调整输出另存目录，便于比较。JSON 路径以场景所在目录为基准；导出时复制纹理到新目录，HTML 把图片内嵌，因此单独移动 HTML 也能看。需要继续编辑时保留整个目录。

顶层字段：`width`/`height` 为画面像素（MP4 用偶数），`background` 为底色，`duration` 秒、`fps`、`source_photos` 为 1–3 个原始来源，`style` 为风格标记。只修改画幅而不修改镜头可能裁边，必须重新抽帧。

`camera`：`distance` 镜头距离，`focal` 透视焦距，`yaw_start` 起始偏航角，`yaw_degrees` 一个周期的偏航跨度，`pitch` 基础俯仰角，`zoom` 全局缩放。默认完整 360° 周期；若改成往复镜头，要同时修改 Python `project()` 和 HTML `geometry()` 中时间函数。不要只改一个渲染器。

每个 `layers` 元素：

```json
{"id":"front-photo","image":"textures/photo.png","back":"textures/back.png","x":120,"y":0,"z":20,"w":220,"h":280,"ry":-30,"rz":-4}
```

`x,y,z` 为中心坐标；x 向右、y 向下、z 朝镜头。`w,h` 为场景单位。`ry` 绕竖轴角度、`rz` 为纸片平面内角度；先 rz 后 ry。`back` 为背面正读素材，渲染器负责翻转 UV，不要预先镜像文字。没有 back 时复用正面。`side` 可为 `front`、`back` 或省略（双面可见）。预设把附属贴片分别放在底页正反两侧，并用 side 避免悬空文字重影。默认预设两面复用图片，定制可换成独立背面文案／细节，提高内容差异。

页面与附属贴片须保持相同 `ry`，局部坐标 `(u,v,d)` 转换为世界坐标：`x=page.x+cos(ry)*u+sin(ry)*d; y=page.y+v; z=page.z-sin(ry)*u+cos(ry)*d`。d 是从纸页表面抬起的距离。不要只给照片增加世界 z，否则旋转后可能离开所属页。

## 质量与性能

Python 使用单应矩阵和逐像素深度判断，HTML 使用 WebGL 透视和深度缓冲。二者镜头／位置一致，抗锯齿略有差别；半透明边缘采用透明度阈值，复杂半透明材质可能需专门混合排序。depth_render.py 为深度渲染模块，collage_assets.py 为异形素材辅助函数。这个脚本不是通用三维建模系统。

默认 720×960、24 fps，用于首轮效果检验；最终需要高清时改为 1080×1440，并同比例放大 camera.focal（1.5 倍），再复核。层数和像素数决定编码耗时。先用分镜定位构图问题，再编码长视频；脚本目前即使只生成封面也会输出 HTML 与分镜。

验证 MP4 可用 PyAV 解码并核对实际帧数、时长、尺寸；抽 0、1/4、1/2、3/4 周期看不同面。检查 `render(scene, t=0)` 与 `t=duration` 的像素一致性，并比较最后一个实际帧到首帧是否平顺。

异形页的连接、正反面装饰与循环检查见 [异形轴心规则](irregular-axis.md)。

当前验收要求 3–4 页、人物真实抠图与标题约 1:3，见 irregular-axis.md。现有命令预设固定三页、照片框与标题初值仅为技术起步；第四页需独立增加，人物透明素材、逐页荧光与装饰必须另行制作，不能直接输出预设作为完成版。
