#!/bin/bash
# 积分系统部署脚本 - Windows WSL2 + Docker Desktop
# 用法: bash deploy-wsl2.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
CONTAINER_NAME="ubuntu-dev"

echo "=== 积分系统 Docker 部署 (WSL2) ==="
echo ""

# 1. 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装或未启动"
    echo "请先启动 Docker Desktop"
    exit 1
fi
echo "✅ Docker 已就绪"

# 2. 检查 docker-compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ docker-compose 未安装"
    exit 1
fi
echo "✅ docker-compose 已就绪"

# 3. 停止并删除旧容器（如果存在）
echo ""
echo "清理旧容器..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# 4. 启动 Ubuntu 容器
echo ""
echo "启动 Ubuntu 22.04 容器..."
docker run -d \
    --name $CONTAINER_NAME \
    --hostname ubuntu-dev \
    -p 2222:22 \
    -p 8000:8000 \
    -p 3000:3000 \
    -p 8080:8080 \
    ubuntu:22.04 \
    bash -c "
        export DEBIAN_FRONTEND=noninteractive &&
        apt-get update -qq &&
        apt-get install -y -qq openssh-server curl git python3 python3-pip > /dev/null 2>&1 &&
        echo 'root:points2026' | chpasswd &&
        mkdir -p /var/run/sshd &&
        sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config &&
        sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config &&
        /usr/sbin/sshd &&
        echo '✅ Ubuntu 容器已就绪，SSH 端口 2222' &&
        tail -f /dev/null
    "

echo "✅ Ubuntu 容器已启动 (容器名: $CONTAINER_NAME)"

# 5. 等待容器启动
echo ""
echo "等待容器初始化..."
sleep 5

# 6. 复制项目文件到容器
echo ""
echo "复制项目文件到容器..."

# Backend
docker cp "$PROJECT_DIR/backend/." $CONTAINER_NAME:/opt/points-system/backend/ 2>/dev/null || {
    docker exec $CONTAINER_NAME mkdir -p /opt/points-system/backend
    docker cp "$PROJECT_DIR/backend/." $CONTAINER_NAME:/opt/points-system/backend/
}

# Frontend dist
docker exec $CONTAINER_NAME mkdir -p /opt/points-system/frontend
docker cp "$PROJECT_DIR/frontend/dist/." $CONTAINER_NAME:/opt/points-system/frontend/

# Deploy scripts
docker exec $CONTAINER_NAME mkdir -p /opt/points-system/deploy
docker cp "$PROJECT_DIR/deploy/Dockerfile.backend" $CONTAINER_NAME:/opt/points-system/deploy/
docker cp "$PROJECT_DIR/deploy/Dockerfile.frontend" $CONTAINER_NAME:/opt/points-system/deploy/
docker cp "$PROJECT_DIR/deploy/nginx.conf" $CONTAINER_NAME:/opt/points-system/deploy/

echo "✅ 文件已复制"

# 7. 在容器内安装 Backend 依赖并启动
echo ""
echo "安装 Backend..."
docker exec $CONTAINER_NAME bash -c "
    cd /opt/points-system/backend &&
    pip3 install -q fastapi uvicorn pydantic aiofiles python-dateutil 2>/dev/null &&
    mkdir -p /opt/points-system/backend/data &&
    echo '✅ Backend 依赖已安装'
"

echo ""
echo "启动 Backend 服务..."
docker exec -d $CONTAINER_NAME bash -c "
    cd /opt/points-system/backend &&
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/backend.log 2>&1 &
    echo 'Backend PID: ' && pgrep -f uvicorn
"

# 8. 在容器内安装 Nginx 并启动 Frontend
echo ""
echo "安装并启动 Frontend (Nginx)..."
docker exec $CONTAINER_NAME bash -c "
    apt-get install -y -qq nginx > /dev/null 2>&1 &&
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
    nginx -t && nginx
    echo '✅ Frontend 已启动 (端口 3000)'
"

echo ""
echo "=== 部署完成 ==="
echo ""
echo "📍 服务地址（从 Windows 浏览器访问）："
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📍 容器信息："
echo "   容器名: $CONTAINER_NAME"
echo "   SSH:    localhost:2222 (root / points2026)"
echo ""
echo "常用命令："
echo "   进入容器: docker exec -it $CONTAINER_NAME bash"
echo "   查看日志: docker logs $CONTAINER_NAME"
echo "   停止服务: docker stop $CONTAINER_NAME"
echo "   删除容器: docker rm -f $CONTAINER_NAME"
