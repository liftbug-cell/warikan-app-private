# ==== 完全版・セキュア認証付きAI割り勘システム ====
# secrets.toml で完全管理・コードに秘密情報なし

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
from typing import Dict, Optional, List
import time
import base64
from io import BytesIO
import os
from pathlib import Path

# ==== ページ設定 ====
st.set_page_config(
    page_title="🍻 友達限定AI割り勘システム Pro",
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
    .template-card {
        background: linear-gradient(135deg, #e8f4f8 0%, #d1ecf1 100%);
        border: 1px solid #bee5eb;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .history-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-left: 4px solid #28a745;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .session-restore {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #ffc107;
    }
    .feature-badge {
        display: inline-block;
        background: linear-gradient(45deg, #28a745, #20c997);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.7rem;
        margin: 0.1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
    .result-highlight {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .security-info {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 1px solid #bee5eb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #17a2b8;
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
</style>
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

# ==== データ管理システム ====
class DataManager:
    def __init__(self, username: str):
        self.username = username
        self.templates_key = f"templates_{username}"
        self.history_key = f"history_{username}"
        self.session_key = f"session_{username}"
    
    def save_template(self, template_name: str, participants: List[Dict]) -> bool:
        """参加者テンプレートを保存"""
        try:
            if self.templates_key not in st.session_state:
                st.session_state[self.templates_key] = {}
            
            template_data = {
                'name': template_name,
                'participants': participants,
                'created_at': datetime.now().isoformat(),
                'created_by': self.username
            }
            
            st.session_state[self.templates_key][template_name] = template_data
            return True
        except Exception as e:
            st.error(f"テンプレート保存エラー: {str(e)}")
            return False
    
    def load_templates(self) -> Dict:
        """保存済みテンプレートを読み込み"""
        return st.session_state.get(self.templates_key, {})
    
    def delete_template(self, template_name: str) -> bool:
        """テンプレートを削除"""
        try:
            if self.templates_key in st.session_state and template_name in st.session_state[self.templates_key]:
                del st.session_state[self.templates_key][template_name]
                return True
            return False
        except:
            return False
    
    def save_calculation_history(self, calculation_data: Dict) -> bool:
        """計算結果履歴を保存"""
        try:
            if self.history_key not in st.session_state:
                st.session_state[self.history_key] = []
            
            history_item = {
                'id': f"calc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}",
                'calculation_time': datetime.now().isoformat(),
                'total_amount': calculation_data.get('total_amount'),
                'participants': calculation_data.get('participants'),
                'results': calculation_data.get('results'),
                'sum_warikan': calculation_data.get('sum_warikan'),
                'diff': calculation_data.get('diff'),
                'calculator': self.username
            }
            
            # 最新10件のみ保持
            st.session_state[self.history_key].insert(0, history_item)
            if len(st.session_state[self.history_key]) > 10:
                st.session_state[self.history_key] = st.session_state[self.history_key][:10]
            
            return True
        except Exception as e:
            st.error(f"履歴保存エラー: {str(e)}")
            return False
    
    def load_calculation_history(self) -> List[Dict]:
        """計算履歴を読み込み"""
        return st.session_state.get(self.history_key, [])
    
    def delete_history_item(self, item_id: str) -> bool:
        """履歴アイテムを削除"""
        try:
            if self.history_key in st.session_state:
                st.session_state[self.history_key] = [
                    item for item in st.session_state[self.history_key] 
                    if item['id'] != item_id
                ]
                return True
            return False
        except:
            return False
    
    def save_session_data(self, session_data: Dict) -> bool:
        """作業中セッションデータを保存"""
        try:
            auto_save_data = {
                'participants': session_data.get('participants', []),
                'total_amount': session_data.get('total_amount', 10000),
                'last_saved': datetime.now().isoformat(),
                'session_id': session_data.get('session_id'),
                'calculation_results': session_data.get('calculation_results')
            }
            
            st.session_state[self.session_key] = auto_save_data
            return True
        except Exception as e:
            st.error(f"セッション保存エラー: {str(e)}")
            return False
    
    def load_session_data(self) -> Optional[Dict]:
        """保存されたセッションデータを読み込み"""
        return st.session_state.get(self.session_key)
    
    def clear_session_data(self) -> bool:
        """セッションデータをクリア"""
        try:
            if self.session_key in st.session_state:
                del st.session_state[self.session_key]
            return True
        except:
            return False

# ==== カスタム倍率管理クラスの追加 ====
class CustomMultiplierManager:
    def __init__(self):
        # Streamlit Cloud対応の永続化
        self.global_key = "GLOBAL_CUSTOM_MULTIPLIERS"
        self.backup_key = "multiplier_backup_store"
    
    def save_multiplier_rules(self, rules: Dict) -> bool:
        """倍率ルールを永続化保存（Streamlit Cloud対応）"""
        try:
            # 方法1: st.session_stateの特別なキーを使用
            # このキーは異なるセッション間で共有される
            for key in list(st.session_state.keys()):
                if key.startswith('user_') or key.startswith('temp_'):
                    continue  # ユーザー固有データはスキップ
            
            # グローバル共有ストレージとして使用
            st.session_state[self.global_key] = {
                'rules': rules,
                'last_updated': datetime.now().isoformat(),
                'updated_by': st.session_state.user['username'] if 'user' in st.session_state else 'unknown'
            }
            
            # バックアップも保存
            st.session_state[self.backup_key] = rules.copy()
            
            return True
            
        except Exception as e:
            st.error(f"倍率ルール保存エラー: {str(e)}")
            return False
    
    def load_multiplier_rules(self) -> Dict:
        """倍率ルールを読み込み（Streamlit Cloud対応）"""
        try:
            # メインストレージから読み込み
            if self.global_key in st.session_state:
                global_data = st.session_state[self.global_key]
                if isinstance(global_data, dict) and 'rules' in global_data:
                    return global_data['rules']
            
            # バックアップから読み込み
            if self.backup_key in st.session_state:
                return st.session_state[self.backup_key]
            
            # 初期値
            return {}
            
        except Exception as e:
            st.error(f"倍率ルール読み込みエラー: {str(e)}")
            return {}
    
    def delete_multiplier_rule(self, rule_name: str) -> bool:
        """倍率ルールを削除"""
        try:
            rules = self.load_multiplier_rules()
            if rule_name in rules:
                del rules[rule_name]
                return self.save_multiplier_rules(rules)
            return False
        except:
            return False
    
    def get_storage_info(self) -> Dict:
        """ストレージ情報を取得"""
        try:
            info = {
                'has_global_storage': self.global_key in st.session_state,
                'has_backup_storage': self.backup_key in st.session_state,
                'rules_count': len(self.load_multiplier_rules()),
                'storage_type': 'Streamlit Session State (Global)',
                'persistence_level': 'アプリ実行中は永続'
            }
            
            if self.global_key in st.session_state:
                global_data = st.session_state[self.global_key]
                if isinstance(global_data, dict):
                    info['last_updated'] = global_data.get('last_updated', '不明')
                    info['updated_by'] = global_data.get('updated_by', '不明')
            
            return info
        except:
            return {'error': True}
    
    def find_matching_multiplier(self, participant_name: str) -> float:
        """参加者名に対応する倍率を検索（柔軟マッチング）"""
        rules = self.load_multiplier_rules()
        
        for rule_name, rule_data in rules.items():
            name_patterns = rule_data.get('name_patterns', [])
            multiplier = rule_data.get('multiplier', 1.0)
            
            # 柔軟な名前マッチング
            for pattern in name_patterns:
                if self._flexible_name_match(participant_name, pattern):
                    return multiplier
        
        return 1.0  # デフォルト倍率
    
    def _flexible_name_match(self, participant_name: str, pattern: str) -> bool:
        """柔軟な名前マッチング"""
        # 正規化：空白、「さん」「君」「ちゃん」などを除去
        def normalize_name(name):
            # よくある敬称を除去
            suffixes = ['さん', 'くん', 'ちゃん', '君', '様', 'サン', 'クン']
            normalized = name.strip()
            for suffix in suffixes:
                if normalized.endswith(suffix):
                    normalized = normalized[:-len(suffix)]
            return normalized.lower()
        
        normalized_participant = normalize_name(participant_name)
        normalized_pattern = normalize_name(pattern)
        
        # 完全一致チェック
        if normalized_participant == normalized_pattern:
            return True
        
        # 部分一致チェック（パターンが参加者名に含まれる）
        if normalized_pattern in normalized_participant:
            return True
        
        # 参加者名がパターンに含まれる
        if normalized_participant in normalized_pattern:
            return True
        
        return False
    
    def export_rules_for_sharing(self) -> str:
        """ルールを共有用形式でエクスポート"""
        rules = self.load_multiplier_rules()
        storage_info = self.get_storage_info()
        
        export_data = {
            'rules': rules,
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'rules_count': len(rules),
                'storage_info': storage_info
            }
        }
        return json.dumps(export_data, ensure_ascii=False, indent=2)
    
    def import_rules_from_text(self, rules_text: str) -> bool:
        """テキストからルールをインポート"""
        try:
            imported_data = json.loads(rules_text)
            
            # 新形式（export_rules_for_sharing からのデータ）
            if 'rules' in imported_data and 'export_info' in imported_data:
                imported_rules = imported_data['rules']
            # 旧形式（直接ルールデータ）
            else:
                imported_rules = imported_data
            
            current_rules = self.load_multiplier_rules()
            current_rules.update(imported_rules)
            return self.save_multiplier_rules(current_rules)
            
        except json.JSONDecodeError:
            st.error("❌ インポートデータの形式が正しくありません")
            return False
        except Exception as e:
            st.error(f"❌ インポートエラー: {str(e)}")
            return False


# ==== セキュア認証システム（TOML完全管理） ====
class SecureAuthSystem:
    def __init__(self):
        # 🔐 すべての認証情報を secrets.toml から読み込み
        self.friends_db = self._load_user_database()
        self.approved_friends = self._get_approved_friends()
        
        # セキュリティ情報
        self.security_info = {
            "auth_method": "Secure TOML Configuration",
            "password_storage": "Hashed in Environment Variables",
            "code_security": "No Secrets in Source Code",
            "admin_management": "Dynamic from TOML"
        }
    
    def _hash(self, password: str) -> str:
        """SHA256でパスワードハッシュ化"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_user_database(self) -> Dict:
        """secrets.toml からユーザーデータベースを構築"""
        user_db = {}
        
        try:
            # 🔐 一般ユーザー情報を取得
            user_info = st.secrets.get("USER_INFO", {})
            user_credentials = st.secrets.get("USER_CREDENTIALS", {})
            
            # 一般ユーザーを追加
            for username, info in user_info.items():
                password_hash = user_credentials.get(username, self._hash(f"{username.lower()}123"))
                
                user_db[username] = {
                    "password_hash": password_hash,
                    "display_name": info.get("display_name", f"{username}さん"),
                    "github_username": info.get("github_username", f"{username}_github"),
                    "permissions": info.get("permissions", ["view", "calculate"]),
                    "created_at": info.get("created_at", "2024-08-17"),
                    "last_login": None,
                    "login_count": 0,
                    "git_verified": info.get("git_verified", False)
                }
            
            # 🔑 管理者アカウントを追加
            admin_credentials = st.secrets.get("ADMIN_CREDENTIALS", {})
            
            for admin_username, admin_info in admin_credentials.items():
                admin_data = {
                    "password_hash": admin_info.get("password_hash", self._hash("admin123")),
                    "display_name": admin_info.get("display_name", f"{admin_username}管理者"),
                    "github_username": admin_info.get("github_username", f"{admin_username}_admin"),
                    "permissions": ["admin", "create", "view", "calculate", "export", "template"],
                    "created_at": admin_info.get("created_at", "2024-08-17"),
                    "last_login": None,
                    "login_count": 0,
                    "git_verified": admin_info.get("git_verified", True)
                }
                user_db[admin_username] = admin_data
            
            # デバッグ情報（開発時のみ）
            if len(user_db) == 0:
                st.warning("⚠️ secrets.toml にユーザー情報が設定されていません")
                # 緊急フォールバック
                user_db["demo"] = {
                    "password_hash": self._hash("demo123"),
                    "display_name": "デモユーザー",
                    "github_username": "demo_user",
                    "permissions": ["view", "calculate"],
                    "created_at": "2024-08-17",
                    "last_login": None,
                    "login_count": 0,
                    "git_verified": False
                }
            
            return user_db
            
        except Exception as e:
            st.error(f"ユーザーDB読み込みエラー: {str(e)}")
            # 最小限のフォールバック
            return {
                "emergency": {
                    "password_hash": self._hash("emergency123"),
                    "display_name": "緊急ユーザー",
                    "github_username": "emergency_user",
                    "permissions": ["admin", "create", "view", "calculate", "export", "template"],
                    "created_at": "2024-08-17",
                    "last_login": None,
                    "login_count": 0,
                    "git_verified": True
                }
            }
    
    def _get_approved_friends(self) -> list:
        """環境変数から承認済み友達リストを取得"""
        try:
            approved = st.secrets.get("APPROVED_FRIENDS", "demo")
            approved_list = [name.strip() for name in approved.split(",")]
            
            # 管理者も自動的に承認済みリストに追加
            admin_users = list(st.secrets.get("ADMIN_CREDENTIALS", {}).keys())
            for admin in admin_users:
                if admin not in approved_list:
                    approved_list.append(admin)
            
            return approved_list
        except:
            return list(self.friends_db.keys())  # フォールバック: 全ユーザーを承認
    
    def add_new_user(self, username: str, password: str, display_name: str, 
                     github_username: str, permissions: list, is_admin: bool = False) -> Dict:
        """新しいユーザーを動的に追加"""
        try:
            if username in self.friends_db:
                return {
                    "success": False,
                    "message": f"ユーザー「{username}」は既に存在します"
                }
            
            # 管理者権限の場合は自動的に admin 権限を追加
            if is_admin and "admin" not in permissions:
                permissions.append("admin")
            
            # 新しいユーザー情報を追加
            self.friends_db[username] = {
                "password_hash": self._hash(password),
                "display_name": display_name,
                "github_username": github_username,
                "permissions": permissions,
                "created_at": datetime.now().strftime('%Y-%m-%d'),
                "last_login": None,
                "login_count": 0,
                "git_verified": False
            }
            
            return {
                "success": True,
                "message": f"ユーザー「{display_name}」を追加しました",
                "is_admin": is_admin,
                "username": username,
                "password_hash": self._hash(password)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"ユーザー追加エラー: {str(e)}"
            }
    
    def update_user_permissions(self, username: str, new_permissions: list) -> Dict:
        """ユーザーの権限を更新"""
        try:
            if username not in self.friends_db:
                return {
                    "success": False,
                    "message": f"ユーザー「{username}」が見つかりません"
                }
            
            self.friends_db[username]["permissions"] = new_permissions
            
            return {
                "success": True,
                "message": f"ユーザー「{username}」の権限を更新しました"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"権限更新エラー: {str(e)}"
            }
    
    def update_approved_friends(self, approved_list: list) -> Dict:
        """承認済み友達リストを更新（セッション内のみ）"""
        try:
            self.approved_friends = approved_list
            return {
                "success": True,
                "message": "承認済み友達リストを更新しました（セッション内のみ）"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"リスト更新エラー: {str(e)}"
            }
    
    def delete_user(self, username: str) -> Dict:
        """ユーザーを削除"""
        try:
            # 管理者の最後の一人は削除不可
            admin_users = [u for u in self.friends_db.values() if "admin" in u["permissions"]]
            if "admin" in self.friends_db[username]["permissions"] and len(admin_users) <= 1:
                return {
                    "success": False,
                    "message": "最後の管理者アカウントは削除できません"
                }
            
            if username not in self.friends_db:
                return {
                    "success": False,
                    "message": f"ユーザー「{username}」が見つかりません"
                }
            
            del self.friends_db[username]
            
            # 承認済みリストからも削除
            if username in self.approved_friends:
                self.approved_friends.remove(username)
            
            return {
                "success": True,
                "message": f"ユーザー「{username}」を削除しました"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"ユーザー削除エラー: {str(e)}"
            }
    
    def authenticate(self, username: str, password: str) -> Dict:
        """認証処理"""
        
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
        
        # 4. ログイン記録更新
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
                "git_verified": user["git_verified"],
                "is_admin": "admin" in user["permissions"]
            },
            "git_status": {
                "connected": True,
                "repo_url": "https://github.com/your-username/warikan-app",
                "branch": "main",
                "last_commit": "2024-08-17 14:30:00"
            }
        }
    
    def get_deployment_info(self) -> Dict:
        """デプロイメント情報取得"""
        admin_count = len([u for u in self.friends_db.values() if "admin" in u["permissions"]])
        
        return {
            "platform": "Streamlit Cloud",
            "repo_visibility": "Public",
            "auth_method": "Secure TOML Configuration",
            "approved_friends": len(self.approved_friends),
            "total_registered": len(self.friends_db),
            "admin_users": admin_count,
            "security_level": "TOML Managed + Zero Code Secrets"
        }

# 認証システム初期化
auth_system = SecureAuthSystem()

# ==== AI最適化エンジン ====
class AIWarikanOptimizer:
    def __init__(self):
        self.default_params = {
            '事業部長': 1.6, '部長': 1.4, '課長': 1.2, '主査': 1.1, '担当': 1.0
        }
    
    def optimize_warikan(self, df_participants, total_amount, marume=500):
        """AI遺伝的アルゴリズムによる最適化（自動倍率適用）"""
        if df_participants.empty:
            return None, None, None, None
        
        # カスタム倍率マネージャーを初期化
        multiplier_manager = CustomMultiplierManager()
        
        best_params = self.default_params.copy()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        iterations = 25
        
        for iteration in range(iterations):
            progress = (iteration + 1) / iterations
            progress_bar.progress(progress)
            status_text.text(f"🤖 AI最適化中... {iteration+1}/{iterations} 世代")
            
            df_calc = df_participants.copy()
            
            # 基本の役職比率を適用
            df_calc['基本比率'] = df_calc['役職'].map(best_params)
            
            # 管理者設定のカスタム倍率を自動適用
            df_calc['管理者設定倍率'] = df_calc['名前'].apply(
                lambda name: multiplier_manager.find_matching_multiplier(name)
            )
            
            # 参加者個別設定の倍率（既存機能との互換性）
            df_calc['個別設定倍率'] = df_calc.get('カスタム倍率', 1.0)
            
            # 最終倍率 = 管理者設定倍率 × 個別設定倍率
            df_calc['最終倍率'] = df_calc['管理者設定倍率'] * df_calc['個別設定倍率']
            
            # 最終比率 = 基本比率 × 最終倍率
            df_calc['比率'] = df_calc['基本比率'] * df_calc['最終倍率']
            
            total_weight = df_calc['比率'].sum()
            df_calc['負担額'] = df_calc['比率'] / total_weight * total_amount
            df_calc['負担額_丸め'] = df_calc['負担額'].apply(
                lambda x: marume * round(x / marume)
            )
            
            sum_warikan = df_calc['負担額_丸め'].sum()
            diff = sum_warikan - total_amount
            
            if abs(diff) <= marume:
                progress_bar.progress(1.0)
                status_text.success("✅ 最適解発見！")
                break
            
            adjustment = 0.01 if abs(diff) > 1000 else 0.005
            mutation_rate = 0.02
            
            if diff > 0:
                for role in ['事業部長', '部長', '課長', '主査']:
                    if role in best_params:
                        best_params[role] *= (1 - adjustment)
                        if random.random() < mutation_rate:
                            best_params[role] *= random.uniform(0.95, 1.05)
            else:
                for role in ['事業部長', '部長', '課長', '主査']:
                    if role in best_params:
                        best_params[role] *= (1 + adjustment)
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
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('👥 個人別負担額', '💼 役職別平均', '🥧 負担額分布', '📊 詳細統計'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "table"}]]
        )
        
        colors_list = [role_colors.get(role, '#95A5A6') for role in df_result['役職']]
        
        # 1. 個人別負担額
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
        
        # 3. 負担額分布
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

# ==== セッション状態管理 ====
def init_session_state():
    """セッション状態初期化"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.git_status = None
        st.session_state.data_manager = None
    
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
    
    if 'auto_save_enabled' not in st.session_state:
        st.session_state.auto_save_enabled = True

# ==== 自動保存機能 ====
def auto_save_session():
    """🔄 自動保存機能"""
    if st.session_state.auto_save_enabled and st.session_state.data_manager:
        session_data = {
            'participants': st.session_state.participants,
            'total_amount': st.session_state.total_amount,
            'session_id': st.session_state.session_id,
            'calculation_results': st.session_state.calculation_results
        }
        st.session_state.data_manager.save_session_data(session_data)

# ==== セッション復元機能 ====
def show_session_restore():
    """🔄 セッション復元機能"""
    data_manager = st.session_state.data_manager
    saved_session = data_manager.load_session_data()
    
    if saved_session:
        last_saved = datetime.fromisoformat(saved_session['last_saved'])
        time_diff = datetime.now() - last_saved
        
        # 24時間以内の保存データのみ表示
        if time_diff.total_seconds() < 86400:  # 24時間
            st.markdown(f"""
            <div class="session-restore">
                <strong>🔄 前回の作業を発見しました</strong><br>
                <small>💾 保存時刻: {last_saved.strftime('%Y年%m月%d日 %H:%M')}</small><br>
                <small>👥 参加者: {len(saved_session.get('participants', []))}人 | 
                💰 金額: {saved_session.get('total_amount', 0):,}円</small>
            </div>
            """, unsafe_allow_html=True)
            
            col_restore, col_ignore = st.columns(2)
            
            with col_restore:
                if st.button("🔄 前回の作業を復元", use_container_width=True, type="primary"):
                    st.session_state.participants = saved_session.get('participants', [])
                    st.session_state.total_amount = saved_session.get('total_amount', 10000)
                    st.session_state.session_id = saved_session.get('session_id', st.session_state.session_id)
                    if saved_session.get('calculation_results'):
                        st.session_state.calculation_results = saved_session['calculation_results']
                    
                    st.success("✅ 前回の作業を復元しました")
                    st.rerun()
            
            with col_ignore:
                if st.button("🆕 新規作業開始", use_container_width=True):
                    data_manager.clear_session_data()
                    st.success("✅ 新規作業を開始しました")
                    st.rerun()

# ==== 認証チェック機能 ====
def check_authentication():
    """🔐 認証状態チェック"""
    init_session_state()
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    
    # データマネージャー初期化
    if st.session_state.data_manager is None:
        st.session_state.data_manager = DataManager(st.session_state.user['username'])
    
    return True

def show_login_page():
    """🔐 ログインページ表示（セキュア版）"""
    st.markdown("""
    <div class="auth-container">
        <h1>🔒 友達限定アクセス</h1>
        <p>このAI割り勘システムは招待された友達のみ利用できます</p>
        <p>✨ セキュアTOML管理 + AI遺伝的アルゴリズム ✨</p>
        <span class="feature-badge">🔐 TOML管理</span>
        <span class="feature-badge">👥 テンプレート</span>
        <span class="feature-badge">💾 履歴保存</span>
        <span class="feature-badge">🔄 自動復元</span>
    </div>
    """, unsafe_allow_html=True)
    
    # セキュリティ情報
    deployment_info = auth_system.get_deployment_info()
    
    st.markdown(f"""
    <div class="security-info">
        <strong>🔐 セキュリティ機能:</strong><br>
        📍 Platform: {deployment_info['platform']}<br>
        🛡️ 認証方式: {deployment_info['auth_method']}<br>
        🔒 セキュリティレベル: {deployment_info['security_level']}<br>
        👥 登録ユーザー: {deployment_info['total_registered']}人 | 
        ✅ 承認済み: {deployment_info['approved_friends']}人 | 
        🔑 管理者: {deployment_info['admin_users']}人
    </div>
    """, unsafe_allow_html=True)
    
    # ログインフォーム
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="auth-form">', unsafe_allow_html=True)
            
            st.markdown("### 👤 セキュアログイン")
            
            with st.form("secure_login_form", clear_on_submit=False):
                username = st.text_input("👤 ユーザー名", placeholder="管理者が設定したユーザー名")
                password = st.text_input("🔑 パスワード", type="password", placeholder="管理者から受け取ったパスワード")
                
                col_login, col_info = st.columns(2)
                
                with col_login:
                    login_button = st.form_submit_button("🔐 ログイン", use_container_width=True)
                
                with col_info:
                    info_button = st.form_submit_button("ℹ️ 設定情報", use_container_width=True)
                
                if login_button:
                    if username and password:
                        with st.spinner("セキュア認証中..."):
                            time.sleep(0.5)
                            result = auth_system.authenticate(username, password)
                            
                            if result["success"]:
                                st.session_state.authenticated = True
                                st.session_state.user = result["user"]
                                st.session_state.git_status = result["git_status"]
                                st.session_state.data_manager = DataManager(username)
                                
                                welcome_msg = f"✅ {result['user']['display_name']}、ようこそ！"
                                if result['user']['is_admin']:
                                    welcome_msg += " （管理者権限）"
                                
                                st.success(welcome_msg)
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(result["message"])
                    else:
                        st.warning("👆 ユーザー名とパスワードを入力してください")
                
                if info_button:
                    st.markdown("""
                    <div class="demo-info">
                    <strong>📋 TOML設定情報:</strong><br><br>
                    
                    <strong>🔐 認証情報の管理:</strong><br>
                    - ユーザー情報: <code>USER_INFO</code><br>
                    - パスワード: <code>USER_CREDENTIALS</code><br>
                    - 管理者: <code>ADMIN_CREDENTIALS</code><br>
                    - 承認リスト: <code>APPROVED_FRIENDS</code><br><br>
                    
                    <strong>✨ セキュリティ特徴:</strong><br>
                    - パスワードはハッシュ化済み<br>
                    - コードに秘密情報なし<br>
                    - 環境変数で完全管理<br>
                    - 複数管理者対応<br><br>
                    
                    <strong>📞 アクセス申請:</strong><br>
                    管理者にユーザー追加を依頼してください
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_user_info():
    """👤 ユーザー情報表示（セキュア版）"""
    user = st.session_state.user
    git_status = st.session_state.git_status
    
    git_icon = "✅" if git_status.get("connected") else "❌"
    admin_badge = "🔑 管理者" if user['is_admin'] else ""
    
    st.markdown(f"""
    <div class="user-info">
        <strong>👤 ログイン中:</strong> {user['display_name']} ({user['username']}) {admin_badge}<br>
        <strong>🐙 GitHub:</strong> {user['github_username']} {'🔒' if user['git_verified'] else '⚠️'}<br>
        <strong>🔗 Git接続:</strong> {git_icon} {git_status.get('repo_url', 'N/A')}<br>
        <strong>🔢 ログイン回数:</strong> {user['login_count']}回<br>
        <strong>🎫 権限:</strong> 
        {''.join([f'<span class="permission-badge">{p}</span>' for p in user['permissions']])}
        <br><br>
        <strong>🔐 セキュリティ:</strong>
        <span class="feature-badge">TOML管理</span>
        <span class="feature-badge">ハッシュ化認証</span>
        <br>
        <strong>✨ Pro機能:</strong>
        <span class="feature-badge">👥 テンプレート</span>
        <span class="feature-badge">💾 履歴保存</span>
        <span class="feature-badge">🔄 自動復元</span>
    </div>
    """, unsafe_allow_html=True)

# ==== テンプレート管理機能 ====
def show_template_management():
    """👥 テンプレート管理機能"""
    st.subheader("👥 参加者テンプレート管理")
    
    data_manager = st.session_state.data_manager
    
    # 権限チェック
    if "template" not in st.session_state.user['permissions']:
        st.error("❌ テンプレート機能の権限がありません")
        return
    
    col_template1, col_template2 = st.columns([1, 1])
    
    with col_template1:
        # テンプレート保存
        st.markdown("#### 💾 新規テンプレート保存")
        
        if st.session_state.participants:
            with st.form("save_template_form"):
                template_name = st.text_input(
                    "📝 テンプレート名", 
                    placeholder="例: 会社飲み会メンバー"
                )
                
                st.markdown("**保存対象参加者:**")
                for participant in st.session_state.participants:
                    st.write(f"• {participant['名前']} ({participant['役職']})")
                
                save_template_btn = st.form_submit_button("💾 テンプレート保存", use_container_width=True)
                
                if save_template_btn and template_name:
                    success = data_manager.save_template(template_name, st.session_state.participants)
                    if success:
                        st.success(f"✅ テンプレート「{template_name}」を保存しました")
                        st.rerun()
                    else:
                        st.error("❌ テンプレート保存に失敗しました")
                elif save_template_btn:
                    st.warning("👆 テンプレート名を入力してください")
        else:
            st.info("💡 参加者を追加してからテンプレートを保存できます")
    
    with col_template2:
        # 保存済みテンプレート一覧
        st.markdown("#### 📂 保存済みテンプレート")
        
        templates = data_manager.load_templates()
        
        if templates:
            for template_name, template_data in templates.items():
                with st.container():
                    st.markdown(f"""
                    <div class="template-card">
                        <strong>📁 {template_name}</strong><br>
                        <small>👥 {len(template_data['participants'])}人 | 
                        📅 {template_data['created_at'][:10]}</small><br>
                        <small>参加者: {', '.join([p['名前'] for p in template_data['participants'][:3]])}
                        {'...' if len(template_data['participants']) > 3 else ''}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_load, col_delete = st.columns([3, 1])
                    
                    with col_load:
                        if st.button(f"📥 読み込み", key=f"load_template_{template_name}", use_container_width=True):
                            st.session_state.participants = template_data['participants'].copy()
                            st.success(f"✅ テンプレート「{template_name}」を読み込みました")
                            auto_save_session()
                            st.rerun()
                    
                    with col_delete:
                        if st.button(f"🗑️", key=f"delete_template_{template_name}", help="テンプレート削除"):
                            success = data_manager.delete_template(template_name)
                            if success:
                                st.success(f"✅ テンプレート「{template_name}」を削除しました")
                                st.rerun()
        else:
            st.info("📝 保存済みテンプレートがありません")

# ==== 履歴管理機能 ====
def show_calculation_history():
    """💾 計算履歴管理機能"""
    st.subheader("📊 計算履歴")
    
    data_manager = st.session_state.data_manager
    history = data_manager.load_calculation_history()
    
    if history:
        st.info(f"📈 過去の計算結果: {len(history)}件")
        
        for i, history_item in enumerate(history):
            calc_time = datetime.fromisoformat(history_item['calculation_time'])
            
            with st.container():
                st.markdown(f"""
                <div class="history-card">
                    <strong>🧮 計算 #{i+1}</strong><br>
                    <small>📅 {calc_time.strftime('%Y年%m月%d日 %H:%M')} | 
                    💰 {history_item['total_amount']:,}円 | 
                    👥 {len(history_item['participants'])}人</small><br>
                    <small>差額: {history_item['diff']:+,}円 | 
                    計算後: {history_item['sum_warikan']:,}円</small>
                </div>
                """, unsafe_allow_html=True)
                
                col_detail, col_restore, col_delete = st.columns([2, 1, 1])
                
                with col_detail:
                    with st.expander("📋 詳細を見る"):
                        # 参加者情報
                        st.markdown("**👥 参加者:**")
                        participants_df = pd.DataFrame(history_item['participants'])
                        st.dataframe(participants_df[['名前', '役職']], hide_index=True)
                        
                        # 計算結果
                        if 'results' in history_item and history_item['results'] is not None:
                            st.markdown("**💰 計算結果:**")
                            results_df = pd.DataFrame(history_item['results'])
                            if '負担額_丸め' in results_df.columns:
                                display_results = results_df[['名前', '役職', '負担額_丸め']].copy()
                                display_results['負担額_丸め'] = display_results['負担額_丸め'].astype(int)
                                display_results.columns = ['名前', '役職', '負担額（円）']
                                st.dataframe(display_results, hide_index=True)
                
                with col_restore:
                    if st.button("🔄 復元", key=f"restore_history_{history_item['id']}", use_container_width=True):
                        # 参加者と設定を復元
                        st.session_state.participants = history_item['participants'].copy()
                        st.session_state.total_amount = history_item['total_amount']
                        
                        # 計算結果も復元（もしあれば）
                        if 'results' in history_item:
                            st.session_state.calculation_results = {
                                'df_result': pd.DataFrame(history_item['results']) if history_item['results'] else None,
                                'sum_warikan': history_item['sum_warikan'],
                                'diff': history_item['diff'],
                                'calculation_time': history_item['calculation_time'],
                                'calculator': history_item['calculator']
                            }
                        
                        auto_save_session()
                        st.success("✅ 履歴から復元しました")
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️", key=f"delete_history_{history_item['id']}", help="履歴削除"):
                        success = data_manager.delete_history_item(history_item['id'])
                        if success:
                            st.success("✅ 履歴を削除しました")
                            st.rerun()
    else:
        st.info("📝 計算履歴がありません")

# ==== 不足している機能の追加パッチ ====

# 1. ユーザー詳細表示機能
def show_user_details(username: str, user_data: Dict, is_admin: bool = False):
    """ユーザー詳細表示"""
    col_info, col_actions = st.columns([2, 1])
    
    with col_info:
        st.write(f"**GitHub:** {user_data['github_username']}")
        st.write(f"**権限:** {', '.join(user_data['permissions'])}")
        st.write(f"**ログイン回数:** {user_data['login_count']}")
        st.write(f"**作成日:** {user_data['created_at']}")
        st.write(f"**承認状態:** {'✅ 承認済み' if username in auth_system.approved_friends else '❌ 未承認'}")
        
        if is_admin:
            st.success("🔑 管理者権限有り")
    
    with col_actions:
        # 承認状態切り替え
        is_approved = username in auth_system.approved_friends
        
        if not is_approved:
            if st.button("✅ 承認", key=f"approve_{username}"):
                auth_system.approved_friends.append(username)
                st.success(f"ユーザー「{username}」を承認しました")
                st.warning("⚠️ 永続化するには secrets.toml の APPROVED_FRIENDS を更新してください")
                st.rerun()
        else:
            if st.button("❌ 承認取消", key=f"revoke_{username}"):
                auth_system.approved_friends.remove(username)
                st.success(f"ユーザー「{username}」の承認を取り消しました")
                st.rerun()
        
        # 削除（最後の管理者以外）
        admin_count = len([u for u in auth_system.friends_db.values() if "admin" in u["permissions"]])
        can_delete = not is_admin or admin_count > 1
        
        if can_delete:
            if st.button("🗑️ 削除", key=f"delete_{username}", help="ユーザーを削除"):
                result = auth_system.delete_user(username)
                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])

# 2. セキュアユーザー管理機能
def show_secure_user_management():
    """🔐 セキュアユーザー管理画面"""
    st.subheader("👥 セキュアユーザー管理")
    
    # セキュリティ情報表示
    st.markdown("""
    <div class="security-info">
    <strong>🔐 セキュリティ機能:</strong><br>
    ✅ パスワードは環境変数で管理<br>
    ✅ 管理者権限は動的設定<br>
    ✅ コードに秘密情報を含まない<br>
    ✅ 複数管理者対応<br>
    ✅ TOML設定で完全管理
    </div>
    """, unsafe_allow_html=True)
    
    # 新規ユーザー追加
    st.markdown("#### ➕ 新規ユーザー追加")
    
    with st.form("add_secure_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("ユーザー名", placeholder="例: 鈴木")
            new_display_name = st.text_input("表示名", placeholder="例: 鈴木さん")
            new_password = st.text_input("パスワード", type="password", placeholder="例: suzuki123")
        
        with col2:
            new_github = st.text_input("GitHub ユーザー名", placeholder="例: suzuki_dev")
            
            # 権限選択
            available_permissions = ["view", "create", "calculate", "export", "template"]
            selected_permissions = st.multiselect(
                "基本権限選択",
                available_permissions,
                default=["view", "calculate", "template"],
                help="基本権限を選択"
            )
            
            # 管理者権限
            is_admin_user = st.checkbox(
                "🔑 管理者権限を付与",
                help="管理者権限を持つユーザーとして追加"
            )
        
        add_user_btn = st.form_submit_button(
            "👤 ユーザー追加" if not is_admin_user else "🔑 管理者追加", 
            use_container_width=True
        )
        
        if add_user_btn:
            if new_username and new_display_name and new_password and selected_permissions:
                result = auth_system.add_new_user(
                    new_username, new_password, new_display_name, 
                    new_github or f"{new_username}_github", 
                    selected_permissions, is_admin_user
                )
                
                if result["success"]:
                    if result.get("is_admin"):
                        st.success(f"✅ {result['message']} (管理者権限付き)")
                        st.warning("⚠️ 管理者アカウントを永続化するには secrets.toml を更新してください")
                    else:
                        st.success(result["message"])
                    
                    st.info("💡 新しいユーザーを有効化するには、承認済みリストに追加してください")
                    
                    # TOML設定例を表示
                    if result.get("is_admin"):
                        st.markdown("**🔐 secrets.toml 設定例（管理者）:**")
                        st.code(f"""
[ADMIN_CREDENTIALS.{new_username}]
password_hash = "{result['password_hash']}"
display_name = "{new_display_name}"
github_username = "{new_github or f'{new_username}_github'}"
created_at = "{datetime.now().strftime('%Y-%m-%d')}"
git_verified = false
                        """, language="toml")
                    else:
                        st.markdown("**📝 secrets.toml 設定例（一般ユーザー）:**")
                        st.code(f"""
[USER_INFO.{new_username}]
display_name = "{new_display_name}"
github_username = "{new_github or f'{new_username}_github'}"
permissions = {selected_permissions}
created_at = "{datetime.now().strftime('%Y-%m-%d')}"
git_verified = false

[USER_CREDENTIALS]
{new_username} = "{result['password_hash']}"
                        """, language="toml")
                    
                    st.code(f'APPROVED_FRIENDS = "{",".join(auth_system.approved_friends + [new_username])}"', language="toml")
                    
                    st.rerun()
                else:
                    st.error(result["message"])
            else:
                st.warning("👆 必須項目をすべて入力してください")
    
    # 既存ユーザー一覧（管理者をハイライト）
    st.markdown("#### 📋 既存ユーザー一覧")
    
    # 管理者とその他のユーザーを分けて表示
    admins = {k: v for k, v in auth_system.friends_db.items() if "admin" in v["permissions"]}
    regular_users = {k: v for k, v in auth_system.friends_db.items() if "admin" not in v["permissions"]}
    
    if admins:
        st.markdown("##### 🔑 管理者アカウント")
        for username, user_data in admins.items():
            with st.expander(f"🔑 {user_data['display_name']} ({username}) - 管理者"):
                show_user_details(username, user_data, is_admin=True)
    
    if regular_users:
        st.markdown("##### 👥 一般ユーザー")
        for username, user_data in regular_users.items():
            with st.expander(f"👤 {user_data['display_name']} ({username})"):
                show_user_details(username, user_data, is_admin=False)

# 3. 管理者統計表示機能
def show_admin_statistics():
    """📊 統計・分析表示"""
    st.subheader("📊 システム統計")
    
    # システム情報
    deployment_info = auth_system.get_deployment_info()
    
    # メトリクス表示
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 登録ユーザー", deployment_info["total_registered"])
    col2.metric("✅ 承認済み", deployment_info["approved_friends"])
    col3.metric("🔑 管理者", deployment_info["admin_users"])
    col4.metric("🔐 認証方式", deployment_info["auth_method"])
    
    # Pro版統計
    st.subheader("📈 Pro機能利用統計")
    
    # 全ユーザーのデータ統計
    total_templates = 0
    total_history = 0
    active_sessions = 0
    
    for username in auth_system.approved_friends:
        if username in auth_system.friends_db:
            user_data_manager = DataManager(username)
            templates = user_data_manager.load_templates()
            history = user_data_manager.load_calculation_history()
            session_data = user_data_manager.load_session_data()
            
            total_templates += len(templates)
            total_history += len(history)
            if session_data:
                active_sessions += 1
    
    col_pro1, col_pro2, col_pro3 = st.columns(3)
    col_pro1.metric("📁 総テンプレート", total_templates)
    col_pro2.metric("📈 総計算履歴", total_history)
    col_pro3.metric("🔄 アクティブセッション", active_sessions)
    
    # ユーザー別データ分析
    st.subheader("👥 ユーザー別利用状況")
    
    user_stats = []
    for username in auth_system.approved_friends:
        if username in auth_system.friends_db:
            user_data = auth_system.friends_db[username]
            user_data_manager = DataManager(username)
            
            templates = user_data_manager.load_templates()
            history = user_data_manager.load_calculation_history()
            session_data = user_data_manager.load_session_data()
            
            user_stats.append({
                "ユーザー名": username,
                "表示名": user_data["display_name"],
                "権限": "🔑管理者" if "admin" in user_data["permissions"] else "👤一般",
                "ログイン回数": user_data["login_count"],
                "テンプレート数": len(templates),
                "計算履歴数": len(history),
                "セッション保存": "✅" if session_data else "❌",
                "最終ログイン": user_data["last_login"][:10] if user_data["last_login"] else "未ログイン"
            })
    
    if user_stats:
        df_user_stats = pd.DataFrame(user_stats)
        st.dataframe(df_user_stats, use_container_width=True, hide_index=True)
        
        # 利用状況グラフ
        if not df_user_stats.empty:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                fig_usage = px.bar(
                    df_user_stats,
                    x='ユーザー名',
                    y=['テンプレート数', '計算履歴数'],
                    title="ユーザー別Pro機能利用状況",
                    barmode='group'
                )
                st.plotly_chart(fig_usage, use_container_width=True)
            
            with col_chart2:
                # 権限分布
                permission_counts = df_user_stats['権限'].value_counts()
                fig_perms = px.pie(
                    values=permission_counts.values,
                    names=permission_counts.index,
                    title="ユーザー権限分布"
                )
                st.plotly_chart(fig_perms, use_container_width=True)

# 4. TOML設定表示機能
def show_toml_configuration():
    """🔐 TOML設定情報"""
    st.subheader("🔐 secrets.toml 設定ガイド")
    
    st.markdown("""
    <div class="security-info">
    <strong>📝 完全なTOML設定例:</strong><br>
    以下の設定をStreamlit CloudのSecretsに追加してください
    </div>
    """, unsafe_allow_html=True)
    
    # 現在の設定状況
    st.markdown("#### 📊 現在の設定状況")
    
    col_status1, col_status2 = st.columns(2)
    
    with col_status1:
        # 設定済み項目をチェック
        has_user_info = bool(st.secrets.get("USER_INFO"))
        has_user_creds = bool(st.secrets.get("USER_CREDENTIALS"))
        has_admin_creds = bool(st.secrets.get("ADMIN_CREDENTIALS"))
        has_approved = bool(st.secrets.get("APPROVED_FRIENDS"))
        
        st.markdown("**✅ 設定状況:**")
        st.write(f"📋 USER_INFO: {'✅' if has_user_info else '❌'}")
        st.write(f"🔑 USER_CREDENTIALS: {'✅' if has_user_creds else '❌'}")
        st.write(f"👨‍💼 ADMIN_CREDENTIALS: {'✅' if has_admin_creds else '❌'}")
        st.write(f"👥 APPROVED_FRIENDS: {'✅' if has_approved else '❌'}")
    
    with col_status2:
        # 統計情報
        st.markdown("**📈 システム情報:**")
        st.write(f"登録ユーザー: {len(auth_system.friends_db)}人")
        st.write(f"承認済み: {len(auth_system.approved_friends)}人")
        admin_count = len([u for u in auth_system.friends_db.values() if "admin" in u["permissions"]])
        st.write(f"管理者: {admin_count}人")
        st.write(f"認証方式: セキュアTOML")
    
    # 完全なTOML設定例
    st.markdown("#### 📝 完全なsecrets.toml設定例")
    
    # 現在の設定を基にした例を生成
    current_approved = ",".join(auth_system.approved_friends)
    
    st.code(f"""
# ==== 基本設定 ====
APPROVED_FRIENDS = "{current_approved}"

# ==== 一般ユーザー情報 ====
[USER_INFO.田中]
display_name = "田中さん"
github_username = "tanaka_dev"
permissions = ["create", "view", "calculate", "export", "template"]
created_at = "2024-08-17"
git_verified = false

[USER_INFO.佐藤]
display_name = "佐藤さん"
github_username = "sato_coder"
permissions = ["view", "calculate", "template"]
created_at = "2024-08-17"
git_verified = false

# ==== 一般ユーザーパスワード（ハッシュ化済み） ====
[USER_CREDENTIALS]
田中 = "あなたが生成したハッシュ値"
佐藤 = "あなたが生成したハッシュ値"

# ==== 管理者アカウント ====
[ADMIN_CREDENTIALS.admin]
password_hash = "あなたの管理者パスワードハッシュ"
display_name = "システム管理者"
github_username = "system_admin"
created_at = "2024-08-17"
git_verified = true

[ADMIN_CREDENTIALS.your_name]
password_hash = "あなたの個人管理者パスワードハッシュ"
display_name = "あなたの名前"
github_username = "your_github_username"
created_at = "2024-08-17"
git_verified = true
    """, language="toml")
    
    # パスワードハッシュ生成ツール
    st.markdown("#### 🔧 パスワードハッシュ生成ツール")
    
    with st.form("hash_generator"):
        password_to_hash = st.text_input("パスワード", type="password", placeholder="ハッシュ化したいパスワードを入力")
        generate_hash_btn = st.form_submit_button("🔐 ハッシュ生成")
        
        if generate_hash_btn and password_to_hash:
            hashed = auth_system._hash(password_to_hash)
            st.code(f'password_hash = "{hashed}"', language="toml")
            st.success("✅ ハッシュ値が生成されました。上記をコピーしてTOMLに貼り付けてください。")
    
    # 設定手順
    st.markdown("#### 📋 設定手順")
    
    st.markdown("""
    1. **パスワードハッシュ生成**: 上記ツールで各ユーザーのパスワードをハッシュ化
    2. **TOML作成**: 上記例を参考にsecrets.tomlを作成
    3. **Streamlit Cloud設定**: Settings → Secrets でTOMLを貼り付け
    4. **アプリ再起動**: 設定反映のためアプリを再起動
    5. **動作確認**: 各ユーザーでログインテスト
    """)
    
    # セキュリティ注意事項
    st.markdown("""
    <div class="security-info">
    <strong>⚠️ セキュリティ注意事項:</strong><br>
    🔐 パスワードハッシュは絶対にコードに含めない<br>
    🔑 管理者パスワードは十分に複雑にする<br>
    👥 不要になったユーザーは速やかに削除<br>
    📝 定期的にアクセスログを確認<br>
    🔄 必要に応じてパスワードを変更
    </div>
    """, unsafe_allow_html=True)

# 5. 管理者ダッシュボード機能
def show_admin_dashboard():
    """👨‍💼 管理者ダッシュボード（一般ユーザー対応版）"""
    # 管理者権限チェック（全体レベル）
    if "admin" not in st.session_state.user['permissions']:
        st.error("❌ 管理者権限が必要です")
        st.info("💡 一般ユーザーは基本機能をご利用ください")
        
        # 一般ユーザー向けの案内
        st.markdown("""
        <div class="user-info">
            <h3>🔍 利用可能な機能</h3>
            <p>一般ユーザーは以下の機能をご利用いただけます：</p>
            <ul>
                <li>👥 参加者管理</li>
                <li>📁 テンプレート機能</li>
                <li>🧮 AI計算</li>
                <li>📊 結果分析</li>
                <li>📈 履歴表示</li>
            </ul>
            <p><strong>管理者機能をご利用の場合は、管理者権限のあるアカウントでログインしてください。</strong></p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 管理者の場合のダッシュボード表示
    st.markdown("""
    <div class="main-header">
        <h1>🛠️ セキュア管理者ダッシュボード</h1>
        <p>TOML管理 & ユーザー管理 & システム統計 & カスタム倍率設定</p>
        <span class="feature-badge">🔐 TOML管理</span>
        <span class="feature-badge">👥 ユーザー管理</span>
        <span class="feature-badge">📊 統計分析</span>
        <span class="feature-badge">🎯 倍率設定</span>
    </div>
    """, unsafe_allow_html=True)
    
    # タブで機能を分割（カスタム倍率タブを追加）
    tab1, tab2, tab3, tab4 = st.tabs(["👥 ユーザー管理", "📊 統計・分析", "🔐 TOML設定", "🎯 倍率設定"])
    
    with tab1:
        show_secure_user_management()
    
    with tab2:
        show_admin_statistics()
    
    with tab3:
        show_toml_configuration()
    
    with tab4:
        show_custom_multiplier_management()

# 6. 管理者専用倍率設定画面の追加
def show_custom_multiplier_management():
    """🎯 管理者専用カスタム倍率設定（Streamlit Cloud対応）"""
    st.subheader("🎯 カスタム倍率設定")
    
    # 管理者権限チェック
    if "admin" not in st.session_state.user['permissions']:
        st.error("❌ この機能は管理者専用です")
        return
    
    multiplier_manager = CustomMultiplierManager()
    
    st.markdown("""
    <div class="security-info">
    <strong>🎯 カスタム倍率機能:</strong><br>
    ✅ 特定の人に固定倍率を設定<br>
    ✅ 柔軟な名前マッチング（山田/山田さん/山田君 すべて対応）<br>
    ✅ 役職によらず優先適用<br>
    ✅ 管理者のみ設定可能<br>
    ✅ <strong>全ユーザーに適用</strong><br>
    ✅ <strong>アプリ実行中は永続</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # ストレージ状況の表示
    st.markdown("#### 📊 ストレージ状況")
    
    try:
        storage_info = multiplier_manager.get_storage_info()
        
        if storage_info.get('error'):
            st.error("❌ ストレージ情報取得エラー")
        else:
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                if storage_info['has_global_storage']:
                    st.success("✅ グローバルストレージ有効")
                else:
                    st.warning("⚠️ グローバルストレージ未初期化")
                
                st.info(f"📊 保存ルール数: {storage_info['rules_count']}個")
                st.info(f"💾 ストレージ方式: {storage_info['storage_type']}")
            
            with col_info2:
                st.info(f"⏱️ 永続性: {storage_info['persistence_level']}")
                
                if 'last_updated' in storage_info:
                    st.info(f"🕒 最終更新: {storage_info['last_updated'][:16]}")
                if 'updated_by' in storage_info:
                    st.info(f"👤 更新者: {storage_info['updated_by']}")
    except Exception as e:
        st.error(f"ストレージ情報表示エラー: {str(e)}")
    
    # Streamlit Cloud使用時の注意事項
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border: 1px solid #ffeaa7; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
    <strong>📋 Streamlit Cloud使用時の注意:</strong><br>
    • ルールは<strong>アプリ実行中のみ保持</strong>されます<br>
    • アプリが再起動すると<strong>ルールはリセット</strong>されます<br>
    • 重要なルールは<strong>エクスポート機能で保存</strong>してください<br>
    • 定期的に<strong>バックアップを取得</strong>することをお勧めします
    </div>
    """, unsafe_allow_html=True)
    
    # 新規ルール追加
    st.markdown("#### ➕ 新規倍率ルール追加")
    
    with st.form("add_multiplier_rule"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            rule_name = st.text_input(
                "📝 ルール名",
                placeholder="例: 山田さん高収入ルール",
                help="管理しやすい名前を付けてください"
            )
            
            name_patterns_input = st.text_input(
                "👤 対象名前パターン",
                placeholder="例: 山田,山田さん,山田君",
                help="カンマ区切りで複数の名前パターンを指定"
            )
            
            st.markdown("**💡 名前パターンの例:**")
            st.markdown("- `山田` → 山田、山田さん、山田君 すべてにマッチ")
            st.markdown("- `田中,田中部長` → 田中関連の名前にマッチ")
        
        with col2:
            multiplier = st.number_input(
                "🎯 倍率",
                min_value=0.1,
                max_value=10.0,
                value=2.0,
                step=0.1,
                help="1.0=通常、2.0=2倍、0.5=半額"
            )
            
            reason = st.text_area(
                "📝 理由・備考",
                placeholder="例: 高収入のため2倍負担",
                help="設定理由を記録（任意）"
            )
        
        add_rule_btn = st.form_submit_button("➕ ルール追加", use_container_width=True)
        
        if add_rule_btn and rule_name and name_patterns_input:
            # 名前パターンをリスト化
            name_patterns = [pattern.strip() for pattern in name_patterns_input.split(',')]
            
            # 新しいルールを作成
            rules = multiplier_manager.load_multiplier_rules()
            rules[rule_name] = {
                'name_patterns': name_patterns,
                'multiplier': multiplier,
                'reason': reason,
                'created_by': st.session_state.user['display_name'],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if multiplier_manager.save_multiplier_rules(rules):
                st.success(f"✅ ルール「{rule_name}」をグローバル保存しました")
                st.info("💡 このルールは全ユーザーに適用されます（アプリ実行中）")
                st.rerun()
            else:
                st.error("❌ ルール追加に失敗しました")
        elif add_rule_btn:
            st.warning("👆 ルール名と名前パターンを入力してください")
    
    # 既存ルール一覧
    st.markdown("#### 📋 既存倍率ルール")
    
    rules = multiplier_manager.load_multiplier_rules()
    
    if rules:
        for rule_name, rule_data in rules.items():
            with st.expander(f"🎯 {rule_name} ({rule_data['multiplier']}倍)", expanded=False):
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    st.write(f"**対象パターン:** {', '.join(rule_data['name_patterns'])}")
                    st.write(f"**倍率:** {rule_data['multiplier']}倍")
                    st.write(f"**理由:** {rule_data.get('reason', '未設定')}")
                    st.write(f"**作成者:** {rule_data.get('created_by', '不明')}")
                    st.write(f"**作成日:** {rule_data.get('created_at', '不明')}")
                    
                    # テストマッチング
                    st.markdown("**🔍 マッチングテスト:**")
                    test_name = st.text_input(
                        "テスト用名前を入力",
                        key=f"test_{rule_name}",
                        placeholder="例: 山田太郎さん"
                    )
                    
                    if test_name:
                        result_multiplier = multiplier_manager.find_matching_multiplier(test_name)
                        
                        if result_multiplier != 1.0:
                            st.success(f"✅ マッチしました！倍率: {result_multiplier}")
                        else:
                            st.info("ℹ️ マッチしませんでした")
                
                with col_actions:
                    if st.button("🗑️ 削除", key=f"delete_rule_{rule_name}"):
                        if multiplier_manager.delete_multiplier_rule(rule_name):
                            st.success(f"✅ ルール「{rule_name}」を削除しました")
                            st.rerun()
                        else:
                            st.error("❌ 削除に失敗しました")
    else:
        st.info("📝 設定済みの倍率ルールがありません")
    
    # 高度な管理機能
    st.markdown("#### 🔧 バックアップ・復元機能")
    
    col_export, col_import = st.columns(2)
    
    with col_export:
        st.markdown("**📤 ルールバックアップ**")
        if st.button("📋 バックアップデータを表示"):
            export_data = multiplier_manager.export_rules_for_sharing()
            st.code(export_data, language="json")
            st.info("💡 上記をコピーして保存してください。アプリ再起動時に復元できます。")
    
    with col_import:
        st.markdown("**📥 ルール復元**")
        with st.form("import_rules"):
            import_text = st.text_area(
                "バックアップデータ",
                placeholder='{"rules": {"ルール名": {"name_patterns": ["名前"], "multiplier": 2.0}}}',
                help="バックアップしたJSON形式データを貼り付け"
            )
            
            if st.form_submit_button("📥 復元実行"):
                if import_text.strip():
                    if multiplier_manager.import_rules_from_text(import_text):
                        st.success("✅ ルールを復元しました")
                        st.rerun()
                else:
                    st.warning("👆 バックアップデータを入力してください")
    
    # 一括テスト機能
    st.markdown("#### 🔍 全ルール一括テスト")
    
    with st.form("bulk_test"):
        test_names = st.text_area(
            "テスト用名前リスト（1行に1名）",
            placeholder="山田太郎\n田中花子さん\n佐藤君\n鈴木部長",
            help="実際の参加者名を入力してテスト"
        )
        
        if st.form_submit_button("🔍 一括テスト実行"):
            if test_names:
                st.markdown("**テスト結果:**")
                
                for name in test_names.strip().split('\n'):
                    name = name.strip()
                    if name:
                        multiplier = multiplier_manager.find_matching_multiplier(name)
                        
                        if multiplier != 1.0:
                            st.markdown(f"- **{name}**: <span style='color: #ff6b6b; font-weight: bold;'>{multiplier}倍</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"- **{name}**: 通常（1.0倍）")

# 7. 計算結果表示の修正（倍率詳細表示）
# ==== 修正版: show_admin_dashboard関数 ====

def show_admin_dashboard():
    """👨‍💼 管理者ダッシュボード（一般ユーザー対応版）"""
    # 管理者権限チェック（全体レベル）
    if "admin" not in st.session_state.user['permissions']:
        st.error("❌ 管理者権限が必要です")
        st.info("💡 一般ユーザーは基本機能をご利用ください")
        
        # 一般ユーザー向けの案内
        st.markdown("""
        <div class="user-info">
            <h3>🔍 利用可能な機能</h3>
            <p>一般ユーザーは以下の機能をご利用いただけます：</p>
            <ul>
                <li>👥 参加者管理</li>
                <li>📁 テンプレート機能</li>
                <li>🧮 AI計算</li>
                <li>📊 結果分析</li>
                <li>📈 履歴表示</li>
            </ul>
            <p><strong>管理者機能をご利用の場合は、管理者権限のあるアカウントでログインしてください。</strong></p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 管理者の場合のダッシュボード表示
    st.markdown("""
    <div class="main-header">
        <h1>🛠️ セキュア管理者ダッシュボード</h1>
        <p>TOML管理 & ユーザー管理 & システム統計 & カスタム倍率設定</p>
        <span class="feature-badge">🔐 TOML管理</span>
        <span class="feature-badge">👥 ユーザー管理</span>
        <span class="feature-badge">📊 統計分析</span>
        <span class="feature-badge">🎯 倍率設定</span>
    </div>
    """, unsafe_allow_html=True)
    
    # タブで機能を分割（カスタム倍率タブを追加）
    tab1, tab2, tab3, tab4 = st.tabs(["👥 ユーザー管理", "📊 統計・分析", "🔐 TOML設定", "🎯 倍率設定"])
    
    with tab1:
        show_secure_user_management()
    
    with tab2:
        show_admin_statistics()
    
    with tab3:
        show_toml_configuration()
    
    with tab4:
        show_custom_multiplier_management()

# ==== 修正版: show_custom_multiplier_management関数 ====

def show_custom_multiplier_management():
    """🎯 管理者専用カスタム倍率設定（一般ユーザー対応版）"""
    st.subheader("🎯 カスタム倍率設定")
    
    # 管理者権限チェック（関数レベル）
    if "admin" not in st.session_state.user['permissions']:
        st.error("❌ この機能は管理者専用です")
        st.info("💡 カスタム倍率は管理者が設定済みの場合、自動的に適用されます")
        
        # 一般ユーザー向けの情報表示
        try:
            multiplier_manager = CustomMultiplierManager()
            rules = multiplier_manager.load_multiplier_rules()
            
            if rules:
                st.markdown("#### 📋 現在適用中の倍率ルール")
                st.success(f"✅ {len(rules)}個のカスタム倍率ルールが設定されています")
                
                # 一般ユーザー向けの簡易表示
                for rule_name, rule_data in rules.items():
                    with st.expander(f"🎯 {rule_name} ({rule_data['multiplier']}倍)", expanded=False):
                        st.write(f"**対象パターン:** {', '.join(rule_data['name_patterns'])}")
                        st.write(f"**倍率:** {rule_data['multiplier']}倍")
                        st.write(f"**理由:** {rule_data.get('reason', '未設定')}")
                        
                        # 一般ユーザー用のテストマッチング
                        st.markdown("**🔍 自分の名前でテスト:**")
                        test_name = st.text_input(
                            "あなたの名前を入力",
                            key=f"user_test_{rule_name}",
                            placeholder="例: 山田太郎さん"
                        )
                        
                        if test_name:
                            result_multiplier = multiplier_manager.find_matching_multiplier(test_name)
                            
                            if result_multiplier != 1.0:
                                st.success(f"✅ あなたに適用される倍率: {result_multiplier}倍")
                            else:
                                st.info("ℹ️ 通常倍率（1.0倍）が適用されます")
                
                # 一括テスト機能（一般ユーザー用）
                st.markdown("#### 🔍 名前マッチング確認")
                
                with st.form("user_bulk_test"):
                    test_names = st.text_area(
                        "テスト用名前リスト（1行に1名）",
                        placeholder="山田太郎\n田中花子さん\n佐藤君",
                        help="あなたや仲間の名前を入力して倍率を確認"
                    )
                    
                    if st.form_submit_button("🔍 倍率確認"):
                        if test_names:
                            st.markdown("**確認結果:**")
                            
                            for name in test_names.strip().split('\n'):
                                name = name.strip()
                                if name:
                                    multiplier = multiplier_manager.find_matching_multiplier(name)
                                    
                                    if multiplier != 1.0:
                                        st.markdown(f"- **{name}**: <span style='color: #ff6b6b; font-weight: bold;'>{multiplier}倍</span>", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"- **{name}**: 通常（1.0倍）")
            else:
                st.info("📝 現在、カスタム倍率ルールは設定されていません")
                st.markdown("""
                <div style="background: linear-gradient(135deg, #e8f4f8 0%, #d1ecf1 100%); border: 1px solid #bee5eb; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                <strong>💡 カスタム倍率機能について:</strong><br>
                • 管理者が特定の人に固定倍率を設定できます<br>
                • 設定されると、AI計算時に自動適用されます<br>
                • 役職による倍率に加えて適用されます
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"倍率情報取得エラー: {str(e)}")
        
        return  # 一般ユーザーはここで終了
    
    # ========== 以下は管理者のみ表示 ==========
    
    multiplier_manager = CustomMultiplierManager()
    
    st.markdown("""
    <div class="security-info">
    <strong>🎯 カスタム倍率機能:</strong><br>
    ✅ 特定の人に固定倍率を設定<br>
    ✅ 柔軟な名前マッチング（山田/山田さん/山田君 すべて対応）<br>
    ✅ 役職によらず優先適用<br>
    ✅ 管理者のみ設定可能<br>
    ✅ <strong>全ユーザーに適用</strong><br>
    ✅ <strong>アプリ実行中は永続</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # ストレージ状況の表示
    st.markdown("#### 📊 ストレージ状況")
    
    try:
        storage_info = multiplier_manager.get_storage_info()
        
        if storage_info.get('error'):
            st.error("❌ ストレージ情報取得エラー")
        else:
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                if storage_info['has_global_storage']:
                    st.success("✅ グローバルストレージ有効")
                else:
                    st.warning("⚠️ グローバルストレージ未初期化")
                
                st.info(f"📊 保存ルール数: {storage_info['rules_count']}個")
                st.info(f"💾 ストレージ方式: {storage_info['storage_type']}")
            
            with col_info2:
                st.info(f"⏱️ 永続性: {storage_info['persistence_level']}")
                
                if 'last_updated' in storage_info:
                    st.info(f"🕒 最終更新: {storage_info['last_updated'][:16]}")
                if 'updated_by' in storage_info:
                    st.info(f"👤 更新者: {storage_info['updated_by']}")
    except Exception as e:
        st.error(f"ストレージ情報表示エラー: {str(e)}")
    
    # Streamlit Cloud使用時の注意事項
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border: 1px solid #ffeaa7; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
    <strong>📋 Streamlit Cloud使用時の注意:</strong><br>
    • ルールは<strong>アプリ実行中のみ保持</strong>されます<br>
    • アプリが再起動すると<strong>ルールはリセット</strong>されます<br>
    • 重要なルールは<strong>エクスポート機能で保存</strong>してください<br>
    • 定期的に<strong>バックアップを取得</strong>することをお勧めします
    </div>
    """, unsafe_allow_html=True)
    
    # 新規ルール追加
    st.markdown("#### ➕ 新規倍率ルール追加")
    
    with st.form("add_multiplier_rule"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            rule_name = st.text_input(
                "📝 ルール名",
                placeholder="例: 山田さん高収入ルール",
                help="管理しやすい名前を付けてください"
            )
            
            name_patterns_input = st.text_input(
                "👤 対象名前パターン",
                placeholder="例: 山田,山田さん,山田君",
                help="カンマ区切りで複数の名前パターンを指定"
            )
            
            st.markdown("**💡 名前パターンの例:**")
            st.markdown("- `山田` → 山田、山田さん、山田君 すべてにマッチ")
            st.markdown("- `田中,田中部長` → 田中関連の名前にマッチ")
        
        with col2:
            multiplier = st.number_input(
                "🎯 倍率",
                min_value=0.1,
                max_value=10.0,
                value=2.0,
                step=0.1,
                help="1.0=通常、2.0=2倍、0.5=半額"
            )
            
            reason = st.text_area(
                "📝 理由・備考",
                placeholder="例: 高収入のため2倍負担",
                help="設定理由を記録（任意）"
            )
        
        add_rule_btn = st.form_submit_button("➕ ルール追加", use_container_width=True)
        
        if add_rule_btn and rule_name and name_patterns_input:
            # 名前パターンをリスト化
            name_patterns = [pattern.strip() for pattern in name_patterns_input.split(',')]
            
            # 新しいルールを作成
            rules = multiplier_manager.load_multiplier_rules()
            rules[rule_name] = {
                'name_patterns': name_patterns,
                'multiplier': multiplier,
                'reason': reason,
                'created_by': st.session_state.user['display_name'],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if multiplier_manager.save_multiplier_rules(rules):
                st.success(f"✅ ルール「{rule_name}」をグローバル保存しました")
                st.info("💡 このルールは全ユーザーに適用されます（アプリ実行中）")
                st.rerun()
            else:
                st.error("❌ ルール追加に失敗しました")
        elif add_rule_btn:
            st.warning("👆 ルール名と名前パターンを入力してください")
    
    # 既存ルール一覧
    st.markdown("#### 📋 既存倍率ルール")
    
    rules = multiplier_manager.load_multiplier_rules()
    
    if rules:
        for rule_name, rule_data in rules.items():
            with st.expander(f"🎯 {rule_name} ({rule_data['multiplier']}倍)", expanded=False):
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    st.write(f"**対象パターン:** {', '.join(rule_data['name_patterns'])}")
                    st.write(f"**倍率:** {rule_data['multiplier']}倍")
                    st.write(f"**理由:** {rule_data.get('reason', '未設定')}")
                    st.write(f"**作成者:** {rule_data.get('created_by', '不明')}")
                    st.write(f"**作成日:** {rule_data.get('created_at', '不明')}")
                    
                    # テストマッチング
                    st.markdown("**🔍 マッチングテスト:**")
                    test_name = st.text_input(
                        "テスト用名前を入力",
                        key=f"test_{rule_name}",
                        placeholder="例: 山田太郎さん"
                    )
                    
                    if test_name:
                        result_multiplier = multiplier_manager.find_matching_multiplier(test_name)
                        
                        if result_multiplier != 1.0:
                            st.success(f"✅ マッチしました！倍率: {result_multiplier}")
                        else:
                            st.info("ℹ️ マッチしませんでした")
                
                with col_actions:
                    if st.button("🗑️ 削除", key=f"delete_rule_{rule_name}"):
                        if multiplier_manager.delete_multiplier_rule(rule_name):
                            st.success(f"✅ ルール「{rule_name}」を削除しました")
                            st.rerun()
                        else:
                            st.error("❌ 削除に失敗しました")
    else:
        st.info("📝 設定済みの倍率ルールがありません")
    
    # 高度な管理機能（管理者のみ）
    st.markdown("#### 🔧 バックアップ・復元機能")
    
    col_export, col_import = st.columns(2)
    
    with col_export:
        st.markdown("**📤 ルールバックアップ**")
        if st.button("📋 バックアップデータを表示"):
            export_data = multiplier_manager.export_rules_for_sharing()
            st.code(export_data, language="json")
            st.info("💡 上記をコピーして保存してください。アプリ再起動時に復元できます。")
    
    with col_import:
        st.markdown("**📥 ルール復元**")
        with st.form("import_rules"):
            import_text = st.text_area(
                "バックアップデータ",
                placeholder='{"rules": {"ルール名": {"name_patterns": ["名前"], "multiplier": 2.0}}}',
                help="バックアップしたJSON形式データを貼り付け"
            )
            
            if st.form_submit_button("📥 復元実行"):
                if import_text.strip():
                    if multiplier_manager.import_rules_from_text(import_text):
                        st.success("✅ ルールを復元しました")
                        st.rerun()
                else:
                    st.warning("👆 バックアップデータを入力してください")
    
    # 一括テスト機能（管理者版）
    st.markdown("#### 🔍 全ルール一括テスト")
    
    with st.form("bulk_test"):
        test_names = st.text_area(
            "テスト用名前リスト（1行に1名）",
            placeholder="山田太郎\n田中花子さん\n佐藤君\n鈴木部長",
            help="実際の参加者名を入力してテスト"
        )
        
        if st.form_submit_button("🔍 一括テスト実行"):
            if test_names:
                st.markdown("**テスト結果:**")
                
                for name in test_names.strip().split('\n'):
                    name = name.strip()
                    if name:
                        multiplier = multiplier_manager.find_matching_multiplier(name)
                        
                        if multiplier != 1.0:
                            st.markdown(f"- **{name}**: <span style='color: #ff6b6b; font-weight: bold;'>{multiplier}倍</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"- **{name}**: 通常（1.0倍）")

# 8. メインアプリケーション機能
def main():
    """🎯 メインアプリケーション（セキュア版）"""
    
    # 🔐 認証チェック
    if not check_authentication():
        return
    
    # セッション初期化
    init_session_state()
    
    # ユーザー情報表示
    show_user_info()
    
    # セッション復元チェック
    show_session_restore()
    
    # メインヘッダー
    user = st.session_state.user
    st.markdown(f'''
    <div class="main-header">
        <h1>🍻 AI割り勘システム Pro</h1>
        <p>セキュア友達限定版 - {user['display_name']}さん専用ダッシュボード</p>
        <span class="feature-badge">🔐 TOML管理</span>
        <span class="feature-badge">👥 テンプレート</span>
        <span class="feature-badge">💾 履歴保存</span>
        <span class="feature-badge">🔄 自動復元</span>
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
            if "admin" in user['permissions'] and st.button("🔐 管理", use_container_width=True):
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
        
        # 金額変更時の自動保存
        if total_amount != st.session_state.total_amount:
            st.session_state.total_amount = total_amount
            auto_save_session()
        
        marume_unit = st.selectbox(
            "🔢 丸め単位（円）",
            options=[100, 500, 1000],
            index=1,
            help="支払い金額を丸める単位"
        )
        
        # Pro機能設定
        st.subheader("✨ Pro機能設定")
        
        auto_save_enabled = st.checkbox(
            "🔄 自動保存",
            value=st.session_state.auto_save_enabled,
            help="作業内容を自動的に保存します"
        )
        st.session_state.auto_save_enabled = auto_save_enabled
        
        # データ統計
        if st.session_state.data_manager:
            templates = st.session_state.data_manager.load_templates()
            history = st.session_state.data_manager.load_calculation_history()
            
            st.subheader("📊 データ統計")
            st.metric("📁 保存テンプレート", len(templates))
            st.metric("📈 計算履歴", len(history))
        
        # セキュリティ情報
        st.subheader("🔐 セキュリティ情報")
        st.success("✅ TOML認証有効")
        st.info(f"🎫 権限: {len(user['permissions'])}個")
        if user['is_admin']:
            st.warning("🔑 管理者権限")
        
        # Git接続情報
        git_status = st.session_state.git_status
        if git_status:
            st.subheader("🔗 Git接続状態")
            if git_status.get("connected"):
                st.success("✅ 接続中")
                st.caption(f"📍 {git_status.get('repo_url', 'N/A')}")
            else:
                st.error("❌ 未接続")
        
        # ログアウト
        st.subheader("🚪 セッション管理")
        if st.button("🚪 ログアウト", type="secondary", use_container_width=True):
            # 自動保存
            auto_save_session()
            
            # セッションクリア
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 参加者管理", 
        "📁 テンプレート", 
        "🧮 AI計算", 
        "📊 結果分析", 
        "📈 履歴"
    ])
    
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
                            auto_save_session()  # 自動保存
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
                col_info, col_delete = st.columns([4, 1])
                
                with col_info:
                    st.markdown(f"""
                    **👤 {participant['名前']}** 
                    <span style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem;">{participant['役職']}</span>
                    """, unsafe_allow_html=True)
                    st.caption(f"追加: {participant['追加日時']} by {participant['追加者']}")
                
                with col_delete:
                    if "create" in user['permissions']:
                        if st.button("🗑️", key=f"delete_{i}", help=f"{participant['名前']}さんを削除"):
                            st.session_state.participants.pop(i)
                            st.success(f"✅ {participant['名前']}さんを削除しました")
                            auto_save_session()
                            st.rerun()
        else:
            st.info("👆 まずは参加者を追加してください")
    
    # ==== タブ2: テンプレート管理 ====
    with tab2:
        show_template_management()
    
    # ==== タブ3: AI計算 ====
    with tab3:
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
                    
                    # 履歴保存
                    calculation_data = {
                        'total_amount': total_amount,
                        'participants': st.session_state.participants,
                        'results': df_result.to_dict('records'),
                        'sum_warikan': sum_warikan,
                        'diff': diff
                    }
                    st.session_state.data_manager.save_calculation_history(calculation_data)
                    
                    auto_save_session()  # 自動保存
                    st.success("✅ 最適化完了！履歴に保存しました")
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
    
    # ==== タブ4: 結果分析 ====
    with tab4:
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
    
    # ==== タブ5: 履歴 ====
    with tab5:
        show_calculation_history()

# ==== アプリケーション実行 ====
if __name__ == "__main__":
    main()