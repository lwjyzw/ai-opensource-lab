@echo off
rem 一键命令行构建 HAP（不需要打开 DevEco Studio，不需要联网）
set "DEVECO_SDK_HOME=D:\Program Files\Huawei\DevEco Studio\sdk"
set "PATH=D:\Program Files\Huawei\DevEco Studio\jbr\bin;D:\Program Files\Huawei\DevEco Studio\tools\node;%PATH%"
cd /d D:\projects\harmonyos\open_neteasy_cloud
node "D:\Program Files\Huawei\DevEco Studio\tools\hvigor\bin\hvigorw.js" --mode module -p product=default assembleHap --no-daemon
