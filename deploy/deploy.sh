#!/bin/bash
# 积分系统部署脚本 - 适用 Ubuntu/Debian Linux

set -e

echo "=== 积分系统 Docker 部署脚本 ==="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "✅ Docker 已安装"
else
    echo "✅ Docker 已安装"
fi

# 检查 docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装"
    exit 1
fi
echo "✅ docker-compose 已安装"

# 创建部署目录
DEPLOY_DIR="/opt/points-system"
echo ""
echo "创建部署目录: $DEPLOY_DIR"
sudo mkdir -p $DEPLOY_DIR

# 复制文件
echo "复制部署文件..."
sudo cp -r deploy/* $DEPLOY_DIR/
sudo cp -r backend $DEPLOY_DIR/
sudo cp -r frontend $DEPLOY_DIR/

# 修改权限
sudo chown -R $USER:$USER $DEPLOY_DIR

cd $DEPLOY_DIR

# 构建并启动
echo ""
echo "构建 Docker 镜像..."
docker-compose build

echo ""
echo "启动服务..."
docker-compose up -d

echo ""
echo "=== 部署完成 ==="
echo "Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "Frontend UI: http://$(hostname -I | awk '{print $1}'):3000"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
