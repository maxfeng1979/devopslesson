# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

一个用于学习 CI/CD 的前后端示例项目。

**技术栈**：
- 后端：FastAPI (Python)
- 前端：React + Vite + TypeScript
- 数据库：SQLite
- 部署：Docker Compose

## 目录结构

```
devopslesson/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── main.py      # FastAPI 入口
│   │   ├── database.py  # SQLite 连接和初始化
│   │   ├── models.py    # Pydantic 模型
│   │   ├── auth.py      # JWT 认证
│   │   └── routers/     # API 路由
│   │       ├── auth.py  # 登录/注册
│   │       ├── form.py  # 表单提交
│   │       ├── coupon.py # 抢优惠券
│   │       └── query.py  # 查询
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             # React 前端
│   ├── src/
│   │   ├── App.tsx      # 路由配置
│   │   ├── pages/       # 页面组件
│   │   │   ├── Login.tsx
│   │   │   ├── Home.tsx
│   │   │   ├── Coupon.tsx
│   │   │   └── Query.tsx
│   │   └── api/         # API 调用封装
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml  # CI/CD 流水线
```

## 常用命令

### 后端开发
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# API 文档: http://localhost:8000/docs
```

### 前端开发
```bash
cd frontend
npm install
npm run dev  # 启动开发服务器 (port 3000)
npm run build  # 构建生产版本
```

### Docker
```bash
docker-compose up --build  # 构建并启动
docker-compose down       # 停止
docker-compose up -d       # 后台运行
```

## 数据库表结构

- **users**: id, username, password_hash, created_at
- **forms**: id, user_id, name, contact, note, created_at
- **coupons**: id, name, total, remaining, created_at
- **coupon_logs**: id, user_id, coupon_id, grabbed_at

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录，返回 JWT |
| GET | /api/auth/me | 获取当前用户 |
| POST | /api/form/submit | 提交表单 |
| GET | /api/form/list | 表单列表 |
| GET | /api/coupons/list | 优惠券列表 |
| POST | /api/coupons/grab | 抢优惠券 |
| GET | /api/coupons/my | 我的优惠券 |
| GET | /api/query/forms | 查询表单记录 |
| GET | /api/query/coupons | 查询优惠券记录 |

## CI/CD 流水线

GitHub Actions 配置在 `.github/workflows/ci.yml`：
1. 测试后端（Python 导入检查）
2. 测试前端（npm build）
3. Docker 构建和集成测试（仅 push 到 main 时）