# Mental Canvas Diary · 异形轴心动态手帐

将照片制作成围绕中央竖轴旋转的 3–4 页动态拼贴手帐。包含技能指令、素材库、Python 渲染脚本与离线 HTML 播放器。

## 使用

将整个仓库目录作为 `mental-canvas-diary` 技能目录导入支持 `SKILL.md` 的代理工具，然后提供照片并请求使用该技能。入口：[SKILL.md](SKILL.md)。

## 本地渲染

需要 Python 3.10+。

```bash
python -m pip install -r scripts/requirements.txt
python scripts/diary.py --photos photo1.jpg photo2.jpg --style birthday --title "把今天收藏" --out outputs/diary --video
```

详细参数与场景结构见 [运行说明](references/runtime.md)。预设仅作技术起步；人物抠图、页面差异、第四页与视觉验收仍需按技能指令完成。

## 模型配置

模型调用说明见 [models.md](references/models.md)。请把 `references/models.json` 中的 endpoint 替换为自己账号可用的推理接入点，并在本机设置 `ARK_TEXT_API_KEY`、`ARK_IMAGE_API_KEY` 或 `ARK_API_KEY`。不要提交密钥或用户照片。仅本地渲染不需要模型密钥。

## 文件结构

- `SKILL.md`：技能入口与制作规范。
- `agents/`：代理界面配置。
- `scripts/`：渲染、素材与模型调用脚本。
- `references/`：排版、效果、模型和运行说明。
- `assets/`：纸张、贴纸、水钻、字形与网页播放器。

## 输出与限制

可交付 MP4、封面、可拖动的离线 HTML、场景 JSON 与图层。模拟 Mental Canvas 视觉效果，不生成其原生工程；MP4 不是 Live Photo。

本仓库基于用户提供的 20260916 完整技能包发布。发布时未执行付费模型调用或成片渲染测试。

## 许可

代码与原创文档采用 [MIT License](LICENSE)。素材、参考截图及第三方内容的权利归各自权利人；MIT 许可不授予第三方内容的额外权利。
