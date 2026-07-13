from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta, date
import hashlib
import jwt
from typing import Optional
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.models.models import User, Chart, Checkin, UserLog, SystemConfig, DailyFortune
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["管理后台"])

# 管理后台 HTML 页面
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>命里管理后台</title>
    <script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a1a;
            color: #e0e0f0;
            min-height: 100vh;
        }
        .login-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .login-box {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 40px;
            width: 400px;
        }
        .login-title {
            font-size: 24px;
            font-weight: 600;
            text-align: center;
            margin-bottom: 24px;
            color: #c9a050;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-label {
            display: block;
            font-size: 14px;
            color: #a0a0c0;
            margin-bottom: 8px;
        }
        .form-input {
            width: 100%;
            height: 44px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
            color: #e0e0f0;
        }
        .login-btn {
            width: 100%;
            height: 44px;
            background: linear-gradient(135deg, #c9a050, #a07830);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        .login-btn:hover {
            opacity: 0.9;
        }
        .error-msg {
            color: #f05050;
            font-size: 14px;
            text-align: center;
            margin-top: 16px;
        }

        /* Dashboard样式 */
        .dashboard {
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 240px;
            background: rgba(255, 255, 255, 0.05);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            padding: 24px 16px;
        }
        .sidebar-title {
            font-size: 20px;
            font-weight: 600;
            color: #c9a050;
            margin-bottom: 24px;
        }
        .sidebar-menu {
            list-style: none;
        }
        .sidebar-item {
            padding: 12px 16px;
            margin-bottom: 8px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .sidebar-item:hover {
            background: rgba(255, 255, 255, 0.08);
        }
        .sidebar-item.active {
            background: rgba(201, 160, 80, 0.2);
            color: #c9a050;
        }
        .main-content {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        .page-title {
            font-size: 24px;
            font-weight: 600;
        }
        .logout-btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            color: #e0e0f0;
            cursor: pointer;
        }

        /* 统计卡片 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
        }
        .stat-label {
            font-size: 14px;
            color: #a0a0c0;
        }
        .stat-value {
            font-size: 32px;
            font-weight: 600;
            color: #c9a050;
            margin-top: 8px;
        }
        .stat-change {
            font-size: 14px;
            color: #80c080;
            margin-top: 4px;
        }

        /* 图表区域 */
        .chart-section {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
        }
        .chart-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
        }
        .chart-container {
            height: 300px;
        }

        /* 用户列表 */
        .table-container {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
        }
        .table-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 16px;
        }
        .search-input {
            width: 200px;
            height: 36px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 8px 12px;
            color: #e0e0f0;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        .data-table th {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: #a0a0c0;
            font-size: 14px;
        }
        .data-table td {
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        .data-table tr:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        /* 配置页面 */
        .config-item {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .config-info {
            flex: 1;
        }
        .config-label {
            font-size: 16px;
            font-weight: 500;
        }
        .config-desc {
            font-size: 14px;
            color: #a0a0c0;
            margin-top: 4px;
        }
        .switch {
            width: 48px;
            height: 24px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            cursor: pointer;
            position: relative;
        }
        .switch.active {
            background: #c9a050;
        }
        .switch-dot {
            width: 20px;
            height: 20px;
            background: #fff;
            border-radius: 10px;
            position: absolute;
            top: 2px;
            left: 2px;
            transition: left 0.2s;
        }
        .switch.active .switch-dot {
            left: 26px;
        }

        .config-group {
            margin-bottom: 32px;
        }

        .config-group-title {
            font-size: 18px;
            font-weight: 600;
            color: #c9a050;
            margin-bottom: 16px;
            padding-left: 12px;
            border-left: 4px solid #c9a050;
        }

        .config-input {
            width: 280px;
            height: 36px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 6px;
            padding: 0 12px;
            font-size: 14px;
            color: #e0e0f0;
        }

        .config-input:focus {
            outline: none;
            border-color: #c9a050;
        }

        .config-input.number {
            width: 120px;
            text-align: right;
        }

        .config-select {
            width: 200px;
            height: 36px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 6px;
            padding: 0 12px;
            font-size: 14px;
            color: #e0e0f0;
        }

        .config-select:focus {
            outline: none;
            border-color: #c9a050;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #a0a0c0;
        }
    </style>
</head>
<body>
    <div id="app">
        <!-- 登录页面 -->
        <div v-if="!isLoggedIn" class="login-container">
            <div class="login-box">
                <div class="login-title">命里管理后台</div>
                <div class="form-group">
                    <label class="form-label">管理员账号</label>
                    <input class="form-input" v-model="loginForm.email" placeholder="admin@mingli.com">
                </div>
                <div class="form-group">
                    <label class="form-label">密码</label>
                    <input class="form-input" type="password" v-model="loginForm.password" placeholder="请输入密码">
                </div>
                <button class="login-btn" @click="handleLogin" :disabled="loginLoading">
                    {{ loginLoading ? '登录中...' : '登录' }}
                </button>
                <div v-if="loginError" class="error-msg">{{ loginError }}</div>
            </div>
        </div>

        <!-- Dashboard页面 -->
        <div v-else class="dashboard">
            <div class="sidebar">
                <div class="sidebar-title">命里后台</div>
                <ul class="sidebar-menu">
                    <li class="sidebar-item" :class="{active: currentPage === 'dashboard'}" @click="currentPage = 'dashboard'">
                        数据统计
                    </li>
                    <li class="sidebar-item" :class="{active: currentPage === 'users'}" @click="currentPage = 'users'">
                        用户管理
                    </li>
                    <li class="sidebar-item" :class="{active: currentPage === 'config'}" @click="currentPage = 'config'">
                        系统配置
                    </li>
                </ul>
            </div>

            <div class="main-content">
                <!-- 数据统计页 -->
                <div v-if="currentPage === 'dashboard'">
                    <div class="header">
                        <div class="page-title">数据统计</div>
                        <button class="logout-btn" @click="handleLogout">退出登录</button>
                    </div>

                    <div v-if="statsLoading" class="loading">加载中...</div>

                    <div v-else>
                        <!-- 统计卡片 -->
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-label">注册用户总数</div>
                                <div class="stat-value">{{ stats.users?.total || 0 }}</div>
                                <div class="stat-change">今日新增 {{ stats.users?.today_new || 0 }}</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">今日活跃用户</div>
                                <div class="stat-value">{{ stats.users?.active_today || 0 }}</div>
                                <div class="stat-change">本周活跃 {{ stats.users?.active_week || 0 }}</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">命盘总数</div>
                                <div class="stat-value">{{ stats.charts?.total || 0 }}</div>
                                <div class="stat-change">今日新增 {{ stats.charts?.today_new || 0 }}</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-label">今日签到</div>
                                <div class="stat-value">{{ stats.checkins?.today || 0 }}</div>
                                <div class="stat-change">运势查看 {{ stats.fortune?.today_views || 0 }}</div>
                            </div>
                        </div>

                        <!-- 用户增长图表 -->
                        <div class="chart-section">
                            <div class="chart-title">用户增长趋势（30天）</div>
                            <div class="chart-container">
                                <canvas id="userChart"></canvas>
                            </div>
                        </div>

                        <!-- 活跃度图表 -->
                        <div class="chart-section">
                            <div class="chart-title">活跃用户趋势（30天）</div>
                            <div class="chart-container">
                                <canvas id="activeChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 用户管理页 -->
                <div v-if="currentPage === 'users'">
                    <div class="header">
                        <div class="page-title">用户管理</div>
                        <button class="logout-btn" @click="handleLogout">退出登录</button>
                    </div>

                    <div class="table-container">
                        <div class="table-header">
                            <input class="search-input" v-model="userSearch" placeholder="搜索用户" @input="loadUsers">
                            <span>共 {{ userTotal }} 个用户</span>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>昵称</th>
                                    <th>手机</th>
                                    <th>命盘数</th>
                                    <th>签到天数</th>
                                    <th>最后活跃</th>
                                    <th>注册时间</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="u in userList" :key="u.id">
                                    <td>{{ u.id }}</td>
                                    <td>{{ u.nickname }}</td>
                                    <td>{{ u.phone || '-' }}</td>
                                    <td>{{ u.charts_count }}</td>
                                    <td>{{ u.checkin_total }}</td>
                                    <td>{{ u.last_active_at || '-' }}</td>
                                    <td>{{ u.created_at?.slice(0, 10) }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- 系统配置页 -->
                <div v-if="currentPage === 'config'">
                    <div class="header">
                        <div class="page-title">系统配置</div>
                        <button class="logout-btn" @click="handleLogout">退出登录</button>
                    </div>

                    <div v-if="configLoading" class="loading">加载中...</div>

                    <template v-else>
                        <div v-for="(items, groupName) in configGroups" :key="groupName" class="config-group">
                            <div class="config-group-title">{{ groupName }}</div>
                            
                            <div v-for="item in items" :key="item.key" class="config-item">
                                <div class="config-info">
                                    <div class="config-label">{{ item.label }}</div>
                                    <div class="config-desc">{{ item.description }}</div>
                                </div>
                                
                                <!-- 开关类型 -->
                                <div v-if="item.type === 'switch'" 
                                     class="switch" 
                                     :class="{active: item.value === 'true'}" 
                                     @click="toggleConfig(item.key)">
                                    <div class="switch-dot"></div>
                                </div>
                                
                                <!-- 文本输入类型 -->
                                <input v-else-if="item.type === 'text'" 
                                       class="config-input" 
                                       :value="item.value" 
                                       @blur="updateConfigValue(item.key, $event.target.value)"
                                       @keyup.enter="updateConfigValue(item.key, $event.target.value)"
                                       :placeholder="item.description">
                                
                                <!-- 数字输入类型 -->
                                <input v-else-if="item.type === 'number'" 
                                       class="config-input number" 
                                       type="number"
                                       :value="item.value" 
                                       @blur="updateConfigValue(item.key, $event.target.value)"
                                       placeholder="请输入数字">
                                
                                <!-- 下拉选择类型 -->
                                <select v-else-if="item.type === 'select'" 
                                        class="config-select" 
                                        :value="item.value"
                                        @change="updateConfigValue(item.key, $event.target.value)">
                                    <option v-for="opt in item.options" :key="opt.value" :value="opt.value">
                                        {{ opt.label }}
                                    </option>
                                </select>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
        </div>
    </div>

    <script>
        const { createApp, ref, onMounted, watch } = Vue;

        // 自动检测API地址：同源则用相对路径，否则用线上地址
        const API_BASE = window.location.hostname === 'localhost' 
            ? 'http://127.0.0.1:8000/api/v1' 
            : window.location.origin + '/api/v1';

        createApp({
            setup() {
                const isLoggedIn = ref(false);
                const token = ref(localStorage.getItem('admin_token') || '');
                const loginForm = ref({ email: '', password: '' });
                const loginLoading = ref(false);
                const loginError = ref('');

                const currentPage = ref('dashboard');
                const stats = ref({});
                const statsLoading = ref(false);

                const userList = ref([]);
                const userTotal = ref(0);
                const userSearch = ref('');

                const config = ref({});
                const configGroups = ref({});
                const configLoading = ref(false);

                // 检查登录状态
                if (token.value) {
                    isLoggedIn.value = true;
                    loadStats();
                    loadConfig();
                }

                // 登录
                async function handleLogin() {
                    loginLoading.value = true;
                    loginError.value = '';
                    try {
                        const res = await fetch(`${API_BASE}/admin/auth/login`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(loginForm.value)
                        });
                        const data = await res.json();
                        if (res.ok) {
                            token.value = data.token;
                            localStorage.setItem('admin_token', data.token);
                            isLoggedIn.value = true;
                            loadStats();
                            loadConfig();
                        } else {
                            loginError.value = data.detail || '登录失败';
                        }
                    } catch (e) {
                        loginError.value = '网络错误';
                    }
                    loginLoading.value = false;
                }

                // 退出登录
                function handleLogout() {
                    localStorage.removeItem('admin_token');
                    token.value = '';
                    isLoggedIn.value = false;
                }

                // 加载统计数据
                async function loadStats() {
                    statsLoading.value = true;
                    try {
                        const res = await fetch(`${API_BASE}/admin/stats/dashboard`, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        if (res.ok) {
                            stats.value = await res.json();
                            renderCharts();
                        }
                    } catch (e) {
                        console.error('加载统计失败', e);
                    }
                    statsLoading.value = false;
                }

                // 加载用户列表
                async function loadUsers() {
                    try {
                        const url = `${API_BASE}/admin/users?page=1&limit=20${userSearch.value ? '&search=' + userSearch.value : ''}`;
                        const res = await fetch(url, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        if (res.ok) {
                            const data = await res.json();
                            userList.value = data.users;
                            userTotal.value = data.total;
                        }
                    } catch (e) {
                        console.error('加载用户失败', e);
                    }
                }

                // 加载配置
                async function loadConfig() {
                    configLoading.value = true;
                    try {
                        const res = await fetch(`${API_BASE}/admin/config`, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        if (res.ok) {
                            const data = await res.json();
                            // 扁平数据
                            config.value = {};
                            if (data.flat) {
                                for (const [k, v] of Object.entries(data.flat)) {
                                    config.value[k] = v.value;
                                }
                            }
                            // 分组数据
                            configGroups.value = data.groups || {};
                        }
                    } catch (e) {
                        console.error('加载配置失败', e);
                    }
                    configLoading.value = false;
                }

                // 切换开关配置
                async function toggleConfig(key) {
                    const newValue = config.value[key] === 'true' ? 'false' : 'true';
                    try {
                        const res = await fetch(`${API_BASE}/admin/config`, {
                            method: 'PUT',
                            headers: {
                                'Authorization': `Bearer ${token.value}`,
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ configs: { [key]: newValue } })
                        });
                        if (res.ok) {
                            config.value[key] = newValue;
                            // 更新分组数据中的值
                            for (const groupName in configGroups.value) {
                                const item = configGroups.value[groupName].find(i => i.key === key);
                                if (item) {
                                    item.value = newValue;
                                    break;
                                }
                            }
                        }
                    } catch (e) {
                        console.error('更新配置失败', e);
                    }
                }

                // 更新配置值（通用）
                async function updateConfigValue(key, value) {
                    try {
                        const res = await fetch(`${API_BASE}/admin/config`, {
                            method: 'PUT',
                            headers: {
                                'Authorization': `Bearer ${token.value}`,
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ configs: { [key]: value } })
                        });
                        if (res.ok) {
                            config.value[key] = value;
                            // 更新分组数据中的值
                            for (const groupName in configGroups.value) {
                                const item = configGroups.value[groupName].find(i => i.key === key);
                                if (item) {
                                    item.value = value;
                                    break;
                                }
                            }
                        }
                    } catch (e) {
                        console.error('更新配置失败', e);
                    }
                }

                // 渲染图表
                function renderCharts() {
                    // 用户增长图表
                    const userCtx = document.getElementById('userChart');
                    if (userCtx && stats.value.trends?.users_30d) {
                        new Chart(userCtx, {
                            type: 'line',
                            data: {
                                labels: stats.value.trends.users_30d.map(d => d.date.slice(5)),
                                datasets: [{
                                    label: '新增用户',
                                    data: stats.value.trends.users_30d.map(d => d.count),
                                    borderColor: '#c9a050',
                                    tension: 0.3
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: { legend: { display: false } },
                                scales: {
                                    x: { grid: { color: 'rgba(255,255,255,0.1)' } },
                                    y: { grid: { color: 'rgba(255,255,255,0.1)' } }
                                }
                            }
                        });
                    }

                    // 活跃度图表
                    const activeCtx = document.getElementById('activeChart');
                    if (activeCtx && stats.value.trends?.active_30d) {
                        new Chart(activeCtx, {
                            type: 'bar',
                            data: {
                                labels: stats.value.trends.active_30d.map(d => d.date.slice(5)),
                                datasets: [{
                                    label: '活跃用户',
                                    data: stats.value.trends.active_30d.map(d => d.count),
                                    backgroundColor: '#c9a050',
                                    borderRadius: 4
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: { legend: { display: false } },
                                scales: {
                                    x: { grid: { color: 'rgba(255,255,255,0.1)' } },
                                    y: { grid: { color: 'rgba(255,255,255,0.1)' } }
                                }
                            }
                        });
                    }
                }

                // 监听页面切换
                watch(currentPage, (page) => {
                    if (page === 'users') {
                        loadUsers();
                    }
                });

                return {
                    isLoggedIn, loginForm, loginLoading, loginError,
                    handleLogin, handleLogout,
                    currentPage, stats, statsLoading,
                    userList, userTotal, userSearch, loadUsers,
                    config, configGroups, configLoading,
                    toggleConfig, updateConfigValue
                };
            }
        }).mount('#app');
    </script>
</body>
</html>
"""


@router.get("", response_class=HTMLResponse)
def admin_page():
    """管理后台页面"""
    return ADMIN_HTML

# JWT密钥
SECRET_KEY = "mingli_admin_secret_key_2024"
ALGORITHM = "HS256"


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class ConfigUpdateRequest(BaseModel):
    configs: dict


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def create_admin_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "is_admin": True,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_admin_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    """验证管理员身份"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少认证信息")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的token")
    
    user = db.query(User).filter(User.id == user_id, User.is_admin == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="非管理员用户")
    return user


@router.post("/auth/login")
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    # 查找管理员用户
    admin = db.query(User).filter(
        User.is_admin == True,
        or_(User.email == req.email, User.phone == req.email)
    ).first()
    
    if not admin:
        raise HTTPException(status_code=401, detail="管理员账号不存在")
    
    # 验证密码
    if not admin.password_hash:
        raise HTTPException(status_code=401, detail="管理员账号未设置密码")
    
    if not verify_password(req.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 更新登录计数
    admin.login_count += 1
    admin.last_active_at = datetime.utcnow()
    db.commit()
    
    # 记录登录日志
    log = UserLog(user_id=admin.id, action="admin_login", detail={"email": req.email})
    db.add(log)
    db.commit()
    
    # 生成token
    token = create_admin_token(admin.id)
    
    return {
        "token": token,
        "user": {
            "id": admin.id,
            "nickname": admin.nickname,
            "email": admin.email,
            "is_admin": admin.is_admin
        }
    }


@router.get("/stats/dashboard")
def get_dashboard_stats(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """获取Dashboard统计数据"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=7)
    month_start = today - timedelta(days=30)
    
    # 用户统计
    total_users = db.query(func.count(User.id)).scalar()
    today_new_users = db.query(func.count(User.id)).filter(
        func.date(User.created_at) == today
    ).scalar()
    
    # 活跃用户统计
    active_today = db.query(func.count(User.id)).filter(
        func.date(User.last_active_at) == today
    ).scalar()
    active_week = db.query(func.count(User.id)).filter(
        User.last_active_at >= week_start
    ).scalar()
    
    # 命盘统计
    total_charts = db.query(func.count(Chart.id)).scalar()
    today_new_charts = db.query(func.count(Chart.id)).filter(
        func.date(Chart.created_at) == today
    ).scalar()
    
    # 签到统计
    today_checkins = db.query(func.count(Checkin.id)).filter(
        Checkin.checkin_date == today
    ).scalar()
    
    # 运势查看统计
    today_fortune_views = db.query(func.count(UserLog.id)).filter(
        UserLog.action == "fortune_view",
        func.date(UserLog.created_at) == today
    ).scalar()
    
    # 用户行为统计（今日）
    action_stats = db.query(
        UserLog.action,
        func.count(UserLog.id)
    ).filter(
        func.date(UserLog.created_at) == today
    ).group_by(UserLog.action).all()
    
    action_counts = {a: c for a, c in action_stats}
    
    # 过去30天用户增长趋势
    user_trend = []
    for i in range(30):
        d = today - timedelta(days=i)
        count = db.query(func.count(User.id)).filter(
            func.date(User.created_at) == d
        ).scalar()
        user_trend.append({"date": str(d), "count": count})
    
    # 过去30天活跃趋势
    active_trend = []
    for i in range(30):
        d = today - timedelta(days=i)
        count = db.query(func.count(User.id)).filter(
            func.date(User.last_active_at) == d
        ).scalar()
        active_trend.append({"date": str(d), "count": count})
    
    return {
        "users": {
            "total": total_users,
            "today_new": today_new_users,
            "active_today": active_today,
            "active_week": active_week
        },
        "charts": {
            "total": total_charts,
            "today_new": today_new_charts
        },
        "checkins": {
            "today": today_checkins
        },
        "fortune": {
            "today_views": today_fortune_views
        },
        "actions": action_counts,
        "trends": {
            "users_30d": user_trend,
            "active_30d": active_trend
        }
    }


@router.get("/users")
def get_user_list(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.nickname.contains(search),
                User.phone.contains(search),
                User.email.contains(search)
            )
        )
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "nickname": u.nickname,
                "phone": u.phone,
                "email": u.email,
                "is_admin": u.is_admin,
                "checkin_days": u.checkin_days,
                "checkin_total": u.checkin_total,
                "charts_count": len(u.charts) if u.charts else 0,
                "last_active_at": str(u.last_active_at) if u.last_active_at else None,
                "created_at": str(u.created_at)
            }
            for u in users
        ]
    }


@router.get("/config")
def get_config(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """获取系统配置"""
    configs = db.query(SystemConfig).all()
    
    # 配置分组和类型定义
    config_meta = {
        # 广告配置
        "enable_ads": {"group": "广告配置", "type": "switch", "label": "开启广告"},
        "ad_banner_unit_id": {"group": "广告配置", "type": "text", "label": "Banner广告位ID"},
        "ad_reward_unit_id": {"group": "广告配置", "type": "text", "label": "激励视频广告位ID"},
        "ad_interstitial_unit_id": {"group": "广告配置", "type": "text", "label": "插屏广告位ID"},
        "ad_frequency_limit": {"group": "广告配置", "type": "number", "label": "每日广告次数限制"},
        
        # VIP配置
        "enable_vip": {"group": "VIP配置", "type": "switch", "label": "开启VIP功能"},
        "vip_month_price": {"group": "VIP配置", "type": "number", "label": "VIP月卡价格(元)"},
        "vip_year_price": {"group": "VIP配置", "type": "number", "label": "VIP年卡价格(元)"},
        "vip_svip_year_price": {"group": "VIP配置", "type": "number", "label": "SVIP年卡价格(元)"},
        "vip_free_days": {"group": "VIP配置", "type": "number", "label": "新用户免费体验天数"},
        
        # AI配置
        "ai_daily_limit_free": {"group": "AI配置", "type": "number", "label": "免费用户每日AI次数"},
        "ai_daily_limit_vip": {"group": "VIP配置", "type": "number", "label": "VIP用户每日AI次数"},
        "ai_provider": {"group": "AI配置", "type": "select", "label": "AI服务提供商", 
                        "options": [{"label": "模拟(Mock)", "value": "mock"}, 
                                    {"label": "OpenAI", "value": "openai"},
                                    {"label": "火山引擎", "value": "volcengine"}]},
        
        # 运势配置
        "fortune_enable": {"group": "运势配置", "type": "switch", "label": "开启每日运势"},
        "fortune_enable_share": {"group": "运势配置", "type": "switch", "label": "开启运势分享"},
        
        # 运营配置
        "app_name": {"group": "运营配置", "type": "text", "label": "小程序名称"},
        "home_banner_title": {"group": "运营配置", "type": "text", "label": "首页Banner标题"},
        "home_banner_subtitle": {"group": "运营配置", "type": "text", "label": "首页Banner副标题"},
        "customer_service": {"group": "运营配置", "type": "text", "label": "客服联系方式"},
        "user_agreement_url": {"group": "运营配置", "type": "text", "label": "用户协议链接"},
        "privacy_policy_url": {"group": "运营配置", "type": "text", "label": "隐私政策链接"},
        
        # 功能开关
        "enable_match": {"group": "功能开关", "type": "switch", "label": "双人匹配功能"},
        "enable_share": {"group": "功能开关", "type": "switch", "label": "分享功能"},
        "enable_checkin": {"group": "功能开关", "type": "switch", "label": "签到功能"},
    }
    
    # 按分组组织
    groups = {}
    for c in configs:
        meta = config_meta.get(c.key, {"group": "其他", "type": "text", "label": c.key})
        group_name = meta["group"]
        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append({
            "key": c.key,
            "value": c.value,
            "description": c.description,
            "type": meta.get("type", "text"),
            "label": meta.get("label", c.key),
            "options": meta.get("options")
        })
    
    return {
        "groups": groups,
        "flat": {c.key: {"value": c.value, "description": c.description} for c in configs}
    }


@router.put("/config")
def update_config(
    req: ConfigUpdateRequest,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """更新系统配置"""
    for key, value in req.configs.items():
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            config.value = str(value)
        else:
            config = SystemConfig(key=key, value=str(value))
            db.add(config)
    db.commit()
    return {"success": True}


@router.post("/init-admin")
def init_admin_account(db: Session = Depends(get_db)):
    """初始化管理员账号（仅第一次使用）"""
    # 检查是否已存在管理员
    existing = db.query(User).filter(User.is_admin == True).first()
    if existing:
        raise HTTPException(status_code=400, detail="管理员账号已存在")
    
    # 创建管理员账号
    admin = User(
        nickname="管理员",
        email="admin@mingli.com",
        password_hash=hash_password("admin123"),  # 默认密码
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # 初始化系统配置
    _init_default_configs(db)
    
    return {
        "success": True,
        "admin": {
            "id": admin.id,
            "email": admin.email,
            "default_password": "admin123"
        },
        "message": "管理员账号已创建，请及时修改密码"
    }


@router.post("/sync-configs")
def sync_default_configs(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """同步默认配置（补充缺失的配置项）"""
    added_count = _init_default_configs(db)
    return {"success": True, "added_count": added_count}


def _init_default_configs(db: Session) -> int:
    """初始化默认配置，返回新增的配置数量"""
    default_configs = [
        # 广告配置
        SystemConfig(key="enable_ads", value="false", description="是否开启广告"),
        SystemConfig(key="ad_banner_unit_id", value="", description="Banner广告位ID"),
        SystemConfig(key="ad_reward_unit_id", value="", description="激励视频广告位ID"),
        SystemConfig(key="ad_interstitial_unit_id", value="", description="插屏广告位ID"),
        SystemConfig(key="ad_frequency_limit", value="10", description="广告每日展示次数限制(次)"),
        
        # VIP配置
        SystemConfig(key="enable_vip", value="false", description="是否开启VIP功能"),
        SystemConfig(key="vip_month_price", value="19.9", description="VIP月卡价格(元)"),
        SystemConfig(key="vip_year_price", value="99", description="VIP年卡价格(元)"),
        SystemConfig(key="vip_svip_year_price", value="199", description="SVIP年卡价格(元)"),
        SystemConfig(key="vip_free_days", value="7", description="新用户VIP免费体验天数"),
        
        # AI配置
        SystemConfig(key="ai_daily_limit_free", value="3", description="免费用户每日AI解读次数"),
        SystemConfig(key="ai_daily_limit_vip", value="99", description="VIP用户每日AI解读次数"),
        SystemConfig(key="ai_provider", value="mock", description="AI服务提供商(mock/openai/volcengine)"),
        
        # 运势配置
        SystemConfig(key="fortune_enable", value="true", description="是否开启每日运势功能"),
        SystemConfig(key="fortune_enable_share", value="true", description="是否开启运势分享"),
        
        # 运营配置
        SystemConfig(key="app_name", value="命里", description="小程序名称"),
        SystemConfig(key="home_banner_title", value="探索你的命理奥秘", description="首页Banner标题"),
        SystemConfig(key="home_banner_subtitle", value="紫微斗数 · 八字排盘 · AI解读", description="首页Banner副标题"),
        SystemConfig(key="customer_service", value="", description="客服联系方式"),
        SystemConfig(key="user_agreement_url", value="", description="用户协议链接"),
        SystemConfig(key="privacy_policy_url", value="", description="隐私政策链接"),
        
        # 功能开关
        SystemConfig(key="enable_match", value="true", description="是否开启双人匹配"),
        SystemConfig(key="enable_share", value="true", description="是否开启分享功能"),
        SystemConfig(key="enable_checkin", value="true", description="是否开启签到功能"),
    ]
    
    added = 0
    for config in default_configs:
        existing = db.query(SystemConfig).filter(SystemConfig.key == config.key).first()
        if not existing:
            db.add(config)
            added += 1
    db.commit()
    return added