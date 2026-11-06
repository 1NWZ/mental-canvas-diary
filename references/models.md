# 在线模型制作流程

配置唯一来源 [models.json](models.json)，调用入口 `scripts/call_models.py`（Python3标准库）。

- 豆包2.0-lite：`ep-20260914174304-5d8v2`，分析输入图和参考库，输出逐页设计与独立素材提示词。
- Seedream5.0Pro：`ep-20260914155654-cjmcd`，读取豆包方案及原图／参考，生成或编辑实际参与合成的独立素材。
- 代码负责透明边清理、素材合成、三维轴心旋转和视频编码。模型不会直接产出最终旋转视频。

用户当前明确要求双模型参与测试。执行 plan → 检查方案 → image → 检查模型素材 → 将合格素材用于场景 → 渲染；不得静默改成纯代码版本。若某一步调用失败，报告实际阻塞，并保留失败记录，不将干运行、历史图片或离线合成记为模型成功。模型返回人物后检查身份、衣物与轮廓，模型改脸也不能交付。

```bash
python3 scripts/call_models.py plan --input brief.txt --out run/plan.txt --reference person.png --reference assets/current-library/01-type.jpg
python3 scripts/call_models.py image --input reviewed-image-prompt.txt --out run/subject.png --reference person.png --reference assets/current-library/01-type.jpg
```

image 的提示词需要实际承接豆包输出，限定独立素材与当前编辑要求；不要把整个三维场景交给静态生图。当前不使用动态闪光，静态水钻保留。透明图若不可靠可输出纯色背景后清理，但必须检查边缘，无黑底污染。

凭据按角色读取 `ARK_TEXT_API_KEY` / `ARK_IMAGE_API_KEY`，其次 `ARK_API_KEY`，最后本机 `~/Documents/Codex/.credentials/ark-text-api-key.txt` 与 `ark-image-api-key.txt`。密钥不进入skill、日志、请求样例或成片包。输出旁保存 `.call.json`，包含endpoint、状态、耗时、参考路径与服务返回的用量；不保存授权头。错误不自动重试，避免超时后重复计费。`--dry-run` 只构造请求，不能算在线成功。

已加入客户端并构造实际请求，但本会话网络无法解析方舟域名，两endpoint均尚未返回成功。只有拿到真实返回并用于成片后，才能声称已验证模型效果。暂无GitHub同步。

## 直接执行入口

代理默认使用 `scripts/run_models.py` 串联豆包与Seedream，接收本次brief、独立素材编辑指令、照片和参考图；不依赖work目录中的历史测试脚本，不要求用户手工复制豆包输出。第一张 --photo 是编辑主体，其余照片用于规划；参考图按需附带。

```bash
python3 scripts/run_models.py --brief run/brief.txt --image-instruction run/edit.txt --photo run/person.png --reference assets/current-library/01-type.jpg --out run/model-result
```

入口成功只表示模型素材就绪，代理仍须检查并接入三维合成与成片验收。网络预检失败返回BLOCKED_NETWORK，明确需要可访问方舟的运行环境；不能通过改DNS为固定IP、关闭TLS校验、启动非授权代理或操作被禁止的终端UI绕开运行限制。不要反复把终端操作转交用户作为默认工作流。
