# ArkTS 仿网易云（open_neteasy_cloud）API 9 → HarmonyOS 6.0.2 迁移实录

把 [linwu-hi/open_neteasy_cloud](https://github.com/linwu-hi/open_neteasy_cloud)（369★，API 9 老工程）
完整迁移到 **HarmonyOS 6.0.2 / API 22**，并用 **纯命令行构建出 HAP**——不打开 DevEco Studio、
构建过程零联网。本机：DevEco Studio 6.0.2.642（自带 SDK 6.0.2/ hvigor 6.22.3 / node 18 / JBR 21）。

## 背景认知

- 该仓库是 API 9（2023，HarmonyOS 4 时代）的骨架工程：仅 887 行 ArkTS、9 个文件、
  本地 mock 数据（README 宣传的完整功能并未包含在源码里）
- 装了 DevEco 6 后打开老工程，IDE 会提示"项目结构需要升级"——本文记录手动完成全过程

## 迁移清单（7 处改动）

### 1. `hvigor/hvigor-config.json5` — 升级构建系统 + 离线化

hvigor 2.4.2 无法识别新 SDK。关键坑：hvigor 官方包**不在 npmjs 也不在华为云镜像**
（`@ohos/hvigor` 404）， wrapper 联网安装必挂。解法是用 `file:` 依赖直连
DevEco 自带的同版本（构建零联网）：

```json5
{
  "modelVersion": "5.0.0",
  "dependencies": {
    "@ohos/hvigor": "file:D:/Program Files/Huawei/DevEco Studio/tools/hvigor/hvigor",
    "@ohos/hvigor-ohos-plugin": "file:D:/Program Files/Huawei/DevEco Studio/tools/hvigor/hvigor-ohos-plugin"
  }
}
```

### 2. `build-profile.json5` — 新 schema

API 9 的 `compileSdkVersion: 9` / `compatibleSdkVersion: 9` 数值写法已废除，
新写法是字符串 + `runtimeOS` 上移到 app 层：

```json5
"products": [{
  "name": "default",
  "compatibleSdkVersion": "6.0.2(22)",
  "runtimeOS": "HarmonyOS"
}]
```

### 3. 根/entry 两个 `hvigorfile.ts` — 新写法

老写法是 `export { appTasks } from '...'`（re-export），新写法必须 default 导出对象，
且**删除 `apps: [...]` 数组**（模块只在 build-profile 声明）：

```ts
import { appTasks } from '@ohos/hvigor-ohos-plugin';
export default { system: appTasks, plugins: [] }
```

### 4. `oh-package.json5` — 加 `"modelVersion": "5.0.0"`

缺这个字段 hvigor 直接报"项目结构需要升级"。

### 5. `EntryAbility.ts` → `EntryAbility.ets`

API 22 要求 ability 源文件为 .ets，同步改 module.json5 的 `srcEntry`。
`@ohos.app.ability.UIAbility` 旧式 import 仍可编译，无需改。

### 6. ArkTS 严格模式三连（编译期报错逐个修）

| 报错 | 修法 |
|---|---|
| `Property 'title' has no initializer` | bean 类字段给默认值：`title: ResourceStr = ''` |
| `arkts-no-props-by-index`（`router.getParams()[KEY]`） | `let params = router.getParams() as Record<string, Object>; params[KEY] as ResourceStr` |
| `arkts-no-any-unknown`（ForEach key 生成器） | 参数显式标类型 `(item: T, index: number)` |

### 7. 明文 HTTP 图片 → https

`http://p1.music.126.net/...` 在 NEXT 默认被拦，改 https。

## 命令行构建（build-hap.bat 核心）

```bat
set "DEVECO_SDK_HOME=D:\Program Files\Huawei\DevEco Studio\sdk"
set "PATH=D:\Program Files\Huawei\DevEco Studio\jbr\bin;D:\Program Files\Huawei\DevEco Studio\tools\node;%PATH%"
cd /d D:\projects\harmonyos\open_neteasy_cloud
node "D:\Program Files\Huawei\DevEco Studio\tools\hvigor\bin\hvigorw.js" --mode module -p product=default assembleHap --no-daemon
```

三个环境要点：
- `DEVECO_SDK_HOME` 指向 SDK 根目录
- `java` 用 DevEco 自带 JBR（JDK 21.0.8）——PackageHap 步骤会 spawn java，
  系统没有 JDK 也能构建（省掉 190MB 的 Temurin 下载）
- node 用 DevEco 自带 v18.20.1，版本刚好满足 hvigor 6

产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`（657KB）

## 运行

unsigned HAP 无法直接安装。最简单路径：用 DevEco Studio 打开迁移后的工程，
插上真机（或起模拟器）直接点 Run——IDE 会自动做本地签名。想纯命令行签名则需
`hap-sign-tool` + 本地证书链（OpenHarmony SIG 有现成 profiling 工具）。

## 二开路径建议

1. **接真数据**：源码里没有任何网络层，接入
   [Binaryify/NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)
   （自部署 Node 服务），把 PageViewModel 的 mock 换成 `@ohos.net.http` 请求
2. **补页面**：README 宣传的播放页/歌单/搜索都没实现，`main_pages.json` 加页面 +
   `router.pushUrl` 抄现有跳转模式
3. **现代化**：老 `@ohos.router` 已被 `Navigation/HM Router` 取代，可作为练手重构
