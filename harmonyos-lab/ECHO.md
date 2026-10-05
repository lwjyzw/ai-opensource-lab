# 回声音乐 Echo —— 从"仿网易云壳子"到"真功能 App"的改造实录

这是本仓库鸿蒙线的最终形态：把 887 行的 API 9 骨架（open_neteasy_cloud）
升级到 HarmonyOS 6.0.2，改名 **回声音乐 Echo**（bundleName `com.echo.music`），
全部内容接入真实 API —— 首页/推荐/榜单/歌单/播放来自
[NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)
本机服务，匿名树洞接自研持久化后端，歌曲用 AVPlayer **真播放**。

工程位置：`D:\projects\harmonyos\open_neteasy_cloud`（git diff 可见全部改动）。

## 架构

```
宿主机 (Windows)
├── :3000  NeteaseCloudMusicApi（node app.js，代理网易云全部接口）
└── :3001  treehole-server.js（自研：匿名树洞 GET/POST/点赞，JSON 落盘）
        ▲
        │ hdc rport tcp:3000/3001（反向端口转发，绕过防火墙）
        │
模拟器 (HarmonyOS 6.0.2, 10.0.2.15)
└── 回声音乐 Echo
    ├── HttpUtil.ets      双地址自动探测 + 请求重试 + 探测日志
    ├── EchoModels.ets    JSON→类手动映射（ArkTS 严格模式）
    ├── IndexPage.ets     首页/推荐/树洞/我的 四 Tab
    └── PlaylistPage.ets  歌单详情 + AVPlayer 状态机播放
```

## 一、后端部署（两个服务）

```bash
export PATH="/d/Program Files/Huawei/DevEco Studio/tools/node:$PATH"
# 音乐 API（Binaryify 30k★ 项目的 npm 包）
mkdir backend && cd backend && npm init -y
npm install NeteaseCloudMusicApi --registry=https://registry.npmmirror.com
node node_modules/NeteaseCloudMusicApi/app.js        # :3000
# 树洞 API（本仓库 harmonyos-lab/treehole-server.js，零依赖）
node treehole-server.js                              # :3001
```

注意：npm 包 `netease-cloud-music-api` 只是加密库；**服务器要装
`NeteaseCloudMusicApi`（大写）**，来自 nooblong/NeteaseCloudMusicApiBackup。

## 二、关键技巧：hdc rport 反向端口转发

模拟器（10.0.2.15，QEMU NAT）访问宿主机服务，直接写 10.0.2.2 会被
Windows 防火墙掐掉（TCP 能通但数据被吞，现象是 CLOSE_WAIT 挂死）。
最干净的方案：

```bash
hdc rport tcp:3000 tcp:3000   # 模拟器 127.0.0.1:3000 → 宿主机 :3000
hdc rport tcp:3001 tcp:3001
```

App 里直接请求 `http://127.0.0.1:3000`，防火墙完全不参与。
HttpUtil 同时保留 10.0.2.2 / 局域网 IP 作为兜底候选并自动探测。

## 三、AVPlayer 状态机（最重要的 API 认知）

`p.url = url` 赋值后**异步**进入 `initialized` 状态，立刻调 `prepare()`
会报 `unsupport prepare operation`。必须状态机驱动：

```ts
p.on('stateChange', (state: string) => {
  if (state === 'initialized') {
    p.prepare().then(() => p.play());
  }
  if (state === 'completed' || state === 'error') { this.isPlaying = false; }
});
await p.reset();
p.url = url;   // 触发 initialized → handler 自动 prepare+play
```

实测日志：`initialized → prepared → prepare ok → playing → play ok`。

## 四、网易云上游的坑（ECONNRESET / 空数据）

后端代理网易云时，上游会**间歇性** `read ECONNRESET`（反爬掐连接），
还会返回 HTTP 200 但 `playlist: null` / `data: [null]`。三层防御：

1. HttpUtil.get 自动重试 2 次
2. 页面数据区块**独立 try/catch**（banner 挂了不影响歌单，反之亦然）
3. 解析后校验空值，空则延时 800ms 重试 3 次

另外：`/top/list?idx=1` 在部分版本只支持 id 调用（500），
改用 `/playlist/detail?id=3778678` 取热歌榜。

## 五、构建与运行

```bash
# 构建（详见 DEPLOY.md 的 build-hap.bat）
hdc install entry\build\default\outputs\default\entry-default-unsigned.hap
hdc rport tcp:3000 tcp:3000 && hdc rport tcp:3001 tcp:3001
hdc shell aa start -a EntryAbility -b com.echo.music
```

启动页点"立即体验"→ 首页全是真实数据（真实轮播/真实歌单封面+播放量/
热歌榜 Top5）→ 点 GO 进热歌榜 → 点任意歌 ▶ 真播放（AVPlayer 走
网易云 CDN 音源）→ 树洞发帖（持久化，杀 App 重启仍在）。

## 六、实测记录

- ✅ personalized ok: 10（真实推荐歌单 10 张）
- ✅ toplist ok: 5（热歌榜前 5：海屿你/明知故犯/于是/甲乙丙丁/我不难过）
- ✅ play start → url ok → state: initialized → prepared → **playing**
- ✅ 树洞发帖 → force-stop 重启 → 帖子仍在（服务端 JSON 落盘）
- ✅ 点赞 128 → ❤️129（状态翻转 + 计数更新）


## 七、借鉴 Mineradio-Android 的功能增强（二开对二开）

从作者自己的 [Mineradio-Android](https://github.com/lwjyzw/Mineradio-Android)
（Electron 音乐播放器的 Android 完整移植版）借鉴三个成熟模式并鸿蒙化：

### 1. 全局音频播放服务（AudioPlayer.ets）
Mineradio 的全局播放器+队列模式：模块级单例 AVPlayer + 队列 + 状态广播。
歌单页/搜索页/本地页共用一个播放器实例，`completed` 状态自动切下一首，
页面通过 subscribe/unsubscribe 订阅播放状态刷新 UI。

### 2. 搜索页（SearchPage.ets）
`/search` → `/cloudsearch` 双接口回退（网易云对归档版 API 的搜索接口
间歇性 502 限流），真实结果（Beyond《海阔天空》全版本实测），
点击即用全局服务播放。

### 3. 持久化本地曲库（LocalPage.ets）
照抄 Mineradio Android 的方案：系统 AudioViewPicker 导入
MP3/FLAC/WAV/OGG/M4A/AAC/Opus → **复制进应用沙箱 filesDir/local/**
（不依赖会失效的临时 uri）→ preferences 持久化曲库列表 →
AVPlayer fdSrc 播放本地文件 → 支持删除与播放全部。

### 踩坑补充

- Git Bash 里 `export MSYS_NO_PATHCONV=1` 之后，所有传给 Windows 程序的
  路径参数必须用 `D:\...` 反斜杠风格，否则 hvigorw.js 会被拼成
  `D:\d\Program Files\...` 直接 MODULE_NOT_FOUND（这个坑让三次构建
  静默装了旧包）
- uitest 点击坐标来自 dumpLayout 的 bounds 中心；**键盘弹出会盖住
  下半屏节点**，先 Back 收键盘再定位
- Emoji 图标（🎵❤️）在 ArkTS Text 里开箱即用，做轻量 UI 够用
