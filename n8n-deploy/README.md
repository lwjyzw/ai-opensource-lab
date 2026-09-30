# n8n Windows 原生部署实录（免 Docker）

目标环境：Windows 10/11，Docker 已卸载，无 Node.js，Python 3.14（n8n 不需要），
所有内容落在 D 盘。实测版本：n8n 2.22.6 / Node v22.21.1（2026-09）。

## 步骤一：免安装版 Node.js（D 盘，无管理员权限）

```bash
mkdir -p /d/tools/node && cd /d/tools/node
# 走 npmmirror 二进制镜像，直连 nodejs.org 也可以
curl -L -o node.zip "https://registry.npmmirror.com/-/binary/node/v22.21.1/node-v22.21.1-win-x64.zip"
powershell -Command "Expand-Archive -Path node.zip -DestinationPath . -Force"
# 验证
export PATH="/d/tools/node/node-v22.21.1-win-x64:$PATH" && node --version
```

## 步骤二：安装 n8n（关键：跳过原生编译）

n8n 依赖 sqlite3（原生模块）。它的预编译二进制托管在 GitHub Releases，
下载被网络重置时 node-pre-gyp 会回退到本地编译 → 本机没有 Visual Studio C++
→ **整个安装回滚失败**。绕过方式：

```bash
npm install -g n8n \
  --prefix "D:\tools\npm-global" \
  --ignore-scripts \
  --registry=https://registry.npmmirror.com
```

## 步骤三：手动补 sqlite3 二进制

npmmirror 镜像了 sqlite3 的预编译包（注意文件名**不带** `-unknown` 后缀，
目录在 `v5.1.7/` 根下而不是 `napi-v6/` 子目录）：

```bash
mkdir -p /d/tools/sqlite3-bin && cd /d/tools/sqlite3-bin
curl -sL -o sq.tar.gz \
  "https://registry.npmmirror.com/-/binary/sqlite3/v5.1.7/sqlite3-v5.1.7-napi-v6-win32-x64.tar.gz"
tar -xzf sq.tar.gz

# 放到 bindings 包搜索的路径（build/Release 是第一优先搜索位）
mkdir -p "/d/tools/npm-global/node_modules/n8n/node_modules/sqlite3/build/Release"
cp build/Release/node_sqlite3.node \
   "/d/tools/npm-global/node_modules/n8n/node_modules/sqlite3/build/Release/"
```

验证（应输出 `SQLITE3 LOAD OK`）：

```bash
cd /d/tools/npm-global/node_modules/n8n/node_modules/sqlite3
node -e "require('./lib/sqlite3-binding.js'); console.log('SQLITE3 LOAD OK')"
```

## 步骤四：启动（数据目录指向 D 盘）

`N8N_USER_FOLDER` 决定 SQLite 数据库、配置和加密密钥的存放位置，
不设置的话默认在 `C:\Users\<你>\.n8n`。

Git Bash（start-n8n.sh）：

```bash
export PATH="/d/tools/node/node-v22.21.1-win-x64:/d/tools/npm-global:$PATH"
export N8N_USER_FOLDER="D:/projects/Zcode_project/n8n-data"
n8n start
```

Windows（start-n8n.bat，可双击）：

```bat
@echo off
set "PATH=D:\tools\node\node-v22.21.1-win-x64;D:\tools\npm-global;%PATH%"
set "N8N_USER_FOLDER=D:\projects\Zcode_project\n8n-data"
n8n start
```

首次启动会自动完成数据库迁移，浏览器打开 http://localhost:5678 创建 owner 账号。

## 升级注意

`npm update -g n8n --prefix "D:\tools\npm-global" --ignore-scripts` 之后，
新版本会带新的 node_modules，**步骤三需要重做一次**（重新复制 .node 文件）。
其他步骤不受影响。

## 验证清单

- [x] `n8n --version` → 2.22.6
- [x] `curl localhost:5678/healthz` → `{"status":"ok"}`
- [x] C 盘零写入（Node、npm 全局目录、n8n 数据全部在 D 盘）
