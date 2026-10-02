# ComfyUI Windows 原生部署 + 第一个自定义节点

实测环境：Windows / Python 3.14 / Intel Arc 核显（无 NVIDIA）/ 2026-09 版 ComfyUI。

## 部署步骤

```bash
# 1. 克隆（国内走镜像）
git clone --depth 1 https://gh-proxy.com/https://github.com/comfyanonymous/ComfyUI.git

# 2. venv（D 盘）+ 依赖（清华源）
cd ComfyUI && python -m venv .venv
./.venv/Scripts/python.exe -m pip install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple
./.venv/Scripts/python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Python 3.14 的一个坑**：`requirements.txt` 里的 `comfyui-workflow-templates`
依赖的素材包 `comfyui-workflow-templates-media-assets-02` 不支持 3.14，
会导致整次安装失败。解法：

```bash
grep -v "comfyui-workflow-templates" requirements.txt > req_no_templates.txt
./.venv/Scripts/python.exe -m pip install -r req_no_templates.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

只损失 UI 里的工作流模板画廊，核心功能与自定义节点完全不受影响。

## 启动

```bash
cd ComfyUI && ./.venv/Scripts/python.exe main.py --cpu
# 浏览器打开 http://127.0.0.1:8188
```

- `--cpu`：本机是 Intel Arc 核显（无 NVIDIA），CPU 模式跑 UI / 开发节点 / 小工作流足够；
  真要本地生图可研究 ipex-llm 的 Intel 路线，或把 ComfyUI 部署到有独卡的机器/云 GPU 上
- torch 版本说明：PyTorch 2.14+ 已提供 cp314 Windows 轮子，Python 3.14 直接可用，无需降级

## 验证自定义节点（本仓库 comfyui-lab 目录内即是完整节点包）

1. 把 `__init__.py` 所在目录复制到 `ComfyUI/custom_nodes/comfyui-my-lab/`
2. 启动日志出现 `0.0 seconds: ...\custom_nodes\comfyui-my-lab` 即加载成功
3. 端到端测试（已验证通过）：

```bash
curl -X POST http://127.0.0.1:8188/prompt -H "Content-Type: application/json" \
  -d '{"client_id":"t","prompt":{"1":{"class_type":"GradientImage","inputs":{"width":512,"height":256,"red":0.85,"green":0.3,"blue":0.4,"direction":"diagonal"}},"2":{"class_type":"SaveImage","inputs":{"images":["1",0],"filename_prefix":"my-lab-test"}}}}'
# 数秒后 ComfyUI/output/ 出现 my-lab-test_00001_.png
```

## 二开路径建议

1. 改 `comfyui-my-lab`：给节点加新控件（见 `__init__.py` 注释，四种核心约定）
2. 读官方节点源码学真实写法：`ComfyUI/comfy_extras/nodes_*.py`（几百个现成例子）
3. 社区节点包范本：`ComfyUI/custom_nodes/` 下安装任意社区包阅读其结构
4. 模型接入：UI 拖入 workflow 或从模板库加载；模型文件放 `ComfyUI/models/` 对应子目录
