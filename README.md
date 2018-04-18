# PortMonitor

一个微小的服务端端口监控程序，带web界面，支持通过web重启服务器程序（需自定义配置）
![index](http://baidu.com/pic/doge.png)https://raw.githubusercontent.com/lwQin/PortMonitor/master/img/index.png)

## 初始化
请自行安装python虚拟环境（virtualenv），以下操作均在 **venv** 环境下进行，操作系统环境为 **Windows**
### 安装第三方库
```shell
(venv) path\to\project\: pip install -r requiretments\requirements.txt
(venv) path\to\project\: pip install requiretments\tornado-5.0.2-cp36-cp36m-win_amd64.whl
```

## 配置
### 1. 配置服务端运行地址及端口
编辑 **path\to\project\$version\web\config.json** 
```json
{
	"server": {
		"host": "localhost",
		"port": "8888"
	},
	"version": "main"
}
```

### 2. 配置需要监控的服务器
编辑 **path\to\project\$version\web\servers.json**
```json
{
    "默认分组": [
        {
            "type": "server",
            "description": "本地web 80端口",
            "host": "localhost",
            "port": 80,
            "flag": "localserver"
        }
    ]
}
```
> *必须存在一个分组及服务器！*

### 3. 配置重启脚本（如有）
编辑 **path\to\project\$version\ServerInfo.json**
```json
{
	"serverflag": {
		"host": "host",
		"port": 22,
		"username": "username",
		"password": "password",
		"cmd_path": "command",
		"log_path": "/path/to/log"
	}
}
```
> json键值必须与服务器信息中的 **flag** 相对应

### 4. 配置web应用
以 nginx 为例子，运行环境为 Windows，分别配置 main 和 test 的虚拟主机指向对应的 **/web** 目录
```config
...
location / {
    root   path\\to\project\\main\\web;
    index  index.html index.htm;
}
alise /test {
    root   path\\to\project\\test\\web;
    index  index.html index.htm;
}
...
```
配置完成后启动 nginx 及服务端
```shell
start path\\to\\nginx.exe

\path\to\venv\python.exe \path\to\project\$version\Server.py
```
即可通过 http://localhost 访问 main 版本，http://localhost/test 访问 test 版本。
web 应用将读取 **/web/config.json** 自动配置服务器地址