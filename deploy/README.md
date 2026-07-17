# 猜词游戏 — 服务器部署指南

## 架构

```
Caddy (:80/:443)
  └─ reverse_proxy → link-word:8000 (FastAPI + 静态文件)
```

单一容器：FastAPI 同时提供 API 和前端静态文件，无需 nginx。

## 部署步骤

### 1. 上传项目到服务器

```bash
# 在本地打包（排除不需要的文件）
cd /path/to/link-word
rsync -avzP \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'node_modules' \
  --exclude '__pycache__' \
  --exclude '.claude' \
  --exclude 'nginx' \
  ./ root@<server-ip>:/srv/caddy/sites/link-word/
```

### 2. 添加服务到 docker-compose.yml

编辑 `/srv/caddy/docker-compose.yml`，将 `deploy/docker-compose.snippet.yml` 的内容添加到 `services:` 下。

### 3. 添加域名路由到 Caddyfile

编辑 `/srv/caddy/Caddyfile`，将 `deploy/Caddyfile.snippet` 的内容添加进去，替换 `guess.example.com` 为实际域名。

### 4. 添加 volumes 声明

在 `docker-compose.yml` 的 `volumes:` 下添加：

```yaml
  linkword_models:
```

### 5. 启动服务

```bash
cd /srv/caddy
docker compose up -d --build link-word
docker compose restart caddy
```

### 6. 验证

```bash
# 健康检查
curl http://localhost:8000/api/health

# 检查前端
curl http://localhost:8000/
```

## 首次启动说明

首次启动时会自动下载 embedding 模型（BAAI/bge-small-zh-v1.5，约 95MB），需要 30-60 秒。模型缓存在 `linkword_models` volume 中，重启不需要重新下载。

## 词库

项目内置了 100 个词的回退词库（10 个分类）。如需自定义词库，可在服务器上挂载：

```yaml
volumes:
  - ./sites/link-word/word_bank/all.json:/app/word_bank/all.json:ro
```

词库格式为 JSON 数组，每个元素包含 `word`、`category`、`difficulty` 字段。