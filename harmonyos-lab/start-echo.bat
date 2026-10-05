@echo off
chcp 65001 > nul
title 回声音乐 Echo 一键启动

rem ============ 1. 启动两个后端服务 ============
set "PATH=D:\Program Files\Huawei\DevEco Studio\tools\node;%PATH%"
cd /d D:\projects\harmonyos\backend

start "回声-音乐API" cmd /c "node node_modules\NeteaseCloudMusicApi\app.js > music-api.log 2>&1"
start "回声-树洞API" cmd /c "node treehole-server.js > treehole.log 2>&1"
echo [1/3] 后端服务启动中 (3000 音乐 / 3001 树洞)...
timeout /t 5 > nul

rem ============ 2. 端口转发到模拟器 ============
set "HDC=D:\Program Files\Huawei\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe"
"%HDC%" rport tcp:3000 tcp:3000 > nul
"%HDC%" rport tcp:3001 tcp:3001 > nul
echo [2/3] 端口转发已建立 (模拟器 127.0.0.1 → 宿主机)

rem ============ 3. 拉起应用 ============
"%HDC%" shell aa force-stop com.echo.music > nul 2>&1
"%HDC%" shell aa start -a EntryAbility -b com.echo.music
echo [3/3] 回声音乐已启动 ✓
echo.
echo 注意：模拟器需先在 DevEco Studio 的 Device Manager 里开机。
echo 关闭本窗口不影响已启动的服务；重新开机模拟器后重跑本脚本即可。
pause
