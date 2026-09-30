@echo off
rem n8n 一键启动（Windows）— Node 与数据目录均在 D 盘
set "PATH=D:\tools\node\node-v22.21.1-win-x64;D:\tools\npm-global;%PATH%"
set "N8N_USER_FOLDER=D:\projects\Zcode_project\n8n-data"
n8n start
