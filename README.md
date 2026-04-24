# DevOps Lesson 示例系统

一个用于学习 CI/CD 的前后端完整项目。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | FastAPI + Python 3.11 | 高性能 API 框架，自动生成 OpenAPI 文档 |
| 前端 | React + Vite + TypeScript | 现代化前端构建 |
| 数据库 | SQLite | 轻量级本地数据库 |
| 部署 | Docker Compose | 容器化部署 |
| CI/CD | GitHub Actions | 自动化流水线 |

---

## 项目结构

```
devopslesson/
├── backend/                     # 后端服务
│   ├── app/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── database.py         # 数据库初始化
│   │   ├── models.py           # Pydantic 数据模型
│   │   ├── auth.py             # JWT 认证
│   │   └── routers/            # API 路由模块
│   │       ├── auth.py         # 登录/注册
│   │       ├── form.py         # 表单提交
│   │       ├── coupon.py       # 优惠券
│   │       └── query.py        # 查询
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                    # 前端应用
│   ├── src/
│   │   ├── App.tsx             # 路由配置
│   │   ├── main.tsx            # 入口文件
│   │   ├── api/index.ts        # API 调用封装
│   │   └── pages/              # 页面组件
│   │       ├── Login.tsx        # 登录/注册页
│   │       ├── Home.tsx         # 主页（表单提交）
│   │       ├── Coupon.tsx       # 抢优惠券
│   │       └── Query.tsx        # 查询页
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml          # Docker 编排配置
├── CLAUDE.md                    # Claude Code 指南
└── .github/workflows/ci.yml    # CI/CD 流水线
```

---

## 主要功能

### 1. 用户认证
- 用户注册（用户名 + 密码）
- 用户登录（JWT Token 认证）
- 登录状态保持（LocalStorage）

### 2. 测试表单
- 填写姓名、联系方式、备注
- 提交后存储到数据库
- 可在查询页面搜索历史提交

### 3. 抢优惠券
- 展示优惠券列表（含剩余数量）
- 点击抢券，后端原子操作扣减库存
- 防止重复抢券（每人每种券限一次）
- 实时显示抢券结果

### 4. 查询功能
- 按关键词搜索表单提交记录
- 按关键词搜索优惠券领取记录
- 表格形式展示结果

---

## 数据库表结构

| 表名 | 字段 | 说明 |
|------|------|------|
| users | id, username, password_hash, created_at | 用户表 |
| forms | id, user_id, name, contact, note, created_at | 表单提交记录 |
| coupons | id, name, total, remaining, created_at | 优惠券配置 |
| coupon_logs | id, user_id, coupon_id, grabbed_at | 领取日志 |

---

## API 文档

启动后端后访问：`http://localhost:8000/docs`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/auth/register | 注册用户 | 否 |
| POST | /api/auth/login | 登录获取 Token | 否 |
| GET | /api/auth/me | 获取当前用户信息 | 是 |
| POST | /api/form/submit | 提交表单 | 是 |
| GET | /api/form/list | 获取表单列表 | 是 |
| GET | /api/coupons/list | 获取优惠券列表 | 否 |
| POST | /api/coupons/grab | 抢优惠券 | 是 |
| GET | /api/coupons/my | 我的优惠券 | 是 |
| GET | /api/query/forms | 查询表单记录 | 是 |
| GET | /api/query/coupons | 查询优惠券记录 | 是 |

---

## 快速开始

### 本地开发

```bash
# 1. 启动后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2. 启动前端（新开终端）
cd frontend
npm install
npm run dev
```

访问 `http://localhost:3000`

### Docker 部署

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d

# 停止
docker-compose down
```

服务地址：
- 前端：http://localhost:3000
- 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## CI/CD 流水线

`.github/workflows/ci.yml` 定义了自动化流程：

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ test-backend │───▶│test-frontend│───▶│docker-build │
│  Python      │    │  npm build  │    │  push only  │
└─────────────┘    └─────────────┘    └─────────────┘
```

**触发条件**：
- Push 到 main 分支
- Pull Request 到 main 分支

**流水线步骤**：
1. **test-backend**：安装依赖，检查 Python 语法
2. **test-frontend**：安装依赖，执行 TypeScript 编译和构建
3. **docker-build**（仅 push）：构建 Docker 镜像，启动容器，健康检查

---

## 初始数据

系统启动时自动创建 3 张优惠券：

| 名称 | 总量 | 剩余 |
|------|------|------|
| 新人券 10元 | 100 | 100 |
| 满减券 20元 | 50 | 50 |
| VIP券 50元 | 20 | 20 |

---

## 扩展学习

1. **添加更多测试**：在 backend 添加 pytest 单元测试
2. **配置 GitHub Secrets**：存储 Docker Hub 凭证实现镜像推送
3. **多环境部署**：添加 staging/production 环境配置
4. **监控集成**：添加 Prometheus + Grafana 监控
5. **Kubernetes**：将 docker-compose 迁移到 K8s 配置