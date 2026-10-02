# Mindustry 游戏 Mod 二开实录（Level 1 JSON + Level 2 Java）

给开源 Java 游戏 **Mindustry**（v8 Build 160.5，~24k★，GPL-3.0）写 Mod 的完整实录。
"改代码 → 重启游戏 → 立刻看到效果"是所有二开形式里正反馈最快的。

实测环境：Windows / Temurin JDK 17.0.20.1 / Mindustry v160.5 / 全部落 D 盘。

## 一、环境准备

### 1. 便携 JDK 17（清华 Adoptium 镜像，免安装）

```bash
mkdir -p /d/tools/jdk-17 && cd /d/tools
curl -sL -o jdk17.zip "https://mirrors.tuna.tsinghua.edu.cn/Adoptium/17/jdk/x64/windows/OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1.zip"
powershell -Command "Expand-Archive -Path jdk17.zip -DestinationPath jdk-17 -Force"
```

### 2. 游戏本体（直接用官方预构建 jar，不需要编译整个游戏）

```bash
mkdir -p /d/projects/mindustry/game && cd /d/projects/mindustry/game
curl -sL -o Mindustry.jar "https://gh-proxy.com/https://github.com/Anuken/Mindustry/releases/download/v160.5/Mindustry.jar"
```

稳定版 release 在 `Anuken/Mindustry/releases`；`Anuken/MindustryBuilds` 是每日滚动
的 BE（bleeding edge）构建，Mod 兼容性不如稳定版。

### 3. 关键技巧：数据目录便携化到 D 盘

桌面版**没有** `-data` 参数（已读 `DesktopLauncher.java` 源码确认），数据目录
硬编码取 `OS.getAppDataDirectoryString()` = `%APPDATA%`。便携化解法是
**只给游戏进程注入自定义 APPDATA 环境变量**：

```bash
export APPDATA="D:/projects/mindustry/data"
java -jar Mindustry.jar
```

游戏的数据、存档、Mod 全部落到 `D:/projects/mindustry/data/Mindustry/`，
其他程序不受影响，C 盘零写入。

一键启动脚本 `start-mindustry.bat`：

```bat
@echo off
set "JAVA_HOME=D:\tools\jdk-17\jdk-17.0.20.1+1"
set "APPDATA=D:\projects\mindustry\data"
"%JAVA_HOME%\bin\java.exe" -jar D:\projects\mindustry\game\Mindustry.jar
```

## 二、Level 1：JSON 内容 Mod（零编译，10 分钟）

`my-lab-mod/` 目录即完整 Mod，复制到 `数据目录/Mindustry/mods/` 下即可。

```
my-lab-mod/
├── mod.json                      # 模元数据（minGameVersion: 146）
├── content/
│   ├── items/crystal.hjson       # 自定义物品：实验室晶体
│   └── blocks/lab-wall.hjson     # 自定义方块：晶体护墙（引用自家物品）
└── sprites/                      # 32x32 物品图 / 64x64(size2) 方块图
```

**踩坑记录**：
- HJSON 里描述文本想用 `[accent]...[]` 富文本方括号必须给整个值加引号，
  否则 `[` 被当成数组解析直接炸掉整个物品定义——**而物品加载失败会让所有
  引用它的方块连锁失败**，报错却指向方块的 requirements，极具迷惑性
- 贴图缺失显示为 "?"，不阻塞加载；`sprites/` 目录按约定路径自动映射

## 三、Level 2：Java 行为 Mod（自定义方块行为）

`my-lab-java/` 目录。基于官方模板 `Anuken/MindustryJavaModTemplate` 改造，
核心是一个自愈护墙：

```java
public class RegenWall extends Wall {
    public float healPercentPerSecond = 0.4f;   // hjson 可直接覆盖的字段

    public RegenWall(String name) {
        super(name);
        update = true;   // 没有 update = true，updateTile 永远不会被调用
    }

    public class RegenWallBuild extends WallBuild {   // 命名约定：<类名>Build
        @Override
        public void updateTile() {
            if (damaged()) {
                float amount = maxHealth * healPercentPerSecond / 60f * delta();
                health(Math.min(maxHealth, health + amount));
            }
        }
    }
}
```

hjson 通过 `type: mylab.RegenWall` 绑定 Java 类，其余字段照常 hjson 配置。
**Java Mod 三件套约定**：继承原版 Block → 定义 `<类名>Build` 内部类覆写行为 →
hjson 绑定 type 并配字段。

### 构建配置（国内网络适配）

- `gradle-wrapper.properties` 的 distributionUrl 换成腾讯镜像：
  `https://mirrors.cloud.tencent.com/gradle/gradle-9.4.1-bin.zip`
- `build.gradle` 的 ivy 仓库 url 改成 `https://gh-proxy.com/https://github.com/`
  （模板从 Mindustry release 拉 dependencies.jar）
- `GRADLE_USER_HOME` 指到 D 盘，避免 gradle 缓存写 C 盘

### 踩坑记录

1. **GBK 编译错误**：中文 Windows 的 javac 默认 GBK 读源码，UTF-8 中文注释
   直接 18 个"编码不可映射字符"。修复：build.gradle 加
   `tasks.withType(JavaCompile){ options.encoding = 'UTF-8' }`
2. **API 认知**：`heal(float)`、`efficiency()` 在普通墙的 Build 上不存在
   （后者是耗电建筑的概念）——直接 `health(Math.min(maxHealth, health + x))`
3. **Mod 会被自动禁用**：内容加载报错的 Mod 会被游戏标记禁用并写入
   `settings.bin`（二进制），之后修好代码也不会自动恢复。全新安装可直接删
   `settings.bin` + `settings_backup.bin` 重置；有存档则进游戏 Mods 菜单手动启用

### 构建

```bash
export JAVA_HOME="D:\\tools\\jdk-17\\jdk-17.0.20.1+1"
export GRADLE_USER_HOME="D:/tools/gradle-home"
cd my-lab-java && gradlew.bat jar --no-daemon
# 产物 build/libs/my-lab-javaDesktop.jar → 复制到 mods/ 目录
```

## 四、验证

游戏启动日志同时出现三行即为全部生效：

```
[MyLabJava] mod loaded
Loading mod: My Lab Java Mod
Loading mod: My Lab Mod
```

游戏内：建造菜单 → 防御分类 → `Lab Wall` / `Regen Wall`；物品栏搜 `crystal`。
放一面 Regen Wall 让敌人打，看它自动回血——这就是你写的 Java 在游戏里跑。

## 五、源码研读入口

游戏完整源码 `Anuken/Mindustry`（约 30 万行 Java）：
- `core/src/mindustry/core/Logic.java` — 游戏主事件循环
- `core/src/mindustry/core/World.java` — 地图与瓦片世界
- `core/src/mindustry/world/blocks/` — 所有方块基类（写 Mod 的 API 词典）
- `core/src/mindustry/content/Blocks.java` — 全部原版方块的实例化参数（最好的 hjson 参考书）
- `core/src/mindustry/mod/ContentParser.java` — hjson 如何变成游戏对象
