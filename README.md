# 猜词游戏 — 语义相似度挑战

基于中文语义相似度的猜词游戏。系统随机选择一个目标词，玩家输入猜测词汇，AI 通过 Embedding 模型计算语义相似度（0–100 分），帮助玩家一步步逼近答案。

## 游戏玩法

1. 系统随机选择一个中文词汇作为目标词
2. 玩家输入猜测词汇（最多 4 个字）
3. 系统返回 **0–100** 的语义相似度分数
4. 分数越高说明越接近目标词，根据分数反馈调整猜测方向
5. 在 50 次猜测内找到目标词即为胜利

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vanilla HTML/CSS/JS，SPA 架构 |
| 后端 | Python FastAPI |
| NLP 模型 | [BAAI/bge-small-zh-v1.5](https://huggingface.co/BAAI/bge-small-zh-v1.5)（~95MB） |
| 向量相似度 | 余弦相似度 |
| 反向代理 | Nginx (Alpine) |
| 部署 | Docker Compose + GitHub Actions CI/CD |

## 项目结构

```
link-word/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/             # API 路由（/api/game/*）
│   │   ├── core/            # 核心逻辑
│   │   │   ├── embedding.py       # Embedding 模型封装
│   │   │   ├── game_controller.py # 游戏流程控制
│   │   │   ├── scorer.py          # 相似度评分
│   │   │   ├── session.py         # 会话管理
│   │   │   ├── validator.py       # 输入校验
│   │   │   ├── word_picker.py     # 目标词选取
│   │   │   └── rate_limiter.py    # 频率限制
│   │   ├── data/            # 词库加载
│   │   ├── models/          # Pydantic 数据模型
│   │   └── main.py          # 应用入口
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── requirements.txt
├── frontend/                # 前端静态文件
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── api.js           # API 请求封装
│   │   ├── app.js           # 主应用逻辑
│   │   ├── components.js    # UI 组件
│   │   └── utils.js         # 工具函数
│   └── assets/
├── nginx/                   # Nginx 配置
│   └── nginx.conf
├── word_bank/               # 词库文件（JSON 格式）
├── scripts/
│   └── dev.sh               # 开发环境一键启动脚本
├── docker-compose.yml
└── .github/workflows/
    └── deploy.yml           # GitHub Actions 自动部署
```

## 快速开始

### 前置要求

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose

### 一键启动

```bash
./scripts/dev.sh
```

或手动启动：

```bash
docker compose up -d --build
```

首次启动会自动下载 Embedding 模型（约 95MB），请耐心等待。启动完成后：

- 🎮 **游戏页面**: http://localhost:3000
- 📖 **API 文档**: http://localhost:8000/api/docs

### 国内环境

如需加速模型下载，设置 HuggingFace 镜像：

```bash
export HF_ENDPOINT=https://hf-mirror.com
docker compose up -d --build
```

## 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `WORD_BANK_PATH` | `/app/word_bank/all.json` | 词库文件路径 |
| `MODEL_NAME` | `BAAI/bge-small-zh-v1.5` | Embedding 模型名称 |
| `MODEL_CACHE_DIR` | `/app/models` | 模型缓存目录 |
| `MAX_GUESSES` | `50` | 每局最大猜测次数 |
| `MIN_GUESS_INTERVAL_SECONDS` | `1.0` | 最小猜测间隔（秒） |
| `SESSION_TTL_SECONDS` | `3600` | 会话有效期（秒） |
| `HF_ENDPOINT` | — | HuggingFace 镜像地址 |

## API 端点

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/health` | 健康检查 |
| `POST` | `/api/game/new` | 创建新游戏 |
| `POST` | `/api/game/{session_id}/guess` | 提交猜测 |
| `GET` | `/api/game/{session_id}/history` | 获取猜测历史 |
| `POST` | `/api/game/{session_id}/giveup` | 放弃游戏 |

## 词库

词库为 JSON 格式，每个词条包含：

```json
{
  "word": "苹果",
  "category": "food",
  "difficulty": "easy"
}
```

内置回退词库包含 100 个中文词汇，覆盖 10 个类别：食物、动物、自然、物品、地点、职业、情感、动作、抽象、文化。

## 部署

项目通过 GitHub Actions 自动部署。推送代码到 `main` 分支后，自动执行：

1. SSH 连接到服务器
2. 拉取最新代码
3. 执行 `docker compose up -d --build`

需要在 GitHub Secrets 中配置：

- `SERVER_HOST` — 服务器地址
- `SERVER_USER` — SSH 用户名
- `SERVER_SSH_KEY` — SSH 私钥
- `SERVER_PATH` — 项目路径（如 `/srv/link-word`）

## 开发

```bash
# 查看日志
docker compose logs -f backend

# 停止服务
docker compose down

# 重建并启动
docker compose up -d --build
```

## License

MIT