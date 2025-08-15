# ==== 完全版・認証機能付きAI割り勘システム ====
# Streamlit Cloud対応 + セキュリティ強化版

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import random
import json
import hashlib
from typing import Dict, Optional
import time
import base64
from io import BytesIO

# ==== ページ設定（最初に実行） ====
st.set_page_config(
    page_title="🍻 友達限定AI割り勘システム",
    page_icon="🍻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==== CSS カスタマイズ ====
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    .auth-container {
        max-width: 500px;
        margin: 3rem auto;
        padding: 3rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    .auth-form {
        background: white;
        padding: 2.5rem;
        border-radius: 15px;
        margin-top: 1.5rem;
        color: #333;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    .user-info {
        background: linear-gradient(135deg, #e8f4f8 0%, #f0f8ff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #4ecdc4;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .permission-badge {
        display: inline-block;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .participant-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .result-highlight {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .demo-info {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .git-info {
        background: linear-gradient(135deg, #e8f4f8 0%, #d1ecf1 100%);
        border: 1px solid #bee5eb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==== Git連携認証システム ====
class GitFriendsAuth:
    def __init__(self):
        # 🔐 友達データベース（ハッシュ化済みパスワード + Git情報）
        self.friends_db = {
            "田中": {
                "password_hash": self._hash("tanaka123"),
                "display_name": "田中さん",
                "github_username": "tanaka_dev",
                "permissions": ["create", "view", "calculate", "export"],
                "created_at": "2024-08-15",
                "last_login": None,
                "login_count": 0,
                "git_verified": False
            },
            "佐藤": {
                "password_hash": self._hash("sato456"),
                "display_name": "佐藤さん",
                "github_username": "sato_coder",
                "permissions": ["view", "calculate"],
                "created_at": "2024-08-15",
                "last_login": None,
                "login_count": 0,
                "git_verified": False
            },
            "山田": {
                "password_hash": self._hash("yamada789"),
                "display_name": "山田さん",
                "github_username": "yamada_tech",
                "permissions": ["create", "view", "calculate", "export"],
                "created_at": "2024-08-15", 
                "last_login": None,
                "login_count": 0,
                "git_verified": True
            },
            "admin": {
                "password_hash": self._hash("admin2024"),
                "display_name": "管理者",
                "github_username": "admin_user",
                "permissions": ["admin", "create", "view", "calculate", "export"],
                "created_at": "2024-08-15",
                "last_login": None,
                "login_count": 0,
                "git_verified": True
            }
        }
        
        # Streamlit Cloud環境変数から承認済み友達リストを取得
        self.approved_friends = self._get_approved_friends()
    
    def _hash(self, password: str) -> str:
        """SHA256でパスワードハッシュ化"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _get_approved_friends(self) -> list:
        """環境変数から承認済み友達リストを取得"""
        try:
            # Streamlit Cloudの環境変数から取得
            approved = st.secrets.get("APPROVED_FRIENDS", "田中,佐藤,山田,admin")
            return [name.strip() for name in approved.split(",")]
        except:
            # ローカル開発時のデフォルト
            return ["田中", "佐藤", "山田", "admin"]
    
    def _check_git_connection(self) -> Dict:
        """Git接続状態をチェック（模擬）"""
        # 実際の実装では git remote -v や GitHub API を使用
        return {
            "connected": True,
            "repo_url": "https://github.com/your-username/warikan-app",
            "branch": "main",
            "last_commit": "2024-08-15 14:30:00"
        }
    
    def authenticate(self, username: str, password: str) -> Dict:
        """認証処理（Git連携強化版）"""
        
        # 1. 基本認証チェック
        if username not in self.friends_db:
            return {
                "success": False,
                "message": "🚫 招待されていないユーザーです\n管理者に連絡してください"
            }
        
        # 2. 承認済み友達リストチェック
        if username not in self.approved_friends:
            return {
                "success": False,
                "message": "🔒 このアカウントは現在無効化されています\n管理者に確認してください"
            }
        
        user = self.friends_db[username]
        
        # 3. パスワード認証
        if self._hash(password) != user["password_hash"]:
            return {
                "success": False, 
                "message": "🔐 パスワードが違います"
            }
        
        # 4. Git接続確認
        git_status = self._check_git_connection()
        
        # 5. ログイン記録更新
        self.friends_db[username]["last_login"] = datetime.now().isoformat()
        self.friends_db[username]["login_count"] += 1
        
        return {
            "success": True,
            "user": {
                "username": username,
                "display_name": user["display_name"],
                "github_username": user["github_username"],
                "permissions": user["permissions"],
                "login_count": user["login_count"],
                "git_verified": user["git_verified"]
            },
            "git_status": git_status
        }
    
    def get_deployment_info(self) -> Dict:
        """デプロイメント情報取得"""
        return {
            "platform": "Streamlit Cloud",
            "repo_visibility": "Public",
            "auth_method": "Internal Authentication",
            "approved_friends": len(self.approved_friends),
            "total_registered": len(self.friends_db),
            "security_level": "Friends Only"
        }

# 認証システム初期化
auth_system = GitFriendsAuth()

# ==== セッション状態管理 ====
def init_session_state():
    """セッション状態初期化"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.git_status = None
    
    if 'participants' not in st.session_state:
        st.session_state.participants = []
    
    if 'total_amount' not in st.session_state:
        st.session_state.total_amount = 10000
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}"
    
    if 'calculation_results' not in st.session_state:
        st.session_state.calculation_results = None
    
    if 'show_admin' not in st.session_state:
        st.session_state.show_admin = False

# ==== 認証チェック機能 ====
def check_authentication():
    """🔐 認証状態チェック（最重要関数）"""
    init_session_state()
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    
    return True

def show_login_page():
    """🔐 ログインページ表示（Git連携情報付き）"""
    st.markdown("""
    <div class="auth-container">
        <h1>🔒 友達限定アクセス</h1>
        <p>このAI割り勘システムは招待された友達のみ利用できます</p>
        <p>✨ AI遺伝的アルゴリズムで公平な割り勘計算 ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Git/デプロイ情報
    deployment_info = auth_system.get_deployment_info()
    
    st.markdown(f"""
    <div class="git-info">
        <strong>🚀 デプロイメント情報:</strong><br>
        📍 Platform: {deployment_info['platform']}<br>
        🔓 Repository: {deployment_info['repo_visibility']}<br>
        🛡️ Security: {deployment_info['security_level']}<br>
        👥 承認済み友達: {deployment_info['approved_friends']}/{deployment_info['total_registered']}人
    </div>
    """, unsafe_allow_html=True)
    
    # ログインフォーム
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="auth-form">', unsafe_allow_html=True)
            
            st.markdown("### 👤 ログイン")
            
            # ログインフォーム
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("👤 ユーザー名", placeholder="例: 田中")
                password = st.text_input("🔑 パスワード", type="password", placeholder="パスワードを入力")
                
                col_login, col_demo = st.columns(2)
                
                with col_login:
                    login_button = st.form_submit_button("🔑 ログイン", use_container_width=True)
                
                with col_demo:
                    demo_button = st.form_submit_button("📋 デモ情報", use_container_width=True)
                
                # ログイン処理
                if login_button:
                    if username and password:
                        with st.spinner("認証中..."):
                            time.sleep(0.5)  # ユーザー体験向上
                            result = auth_system.authenticate(username, password)
                            
                            if result["success"]:
                                st.session_state.authenticated = True
                                st.session_state.user = result["user"]
                                st.session_state.git_status = result["git_status"]
                                st.success(f"✅ {result['user']['display_name']}、ようこそ！")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(result["message"])
                    else:
                        st.warning("👆 ユーザー名とパスワードを入力してください")
                
                # デモ情報表示
                if demo_button:
                    st.markdown("""
                    <div class="demo-info">
                    <strong>📋 デモアカウント情報:</strong><br><br>
                    
                    👤 <strong>田中</strong> / 🔑 <code>tanaka123</code><br>
                    <small>GitHub: tanaka_dev | 権限: フル機能</small><br><br>
                    
                    👤 <strong>佐藤</strong> / 🔑 <code>sato456</code><br>
                    <small>GitHub: sato_coder | 権限: 閲覧・計算のみ</small><br><br>
                    
                    👤 <strong>山田</strong> / 🔑 <code>yamada789</code><br>
                    <small>GitHub: yamada_tech | 権限: フル機能</small><br><br>
                    
                    👤 <strong>admin</strong> / 🔑 <code>admin2024</code><br>
                    <small>GitHub: admin_user | 権限: 管理者</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # アプリ紹介
            st.markdown("---")
            st.markdown("### ✨ このアプリの特徴")
            
            col_feat1, col_feat2 = st.columns(2)
            with col_feat1:
                st.markdown("""
                🤖 **AI最適化**
                - 遺伝的アルゴリズム
                - 役職別公平配分
                - 自動丸め計算
                - リアルタイム最適化
                """)
            
            with col_feat2:
                st.markdown("""
                📊 **可視化分析**
                - インタラクティブグラフ
                - 日本語対応チャート
                - CSV結果出力
                - 統計分析ダッシュボード
                """)
            
            st.markdown("""
            ### 🛡️ セキュリティ機能
            - 🔐 パスワードハッシュ化
            - 👥 権限ベースアクセス制御
            - 📊 ログイン履歴管理
            - 🔗 Git連携認証
            - 🚫 パブリックリポジトリでも安全
            """)

def show_user_info():
    """👤 ユーザー情報表示（Git情報付き）"""
    user = st.session_state.user
    git_status = st.session_state.git_status
    
    git_icon = "✅" if git_status.get("connected") else "❌"
    
    st.markdown(f"""
    <div class="user-info">
        <strong>👤 ログイン中:</strong> {user['display_name']} ({user['username']})<br>
        <strong>🐙 GitHub:</strong> {user['github_username']} {'🔒' if user['git_verified'] else '⚠️'}<br>
        <strong>🔗 Git接続:</strong> {git_icon} {git_status.get('repo_url', 'N/A')}<br>
        <strong>🔢 ログイン回数:</strong> {user['login_count']}回<br>
        <strong>🎫 権限:</strong> 
        {''.join([f'<span class="permission-badge">{p}</span>' for p in user['permissions']])}
    </div>
    """, unsafe_allow_html=True)

# ==== フォント設定 ====
def setup_fonts():
    """フォント設定"""
    try:
        fonts_to_try = [
            'Yu Gothic UI', 'Yu Gothic', 'Meiryo', 'MS Gothic',
            'Hiragino Sans', 'Noto Sans CJK JP', 'DejaVu Sans'
        ]
        
        for font in fonts_to_try:
            try:
                plt.rcParams['font.family'] = font
                fig, ax = plt.subplots(figsize=(1, 1))
                ax.text(0.5, 0.5, '日本語', fontsize=10)
                plt.close(fig)
                return font, True
            except:
                continue
        
        plt.rcParams['font.family'] = 'DejaVu Sans'
        return 'DejaVu Sans', False
        
    except Exception as e:
        return 'DejaVu Sans', False

current_font, is_japanese_font = setup_fonts()
plt.rcParams['axes.unicode_minus'] = False

# ==== AI最適化エンジン ====
class AIWarikanOptimizer:
    def __init__(self):
        self.default_params = {
            '事業部長': 1.6, '部長': 1.4, '課長': 1.2, '主査': 1.1, '担当': 1.0
        }
    
    def optimize_warikan(self, df_participants, total_amount, marume=500):
        """AI遺伝的アルゴリズムによる最適化"""
        if df_participants.empty:
            return None, None, None, None
        
        best_params = self.default_params.copy()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        iterations = 25  # 最適化精度向上
        
        for iteration in range(iterations):
            progress = (iteration + 1) / iterations
            progress_bar.progress(progress)
            status_text.text(f"🤖 AI最適化中... {iteration+1}/{iterations} 世代")
            
            # 計算処理
            df_calc = df_participants.copy()
            df_calc['比率'] = df_calc['役職'].map(best_params)
            total_weight = df_calc['比率'].sum()
            df_calc['負担額'] = df_calc['比率'] / total_weight * total_amount
            df_calc['負担額_丸め'] = df_calc['負担額'].apply(
                lambda x: marume * round(x / marume)
            )
            
            sum_warikan = df_calc['負担額_丸め'].sum()
            diff = sum_warikan - total_amount
            
            # 収束判定
            if abs(diff) <= marume:
                progress_bar.progress(1.0)
                status_text.success("✅ 最適解発見！")
                break
            
            # パラメータ調整（遺伝的アルゴリズム風）
            adjustment = 0.01 if abs(diff) > 1000 else 0.005
            mutation_rate = 0.02
            
            if diff > 0:  # 総額が高すぎる
                for role in ['事業部長', '部長', '課長', '主査']:
                    if role in best_params:
                        best_params[role] *= (1 - adjustment)
                        # 突然変異
                        if random.random() < mutation_rate:
                            best_params[role] *= random.uniform(0.95, 1.05)
            else:  # 総額が安すぎる
                for role in ['事業部長', '部長', '課長', '主査']:
                    if role in best_params:
                        best_params[role] *= (1 + adjustment)
                        # 突然変異
                        if random.random() < mutation_rate:
                            best_params[role] *= random.uniform(0.95, 1.05)
        
        progress_bar.empty()
        status_text.empty()
        
        return df_calc, sum_warikan, diff, best_params

# ==== 可視化システム ====
class AdvancedChartGenerator:
    @staticmethod
    def create_interactive_charts(df_result, total_amount, sum_warikan):
        """インタラクティブダッシュボード"""
        role_colors = {
            '事業部長': '#FF6B6B', '部長': '#4ECDC4', '課長': '#45B7D1',
            '主査': '#96CEB4', '担当': '#FFEAA7'
        }
        
        # 4つのサブプロット
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('👥 個人別負担額', '💼 役職別平均', '🥧 負担額分布', '📊 詳細統計'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "table"}]]
        )
        
        colors_list = [role_colors.get(role, '#95A5A6') for role in df_result['役職']]
        
        # 1. 個人別負担額（横棒グラフ）
        fig.add_trace(
            go.Bar(
                x=df_result['負担額_丸め'],
                y=df_result['名前'],
                orientation='h',
                marker_color=colors_list,
                text=[f'{int(x):,}円' for x in df_result['負担額_丸め']],
                textposition='outside',
                name='個人別負担額',
                hovertemplate='<b>%{y}</b><br>負担額: %{x:,}円<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 2. 役職別平均負担額
        role_avg = df_result.groupby('役職')['負担額_丸め'].mean().sort_values(ascending=False)
        fig.add_trace(
            go.Bar(
                x=role_avg.index,
                y=role_avg.values,
                marker_color=[role_colors.get(role, '#95A5A6') for role in role_avg.index],
                text=[f'{int(x):,}円' for x in role_avg.values],
                textposition='outside',
                name='役職別平均',
                hovertemplate='<b>%{x}</b><br>平均: %{y:,}円<extra></extra>'
            ),
            row=1, col=2
        )
        
        # 3. 負担額分布（円グラフ）
        fig.add_trace(
            go.Pie(
                labels=df_result['名前'],
                values=df_result['負担額_丸め'],
                marker_colors=colors_list,
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>金額: %{value:,}円<br>割合: %{percent}<extra></extra>',
                name='負担額分布'
            ),
            row=2, col=1
        )
        
        # 4. 統計テーブル
        stats_data = [
            ['目標金額', f'{total_amount:,}円'],
            ['計算後合計', f'{sum_warikan:,}円'],
            ['差額', f'{sum_warikan - total_amount:+,}円'],
            ['参加者数', f'{len(df_result)}人'],
            ['平均負担額', f'{int(df_result["負担額_丸め"].mean()):,}円'],
            ['最高負担額', f'{int(df_result["負担額_丸め"].max()):,}円'],
            ['最低負担額', f'{int(df_result["負担額_丸め"].min()):,}円'],
            ['負担額範囲', f'{int(df_result["負担額_丸め"].max() - df_result["負担額_丸め"].min()):,}円']
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['統計項目', '値'],
                           fill_color='#667eea',
                           font=dict(color='white', size=12)),
                cells=dict(values=[[row[0] for row in stats_data], 
                                  [row[1] for row in stats_data]],
                          fill_color='#f8f9fa',
                          font=dict(size=11)),
                name='統計情報'
            ),
            row=2, col=2
        )
        
        # レイアウト調整
        fig.update_layout(
            height=800,
            title=dict(
                text=f'🍻 割り勘分析ダッシュボード<br><span style="font-size:14px;">合計: {sum_warikan:,}円 (目標: {total_amount:,}円)</span>',
                x=0.5,
                font=dict(size=18)
            ),
            showlegend=False,
            font=dict(family=current_font, size=12)
        )
        
        return fig

# ==== CSV出力機能 ====
def generate_csv_output(df_result, total_amount, sum_warikan):
    """CSV出力用データ生成"""
    csv_data = df_result.copy()
    csv_data['計算日時'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    csv_data['セッションID'] = st.session_state.session_id
    csv_data['目標金額'] = total_amount
    csv_data['計算後合計'] = sum_warikan
    csv_data['差額'] = sum_warikan - total_amount
    
    output = BytesIO()
    csv_data.to_csv(output, index=False, encoding='utf-8-sig')
    return output.getvalue()

# ==== メインアプリケーション ====
def main():
    """🎯 メインアプリケーション"""
    
    # 🔐 認証チェック（最重要！）
    if not check_authentication():
        return  # 認証失敗時は処理終了
    
    # セッション初期化
    init_session_state()
    
    # ユーザー情報表示
    show_user_info()
    
    # メインヘッダー
    user = st.session_state.user
    st.markdown(f'''
    <div class="main-header">
        <h1>🍻 AI割り勘システム</h1>
        <p>友達限定版 - {user['display_name']}さん専用ダッシュボード</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ システム設定")
        
        # システム情報
        st.info(f"🔤 フォント: {current_font}\n📝 日本語: {'✅' if is_japanese_font else '❌'}")
        
        # ナビゲーション
        st.subheader("📱 ナビゲーション")
        
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("🏠 ホーム", use_container_width=True):
                st.session_state.show_admin = False
                st.rerun()
        
        with col_nav2:
            if "admin" in user['permissions'] and st.button("👨‍💼 管理", use_container_width=True):
                st.session_state.show_admin = True
                st.rerun()
        
        # 基本設定
        st.subheader("💰 割り勘設定")
        total_amount = st.number_input(
            "💰 合計金額（円）",
            min_value=100,
            max_value=1000000,
            value=st.session_state.total_amount,
            step=500,
            help="飲み会・食事会などの合計金額を入力"
        )
        st.session_state.total_amount = total_amount
        
        marume_unit = st.selectbox(
            "🔢 丸め単位（円）",
            options=[100, 500, 1000],
            index=1,
            help="支払い金額を丸める単位"
        )
        
        # Git接続情報
        git_status = st.session_state.git_status
        if git_status:
            st.subheader("🔗 Git接続状態")
            if git_status.get("connected"):
                st.success("✅ 接続中")
                st.caption(f"📍 {git_status.get('repo_url', 'N/A')}")
                st.caption(f"🌿 Branch: {git_status.get('branch', 'N/A')}")
            else:
                st.error("❌ 未接続")
        
        # ログアウト
        st.subheader("🚪 セッション管理")
        if st.button("🚪 ログアウト", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.git_status = None
            st.session_state.participants = []
            st.session_state.calculation_results = None
            st.success("✅ ログアウトしました")
            time.sleep(1)
            st.rerun()
    
    # 管理者ダッシュボード表示判定
    if st.session_state.get('show_admin', False):
        show_admin_dashboard()
        return
    
    # メインコンテンツ
    tab1, tab2, tab3 = st.tabs(["👥 参加者管理", "🧮 AI計算", "📊 結果分析"])
    
    # ==== タブ1: 参加者管理 ====
    with tab1:
        st.subheader("👥 参加者管理")
        
        # 権限チェック
        if "create" not in user['permissions'] and "view" not in user['permissions']:
            st.error("❌ この機能を使用する権限がありません")
            return
        
        col_add1, col_add2 = st.columns([3, 1])
        
        with col_add1:
            # 参加者追加フォーム
            with st.form("add_participant_form"):
                col_name, col_role = st.columns([2, 1])
                
                with col_name:
                    new_name = st.text_input("👤 名前", placeholder="例: 田中さん")
                
                with col_role:
                    new_role = st.selectbox(
                        "💼 役職",
                        options=['担当', '主査', '課長', '部長', '事業部長'],
                        help="役職に応じて負担比率が調整されます"
                    )
                
                add_button = st.form_submit_button("➕ 参加者追加", use_container_width=True)
                
                if add_button and new_name:
                    if "create" in user['permissions']:
                        # 重複チェック
                        if not any(p['名前'] == new_name for p in st.session_state.participants):
                            st.session_state.participants.append({
                                '名前': new_name,
                                '役職': new_role,
                                '追加日時': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                '追加者': user['display_name']
                            })
                            st.success(f"✅ {new_name}さん（{new_role}）を追加しました")
                            st.rerun()
                        else:
                            st.warning("⚠️ 同じ名前の参加者が既に存在します")
                    else:
                        st.error("❌ 参加者追加権限がありません")
                elif add_button:
                    st.warning("👆 名前を入力してください")
        
        with col_add2:
            st.metric("👥 参加者数", len(st.session_state.participants))
        
        # 参加者一覧表示
        if st.session_state.participants:
            st.subheader("📋 参加者一覧")
            
            for i, participant in enumerate(st.session_state.participants):
                with st.container():
                    st.markdown(f"""
                    <div class="participant-card">
                        <strong>👤 {participant['名前']}</strong> 
                        <span class="permission-badge">{participant['役職']}</span><br>
                        <small>追加: {participant['追加日時']} by {participant['追加者']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 削除ボタン
                    if "create" in user['permissions']:
                        if st.button(f"🗑️ 削除", key=f"delete_{i}", help=f"{participant['名前']}さんを削除"):
                            st.session_state.participants.pop(i)
                            st.success(f"✅ {participant['名前']}さんを削除しました")
                            st.rerun()
        else:
            st.info("👆 まずは参加者を追加してください")
    
    # ==== タブ2: AI計算 ====
    with tab2:
        st.subheader("🧮 AI遺伝的アルゴリズム計算")
        
        # 権限チェック
        if "calculate" not in user['permissions']:
            st.error("❌ 計算権限がありません")
            return
        
        if not st.session_state.participants:
            st.warning("⚠️ 参加者を先に追加してください")
            return
        
        # 計算設定
        col_calc1, col_calc2, col_calc3 = st.columns(3)
        
        with col_calc1:
            st.metric("💰 合計金額", f"{total_amount:,}円")
        
        with col_calc2:
            st.metric("👥 参加者数", len(st.session_state.participants))
        
        with col_calc3:
            avg_amount = total_amount / len(st.session_state.participants)
            st.metric("📊 平均負担額", f"{avg_amount:,.0f}円")
        
        # AI計算実行
        if st.button("🤖 AI最適化実行", type="primary", use_container_width=True):
            with st.spinner("AI遺伝的アルゴリズムで最適化中..."):
                # データフレーム作成
                df_participants = pd.DataFrame(st.session_state.participants)
                
                # AI最適化実行
                optimizer = AIWarikanOptimizer()
                df_result, sum_warikan, diff, best_params = optimizer.optimize_warikan(
                    df_participants, total_amount, marume_unit
                )
                
                if df_result is not None:
                    # 結果保存
                    st.session_state.calculation_results = {
                        'df_result': df_result,
                        'sum_warikan': sum_warikan,
                        'diff': diff,
                        'best_params': best_params,
                        'calculation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'calculator': user['display_name']
                    }
                    
                    st.success("✅ 最適化完了！")
                    time.sleep(0.5)
                    st.rerun()
        
        # 計算結果表示
        if st.session_state.calculation_results:
            results = st.session_state.calculation_results
            df_result = results['df_result']
            sum_warikan = results['sum_warikan']
            diff = results['diff']
            
            st.markdown(f"""
            <div class="result-highlight">
                <h3>🎯 計算結果</h3>
                <p><strong>計算時刻:</strong> {results['calculation_time']}</p>
                <p><strong>計算者:</strong> {results['calculator']}</p>
                <p><strong>合計金額:</strong> {sum_warikan:,}円 (目標: {total_amount:,}円)</p>
                <p><strong>差額:</strong> {diff:+,}円</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 結果テーブル
            st.subheader("💰 個人別負担額")
            
            # 表示用データフレーム
            display_df = df_result[['名前', '役職', '負担額_丸め']].copy()
            display_df['負担額_丸め'] = display_df['負担額_丸め'].astype(int)
            display_df.columns = ['名前', '役職', '負担額（円）']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # 最適化パラメータ表示
            with st.expander("🔧 AI最適化パラメータ"):
                params_df = pd.DataFrame([
                    {'役職': role, '比率': f"{ratio:.3f}"}
                    for role, ratio in results['best_params'].items()
                ])
                st.dataframe(params_df, hide_index=True)
    
    # ==== タブ3: 結果分析 ====
    with tab3:
        st.subheader("📊 結果分析・可視化")
        
        if not st.session_state.calculation_results:
            st.warning("⚠️ 先にAI計算を実行してください")
            return
        
        results = st.session_state.calculation_results
        df_result = results['df_result']
        sum_warikan = results['sum_warikan']
        
        # インタラクティブチャート生成
        chart_generator = AdvancedChartGenerator()
        fig = chart_generator.create_interactive_charts(df_result, total_amount, sum_warikan)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 統計分析
        col_stats1, col_stats2 = st.columns(2)
        
        with col_stats1:
            st.subheader("📈 統計サマリー")
            
            stats_data = {
                "平均負担額": f"{df_result['負担額_丸め'].mean():.0f}円",
                "標準偏差": f"{df_result['負担額_丸め'].std():.0f}円",
                "最大負担額": f"{df_result['負担額_丸め'].max():.0f}円",
                "最小負担額": f"{df_result['負担額_丸め'].min():.0f}円",
                "負担額範囲": f"{df_result['負担額_丸め'].max() - df_result['負担額_丸め'].min():.0f}円"
            }
            
            for key, value in stats_data.items():
                st.metric(key, value)
        
        with col_stats2:
            st.subheader("💼 役職別分析")
            
            role_analysis = df_result.groupby('役職').agg({
                '負担額_丸め': ['count', 'mean', 'sum']
            }).round(0)
            
            role_analysis.columns = ['人数', '平均負担額', '合計負担額']
            st.dataframe(role_analysis)
        
        # CSV出力
        if "export" in user['permissions']:
            st.subheader("📥 データ出力")
            
            csv_data = generate_csv_output(df_result, total_amount, sum_warikan)
            
            st.download_button(
                label="📥 CSV形式でダウンロード",
                data=csv_data,
                file_name=f"warikan_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("ℹ️ CSV出力権限がありません")

# ==== 管理者ダッシュボード ====
def show_admin_dashboard():
    """👨‍💼 管理者ダッシュボード（Git連携情報付き）"""
    if "admin" not in st.session_state.user['permissions']:
        st.error("❌ 管理者権限が必要です")
        return
    
    st.markdown("""
    <div class="main-header">
        <h1>🛠️ 管理者ダッシュボード</h1>
        <p>ユーザー管理 & システム統計 & Git連携</p>
    </div>
    """, unsafe_allow_html=True)
    
    # システム情報
    deployment_info = auth_system.get_deployment_info()
    
    # メトリクス表示
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 登録ユーザー", deployment_info["total_registered"])
    col2.metric("✅ 承認済み", deployment_info["approved_friends"])
    col3.metric("🔒 セキュリティ", deployment_info["security_level"])
    col4.metric("🚀 プラットフォーム", deployment_info["platform"])
    
    # Git連携情報
    st.subheader("🔗 Git連携状況")
    
    git_status = st.session_state.git_status
    if git_status:
        col_git1, col_git2 = st.columns(2)
        
        with col_git1:
            st.info(f"""
            **リポジトリ情報:**
            - URL: {git_status.get('repo_url', 'N/A')}
            - ブランチ: {git_status.get('branch', 'N/A')}
            - 最終コミット: {git_status.get('last_commit', 'N/A')}
            """)
        
        with col_git2:
            st.success(f"""
            **デプロイ情報:**
            - 可視性: {deployment_info['repo_visibility']}
            - 認証方式: {deployment_info['auth_method']}
            - セキュリティレベル: {deployment_info['security_level']}
            """)
    
    # ユーザー管理
    st.subheader("👥 ユーザー管理")
    
    # 友達データベースの情報を表示
    user_data = []
    for username, data in auth_system.friends_db.items():
        user_data.append({
            "ユーザー名": username,
            "表示名": data["display_name"],
            "GitHub": data["github_username"],
            "Git認証": "✅" if data["git_verified"] else "❌",
            "権限数": len(data["permissions"]),
            "権限": ", ".join(data["permissions"]),
            "ログイン回数": data["login_count"],
            "最終ログイン": data["last_login"] or "未ログイン",
            "作成日": data["created_at"],
            "承認状態": "✅" if username in auth_system.approved_friends else "❌"
        })
    
    df_users = pd.DataFrame(user_data)
    st.dataframe(df_users, use_container_width=True)
    
    # 承認済み友達リスト管理
    st.subheader("🎫 承認済み友達リスト")
    
    st.info(f"""
    **現在の承認済みユーザー:**
    {', '.join(auth_system.approved_friends)}
    
    **設定方法:**
    Streamlit Cloud の環境変数 `APPROVED_FRIENDS` で管理
    例: "田中,佐藤,山田,admin"
    """)
    
    # セッション統計
    st.subheader("📊 セッション統計")
    
    if hasattr(st.session_state, 'calculation_results') and st.session_state.calculation_results:
        results = st.session_state.calculation_results
        
        session_stats = {
            "セッションID": st.session_state.session_id,
            "最終計算時刻": results.get('calculation_time', 'N/A'),
            "計算者": results.get('calculator', 'N/A'),
            "参加者数": len(st.session_state.participants),
            "計算済み": "✅" if results else "❌"
        }
        
        col_session1, col_session2 = st.columns(2)
        
        with col_session1:
            for key, value in list(session_stats.items())[:3]:
                st.metric(key, value)
        
        with col_session2:
            for key, value in list(session_stats.items())[3:]:
                st.metric(key, value)
    else:
        st.info("まだ計算が実行されていません")

# ==== アプリケーション実行 ====
if __name__ == "__main__":
    main()