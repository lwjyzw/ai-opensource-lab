# AI 开源项目二次开发实验场

记录两个高星开源项目（Open WebUI / n8n）的二次开发起步成果：插件模板、源码导读、
Windows 免 Docker 部署实录。所有方案均针对国内网络环境与 D 盘部署约束实测通过。

## 目录结构

```
├── open-webui-pipes/          # Open WebUI 插件模板（零侵入二开）
│   ├── custom_model_pipe.py   # Pipe：接入任意 OpenAI 兼容 API（DeepSeek/Kimi/通义/vLLM/Ollama）
│   ├── audit_filter.py        # Filter：inlet 输入拦截 + outlet 审计日志
│   ├── ARCHITECTURE.md        # 带行号的源码导读（消息主流程 + 插件挂载点速查）
│   └── README.md              # 导入步骤 + 各家 API 端点速查
└── n8n-deploy/                # n8n Windows 原生部署（免 Docker）
    ├── README.md              # 完整部署实录：踩坑与解法
    ├── start-n8n.bat          # Windows 双击启动脚本
    └── start-n8n.sh           # Git Bash 启动脚本
```

## 优化说明

### 1. Open WebUI Pipe 模板（对比官方最小示例的改进）

- **Manifold 多模型暴露**：一个插件通过 Valves 里的 `model_ids` 配置生成多个独立模型项，
  改 API 地址即可切换服务商，不用改代码
- **UserValves 每用户参数**：temperature / max_tokens 由每个用户独立设置，不互相干扰
- **`__event_emitter__` 状态提示**：调用前后在聊天界面显示状态条，用户体验完整
- **错误可见化**：API 报错直接以文本流显示在对话里，而不是静默失败（调试时不用翻日志）
- **未配置保护**：没填 API Key 时在模型列表里显示提示项而非空白

### 2. Open WebUI Filter 模板

- `inlet` 超长输入与黑名单关键词拦截（抛异常即拒绝请求）
- `file_handler = True` 跳过文件处理（基于源码 `utils/filter.py:184` 实际行为）
- `outlet` 审计钩子：响应完成后统计并输出审计日志
- 全部钩子签名经 AST 验证，与框架 `inspect.signature` 反射注入机制匹配

### 3. 源码导读（ARCHITECTURE.md）

- 一条消息从 `POST /api/chat/completions` 到流式响应的完整生命周期图（含行号）
- `middleware.py`（6400 行）只读 4 个关键函数的精读清单
- 六类插件（Pipe / Filter×3 / Tool / Action）调用位置速查表
- 可注入参数完整清单及源码出处

### 4. n8n Windows 免 Docker 部署方案（核心优化）

| 问题 | 解法 |
|---|---|
| Docker Desktop 已卸载，且虚拟磁盘/镜像占空间 | 完全原生运行，零容器 |
| 本机无 Node.js，安装器默认写 C 盘 | 官方免安装 zip 解压到 `D:\tools\node`，无需管理员权限 |
| sqlite3 原生模块预编译包托管在 GitHub，下载被重置后回退本地编译，又缺 MSVC | `npm install --ignore-scripts` 跳过编译 + 从 npmmirror 手动补 `napi-v6-win32-x64` 二进制 |
| n8n 默认数据目录在 `~/.n8n`（C 盘） | `N8N_USER_FOLDER` 指向 `D:\projects\Zcode_project\n8n-data` |
| 每次启动要手敲环境变量 | 提供 `.bat` / `.sh` 一键启动脚本 |

> ⚠️ 升级注意：执行 `npm update -g n8n` 后，`build/Release/node_sqlite3.node` 会被清掉，
> 需按 n8n-deploy/README.md 里的三步重新放置。

### 5. 国内网络环境适配经验

- GitHub clone 走 `gh-proxy.com` 镜像；npm 走 `registry.npmmirror.com`（含二进制镜像）
- HuggingFace 镜像（`HF_ENDPOINT=https://hf-mirror.com`）对元数据有效，但容器内 xet
  传输后端仍会直连 `huggingface.co` 导致卡死——**结论：依赖 HF 大模型下载的项目
  优先选原生部署 + 预下载到缓存目录，而不是容器内下载**

## 快速复现

**n8n**：双击 `n8n-deploy/start-n8n.bat`（或 Git Bash 里跑 `start-n8n.sh`），
浏览器打开 http://localhost:5678

**Open WebUI 插件**：按 `open-webui-pipes/README.md` 的 7 步导入（需 Open WebUI 已运行，
Python 3.11 或 Docker 环境）

## License 提示

- n8n：Sustainable Use License（fair-code）——个人学习/内部使用自由，**不可将二开版对外分发为产品**
- Open WebUI：自定义 Open WebUI License——保留品牌可自由使用，去除品牌商用需企业授权
- 本仓库自有内容（模板、文档、脚本）可自由取用
