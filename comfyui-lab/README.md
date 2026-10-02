# ComfyUI — My Lab 节点包（二开起步示例）

一个最小可运行的自定义节点包，演示 ComfyUI 二开的核心契约：

## 节点

| 节点 | 类型 | 演示点 |
|---|---|---|
| 渐变图 (GradientImage) | IMAGE | torch 生成 `[1,H,W,3]` float 图像、INT/FLOAT/下拉框三种输入控件 |
| 文本加工 (TextCase) | STRING | 多行文本、optional 输入、多返回值 + RETURN_NAMES 命名 |

## ComfyUI 自定义节点核心约定（记住这四样就能写节点）

```python
NODE_CLASS_MAPPINGS = { "内部ID": 类 }          # 注册
NODE_DISPLAY_NAME_MAPPINGS = { "内部ID": "显示名" }  # UI 显示名
类.INPUT_TYPES()  # 声明输入控件（required/optional）
类.RETURN_TYPES / RETURN_NAMES / FUNCTION / CATEGORY
```

- IMAGE 张量约定：`[batch, height, width, channels]`，float32，值域 0-1，通道顺序 RGB
- 节点目录放在 `ComfyUI/custom_nodes/任意名字/`，启动时自动扫描加载
- 需要额外 pip 依赖时，在节点目录放 `requirements.txt`，启动器会提示安装

## 使用

1. 启动 ComfyUI（见上层 README）
2. 画布双击 / 右键 Add Node → 分类 `my-lab` → 拖入"渐变图"节点
3. 接到 Preview Image 节点，Queue Prompt，即可看到自己的节点第一次出图
