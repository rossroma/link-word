# 猜词游戏 — 服务器部署指南

## 架构

```
Caddy (:80/:443)
  └─ reverse_proxy → link-word:8000 (FastAPI + 静态文件 + ONNX 推理)
```

单一容器，无需 nginx、无需下载模型、无需挂载 volume。

## 部署步骤

### 1. 首次部署（服务器上手动操作）

```bash
ssh root@<server-ip>
cd /srv/caddy/sites
git clone git@github.com:rossroma/link-word.git
```

### 2. 添加服务到 docker-compose.yml

编辑 `/srv/caddy/docker-compose.yml`，将 `deploy/docker-compose.snippet.yml` 的内容添加到 `services:` 下。

### 3. 添加域名路由到 Caddyfile

编辑 `/srv/caddy/Caddyfile`，添加：

```
word.rossroma.com {
    reverse_proxy link-word:8000
}
```

### 4. 启动服务

```bash
cd /srv/caddy
docker compose up -d --build link-word
docker compose restart caddy
```

### 5. 验证

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/
```

## 后续更新

推送代码到 `main` 分支 → GitHub Actions 自动部署（git pull + docker compose up --build link-word）。

## 技术说明

- **ONNX Runtime** 替代 PyTorch，pip 包从 500MB 降到 15MB，构建只需 45 秒
- **模型已内置**在镜像中（91.5MB），无需启动时下载
- **词库**内置 110 个词，无需外部文件