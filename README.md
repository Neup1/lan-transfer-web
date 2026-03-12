# 局域网大文件传输工具

这是一个专门用于同一局域网内文件传输的命令行工具，适合你这种场景：
- A 电脑：公司 5G WiFi
- B 电脑：网线接入
- 两台机器在同一子网

工具文件：`lan_transfer.py`

## 你要的 3 个要求

1. 密码验证：采用 challenge-response（挑战握手）+ 会话 token，不需要明文反复发送密码。  
2. 传输速度：上传下载都用大块流式读写；下载端优先用 `sendfile`，在局域网下吞吐较高。  
3. 文件格式支持：按二进制传输，不限制扩展名，常见文档/压缩包/视频/镜像等都可传。

## 环境要求

- Python 3.11+（3.9+ 也基本可用）
- 无第三方依赖

## 快速开始

### 1) 在接收端（例如插网线的电脑）启动服务端

```powershell
python lan_transfer.py serve --bind 0.0.0.0 --port 9000 --root "D:\LAN_SHARE" --password "你的密码"
```

启动后会显示共享目录和端口。
然后在浏览器打开：`http://接收端IP:9000/`（例如 `http://192.168.1.20:9000/`）。

### 2) 在发送端上传文件

```powershell
python lan_transfer.py upload --server 192.168.1.20:9000 --password "你的密码" "F:\big\movie.mkv"
```

也可以指定远程路径：

```powershell
python lan_transfer.py upload --server 192.168.1.20:9000 --password "你的密码" "F:\big\movie.mkv" "videos/movie.mkv"
```

### 3) 下载文件（支持断点续传）

```powershell
python lan_transfer.py download --server 192.168.1.20:9000 --password "你的密码" "videos/movie.mkv" "D:\Downloads\movie.mkv"
```

## 常用命令

## Web 页面功能

打开 `http://服务端IP:9000/` 后可直接使用：
- 密码登录（与命令行同一密码）
- 文件列表和目录切换（含返回上级、刷新）
- 上传（支持多选 + 断点续传）
- 下载
- 新建文件夹

页面风格为简约风，边框和卡片采用柔和圆角与浅阴影。

### 查看远端目录

```powershell
python lan_transfer.py list --server 192.168.1.20:9000 --password "你的密码" "videos"
```

### 查看远端文件信息

```powershell
python lan_transfer.py stat --server 192.168.1.20:9000 --password "你的密码" "videos/movie.mkv"
```

### 创建远端目录

```powershell
python lan_transfer.py mkdir --server 192.168.1.20:9000 --password "你的密码" "videos"
```

## 断点续传与覆盖

默认行为：
- 上传：若远端已有同名文件且大小小于本地，会从断点继续。
- 下载：若本地已有同名文件且大小小于远端，会从断点继续。

可选参数：
- `--no-resume`：关闭断点续传，强制从 0 开始。
- `--force`：覆盖已有文件。

## 性能建议（局域网实测常见优化点）

- 尽量让接收端使用 SSD 目录作为 `--root`。
- 优先使用 5GHz WiFi（信号好时）或全程有线连接。
- 尽量减少同时高占用网络应用（网盘同步、在线视频等）。
- 打开 Windows 防火墙入站端口（例如 9000）。

## 安全说明

- 本工具已做密码认证，但默认是 HTTP 明文链路。  
- 在“公司可信内网 + 同子网”场景一般可用；若有更高安全要求，建议叠加 VPN 或内网 TLS 反代。

## 故障排查

- 无法连接：先 `ping` 服务端 IP，确认两台机器互通且端口未被防火墙拦截。  
- 认证失败：检查两端密码是否一致。  
- 传输中断：再次执行同一命令，默认会从断点继续。
