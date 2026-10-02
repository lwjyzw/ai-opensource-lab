"""ComfyUI 二开起步：自定义节点示例包

放在 ComfyUI/custom_nodes/ 下即可被自动加载（无需注册、无需重启工具）。
包含两个节点：
  1. GradientImage (image)  — 生成一张可调尺寸/颜色的渐变图，零模型依赖，
     用来第一次在画布上跑通"我的节点"出图
  2. TextCase    (text)    — 文本大小写转换 + 前后缀拼接，演示最简单的字符串节点写法

官方文档: https://docs.comfy.org/essentials/custom-node-away-lifecycle
更多实战范本: ComfyUI/custom_nodes/ 下的社区节点包
"""

import torch


class GradientImage:
    """最简 IMAGE 节点：输出 [B, H, W, C] float32 张量，值域 0-1（ComfyUI 图像约定）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 512, "min": 16, "max": 4096, "step": 8}),
                "height": ("INT", {"default": 512, "min": 16, "max": 4096, "step": 8}),
                "red": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01}),
                "green": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                "blue": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "direction": (["horizontal", "vertical", "diagonal"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "make"
    CATEGORY = "my-lab"

    def make(self, width, height, red, green, blue, direction):
        base = torch.tensor([red, green, blue], dtype=torch.float32)
        img = torch.ones(height, width, 3) * base

        if direction == "horizontal":
            fade = torch.linspace(0.0, 1.0, width).view(1, width, 1)
        elif direction == "vertical":
            fade = torch.linspace(0.0, 1.0, height).view(height, 1, 1)
        else:  # diagonal
            fx = torch.linspace(0.0, 1.0, width).view(1, width, 1)
            fy = torch.linspace(0.0, 1.0, height).view(height, 1, 1)
            fade = (fx + fy) / 2

        img = img * (1 - fade) + fade  # 向白色渐变
        return (img.unsqueeze(0),)


class TextCase:
    """最简 STRING 节点：演示必填/可选输入、多返回值写法"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "Hello ComfyUI", "multiline": True}),
                "mode": (["upper", "lower", "title"],),
            },
            "optional": {
                "prefix": ("STRING", {"default": ""}),
                "suffix": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "length")
    FUNCTION = "convert"
    CATEGORY = "my-lab"

    def convert(self, text, mode, prefix="", suffix=""):
        out = {"upper": text.upper, "lower": text.lower, "title": text.title}[mode]()
        out = f"{prefix}{out}{suffix}"
        return (out, len(out))


# ComfyUI 启动时读取这两个映射表完成节点注册
NODE_CLASS_MAPPINGS = {
    "GradientImage": GradientImage,
    "TextCase": TextCase,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GradientImage": "渐变图 (My Lab)",
    "TextCase": "文本加工 (My Lab)",
}
