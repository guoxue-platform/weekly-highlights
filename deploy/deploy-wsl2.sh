#!/bin/bash
# 积分系统部署脚本 - Windows Docker Desktop (WSL2 环境)
# 使用: bash deploy-wsl2.sh
#
# 前提条件（wqs 需要执行）：
# 1. Docker Desktop 已安装（Windows）
# 2. WSL2 已安装
# 3. Docker Desktop 设置中启用 WSL Integration

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER_NAME="ubuntu-dev"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo "=== 积分系统 Docker 部署 (WSL2 + Docker Desktop) ==="
echo ""

# 检查 docker 是否可用
if ! docker info &> /dev/null; then
    echo "❌ Docker 不可用"
    echo "请确保："
    echo "  1. Docker Desktop 已启动（Windows）"
    echo "  2. Docker Desktop Settings → Resources → WSL Integration → 启用 Ubuntu"
    exit 1
fi
echo "✅ Docker 可用 ($(docker version --format '{{.Server.Version}}' 2>/dev/null))"

# 清理旧容器
echo ""
echo "清理旧容器..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# 创建网络（如果不存在）
docker network create points-net 2>/dev/null || true

# 启动 Ubuntu 容器
echo ""
echo "启动 Ubuntu 22.04 容器..."
docker run -d \
    --name $CONTAINER_NAME \
    --hostname ubuntu-dev \
    --network points-net \
    -p 2222:22 \
    -p $BACKEND_PORT:8000 \
    -p $FRONTEND_PORT:3000 \
    ubuntu:22.04 \
    bash -c "
        export DEBIAN_FRONTEND=noninteractive &&
        apt-get update -qq &&
        apt-get install -y -qq openssh-server curl git python3 python3-pip nginx > /dev/null 2>&1 &&
        echo 'root:points2026' | chpasswd &&
        mkdir -p /var/run/sshd /opt/points-system/backend/data /opt/points-system/frontend &&
        sed -i 's/#PermitRootLogin yes/PermitRootLogin yes/' /etc/ssh/sshd_config &&
        sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config &&
        /usr/sbin/sshd &&
        echo '✅ Ubuntu 容器初始化完成'
        tail -f /dev/null
    "

echo "✅ Ubuntu 容器已启动 (容器名: $CONTAINER_NAME)"

# 等待容器完全启动
echo ""
echo "等待容器初始化..."
sleep 8

# 复制项目文件到容器
echo ""
echo "复制项目文件..."

# Backend
docker cp "$PROJECT_DIR/backend/." $CONTAINER_NAME:/opt/points-system/backend/

# Frontend dist
docker cp "$PROJECT_DIR/frontend/dist/." $CONTAINER_NAME:/opt/points-system/frontend/

echo "✅ 文件已复制到容器"

# 安装 Backend 依赖
echo ""
echo "安装 Backend 依赖..."
docker exec $CONTAINER_NAME bash -c "
    cd /opt/points-system/backend &&
    pip3 install -q fastapi uvicorn pydantic aiofiles python-dateutil 2>/dev/null &&
    echo '✅ Backend 依赖已安装'
"

# 启动 Backend
echo ""
echo "启动 Backend 服务..."
docker exec -d $CONTAINER_NAME bash -c "
    cd /opt/points-system/backend &&
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/backend.log 2>&1 &
    sleep 2
    curl -s http://localhost:8000/health && echo ' ✅ Backend 健康'
"

# 配置 Nginx + 启动 Frontend
echo ""
echo "配置 Nginx..."
docker exec $CONTAINER_NAME bash -c "
    cat > /etc/nginx/sites-available/default << 'NGINX_EOF'
server {
    listen 3000;
    root /opt/points-system/frontend;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
NGINX_EOF
    nginx -s reload 2>/dev/null || nginx
    echo '✅ Frontend (Nginx) 已启动'
"

# 验证服务
echo ""
echo "=== 验证服务 ==="
sleep 2
BACKEND_OK=$(docker exec $CONTAINER_NAME curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null || echo "fail")
if [ "$BACKEND_OK" = "200" ]; then
    echo "✅ Backend API: http://localhost:$BACKEND_PORT"
    echo "✅ API Docs:   http://localhost:$BACKEND_PORT/docs"
else
    echo "⚠️ Backend 启动中，请稍后刷新"
fi

FRONTEND_OK=$(docker exec $CONTAINER_NAME curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo "fail")
if [ "$FRONTEND_OK" = "200" ]; then
    echo "✅ Frontend UI: http://localhost:$FRONTEND_PORT"
else
    echo "⚠️ Frontend 启动中，请稍后刷新"
fi

echo ""
echo "=== 部署完成 ==="
echo ""
echo "📍 访问地址（从 Windows 浏览器）："
echo "   积分系统: http://localhost:$FRONTEND_PORT"
echo "   API:       http://localhost:$BACKEND_PORT"
echo ""
echo "📍 容器管理命令："
echo "   进入容器: docker exec -it $CONTAINER_NAME bash"
echo "   查看日志: docker logs $CONTAINER_NAME"
echo "   停止:     docker stop $CONTAINER_NAME"
echo "   删除:     docker rm -f $CONTAINER_NAME"
echo ""
echo "📍 OpenClaw 部署（后续）："
echo "   进入容器后安装 OpenClaw"
