# 环境检查表

> 10 分钟装齐。**所有命令在 macOS / Linux 终端可直接复制跑**。

## 1. 30 秒速查

```bash
bash <(curl -s https://raw.githubusercontent.com/.../check.sh)  # 待补
# 或手动跑下面 6 步
```

## 2. 6 步装齐

### Step 1 · Python 3.10+

```bash
# macOS
brew install python@3.12
export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"

# Ubuntu
sudo apt update && sudo apt install python3.12 python3-pip

# 验证
python3 --version    # 期望 3.10+
```

> ⚠ **避坑**：macOS 自带 Python 3.9 偏老，**一定要装新版本**。

### Step 2 · pip

```bash
python3 -m ensurepip --upgrade
python3 -m pip --version
```

### Step 3 · Docker

- **macOS**：[Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- **Windows**：装 WSL2 后再装 Docker Desktop
- **Linux**：`sudo apt install docker.io && sudo usermod -aG docker $USER`

**验证**：
```bash
docker --version
docker compose version
docker run hello-world
```

> ⚠ **避坑**：macOS 上 Docker Desktop 没启动？看菜单栏鲸鱼图标。
> "Cannot connect to Docker daemon"？启动 Docker Desktop 等 10 秒。

### Step 4 · Python 库

```bash
pip install rdflib pyshacl SPARQLWrapper anthropic gradio
```

**验证**：
```bash
python3 -c "import rdflib; print('rdflib', rdflib.__version__)"
python3 -c "import pyshacl; print('pyshacl OK')"
python3 -c "import anthropic; print('anthropic OK')"
```

### Step 5 · Anthropic API Key

```bash
# 注册：https://console.anthropic.com/
# 拿 API Key

export ANTHROPIC_API_KEY="sk-a...n```

> ⚠ **避坑**：API Key 不要 commit 到 Git。写入 `~/.zshrc` 或 `~/.bashrc`：
> ```bash
> echo 'export ANTHROPIC_API_KEY="sk-..."' >> ~/.zshrc
> source ~/.zshrc
> ```

### Step 6 · JDK（如果要用 Protégé）

```bash
brew install --cask temurin   # macOS
sudo apt install default-jre  # Ubuntu
```

**验证**：
```bash
java --version
```

## 3. 完整检查脚本

新建 `~/check-env.sh`：

```bash
#!/bin/bash
echo "=== 环境检查 ==="
echo ""

# Python
echo "Python: $(python3 --version 2>&1 || echo 'NOT FOUND')"
echo "Pip:    $(python3 -m pip --version 2>&1 | head -1 || echo 'NOT FOUND')"

# Docker
echo "Docker: $(docker --version 2>&1 || echo 'NOT FOUND')"
echo "Compose: $(docker compose version 2>&1 | head -1 || echo 'NOT FOUND')"

# Python libs
for lib in rdflib pyshacl SPARQLWrapper anthropic gradio; do
    python3 -c "import $lib; print('$lib', getattr($lib, '__version__', 'OK'))" 2>/dev/null \
        || echo "$lib: NOT FOUND"
done

# API Key
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "Anthropic API: SET (${ANTHROPIC_API_KEY:0:8}...)"
else
    echo "Anthropic API: NOT SET"
fi

# Java (optional)
echo "Java: $(java --version 2>&1 | head -1 || echo 'NOT FOUND (optional)')"

echo ""
echo "=== 检查完成 ==="
```

**跑**：
```bash
chmod +x ~/check-env.sh
~/check-env.sh
```

**期望输出**：
```
=== 环境检查 ===

Python: Python 3.12.4
Pip:    pip 24.0
Docker: Docker version 25.0.3
Compose: Docker Compose version v2.27.0
rdflib 7.0.0
pyshacl OK
SPARQLWrapper 2.0.0
anthropic OK
gradio OK
Anthropic API: SET (sk-ant-a...)

Java: openjdk 21.0.2 2024-01-16

=== 检查完成 ===
```

## 4. 故障排除

### 4.1 "docker: command not found"

- 装 Docker Desktop
- 重启终端
- 验证：`docker --version`

### 4.2 "Permission denied" on /var/run/docker.sock

```bash
sudo usermod -aG docker $USER
# 注销重新登录
```

### 4.3 Python 库装不上

```bash
# 用 venv 隔离
python3 -m venv ~/onto-venv
source ~/onto-venv/bin/activate
pip install rdflib pyshacl
```

### 4.4 Fuseki 启动失败

```bash
docker compose logs fuseki
# 看到 "Cannot bind to port 3030"？改 ports 为 "3031:3030"
```

### 4.5 SPARQL 查询超时

Fuseki 默认不设超时。可以在 `fuseki-config.ttl` 加：
```turtle
ja:context ja:Context ;
    ja:dataset <#dataset> ;
    ja:endpoint [
        ja:path "/shop" ;
        ja:queryTimeout "5000"  # 5 秒
    ] .
```

## 5. 验证环境：跑 Hello World

```bash
# 1. 启动 Fuseki
cd ~/ontology-hello
docker compose up -d
sleep 10

# 2. 健康检查
curl http://localhost:3030/$/ping
# 期望返回简单文本

# 3. 装 Python 库
pip install rdflib pyshacl

# 4. 跑第一个查询
curl -G http://localhost:3030/shop/query \
    --data-urlencode "query=SELECT * WHERE { ?s ?p ?o } LIMIT 1"
# 期望返回一条三元组
```

**全过 = 环境就绪。**

## 6. 卸载（如需）

```bash
# 停 Fuseki
cd ~/ontology-hello && docker compose down

# 删 Python 库
pip uninstall -y rdflib pyshacl SPARQLWrapper anthropic gradio

# 删 Docker（按系统走）
```

## 7. 速读建议

- 30 秒看完：第 1、2 节
- 装环境：按第 2 节顺序跑
- 跑通后：第 3 节验证
