# ==== Streamlit Web版 AI割り勘システム ====
# ブラウザで使える日本語対応割り勘計算ツール

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
import sqlite3
from datetime import datetime
import random
import json
import os

# ==== フォント設定（Web版） ====
def setup_web_fonts():
    """Web版フォント設定"""
    try:
        # 日本語フォント候補
        fonts_to_try = [
            'Yu Gothic UI', 'Yu Gothic', 'Meiryo', 'MS Gothic',
            'Hiragino Sans', 'Noto Sans CJK JP', 'DejaVu Sans'
        ]
        
        for font in fonts_to_try:
            try:
                plt.rcParams['font.family'] = font
                # テスト描画
                fig, ax = plt.subplots(figsize=(1, 1))
                ax.text(0.5, 0.5, '日本語', fontsize=10)
                plt.close(fig)
                
                st.success(f"✅ フォント設定: {font}")
                return font, True
            except:
                continue
        
        # フォールバック
        plt.rcParams['font.family'] = 'DejaVu Sans'
        st.warning("⚠️ 英語フォントを使用: DejaVu Sans")
        return 'DejaVu Sans', False
        
    except Exception as e:
        st.error(f"フォント設定エラー: {e}")
        return 'DejaVu Sans', False

# フォント設定実行
current_font, is_japanese_font = setup_web_fonts()
plt.rcParams['axes.unicode_minus'] = False

# ==== ページ設定 ====
st.set_page_config(
    page_title="🍻 AI割り勘システム",
    page_icon="🍻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==== CSS カスタマイズ ====
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .participant-card {
        background: #e8f4f8;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.3rem 0;
        border-left: 3px solid #4ecdc4;
    }
    .result-highlight {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==== データベース管理 ====
@st.cache_resource
def init_database():
    """データベース初期化"""
    conn = sqlite3.connect('web_warikan.db', check_same_thread=False)
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS web_sessions (
            session_id TEXT PRIMARY KEY,
            total_amount INTEGER,
            created_at TEXT,
            participants_json TEXT,
            results_json TEXT
        )
    ''')
    
    conn.commit()
    return conn

# ==== セッション状態管理 ====
def init_session_state():
    """セッション状態初期化"""
    if 'participants' not in st.session_state:
        st.session_state.participants = []
    if 'total_amount' not in st.session_state:
        st.session_state.total_amount = 10000
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}"
    if 'calculation_results' not in st.session_state:
        st.session_state.calculation_results = None

# ==== AI最適化エンジン ====
class WebWarikanOptimizer:
    def __init__(self):
        self.default_params = {
            '事業部長': 1.6, '部長': 1.4, '課長': 1.2, '主査': 1.1, '担当': 1.0
        }
    
    def optimize_warikan(self, df_participants, total_amount, marume=500):
        """Web版最適化エンジン"""
        if df_participants.empty:
            return None, None, None
        
        best_params = self.default_params.copy()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for iteration in range(20):  # Web版は少し多めに
            # 進捗表示
            progress = (iteration + 1) / 20
            progress_bar.progress(progress)
            status_text.text(f"🤖 AI最適化中... {iteration+1}/20")
            
            # 計算
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
                status_text.success("✅ 最適化完了！")
                break
            
            # パラメータ調整
            adjustment = 0.015 if abs(diff) > 1000 else 0.008
            
            if diff > 0:
                for role in ['事業部長', '部長', '課長', '主査']:
                    if role in best_params:
                        best_params[role] *= (1 - adjustment)
            else:
                for role in ['事業部長', '部長', '課長', '主査']:
                    if role in best_params:
                        best_params[role] *= (1 + adjustment)
        
        # プログレス非表示
        progress_bar.empty()
        status_text.empty()
        
        return df_calc, sum_warikan, diff, best_params

# ==== 可視化システム ====
class WebChartGenerator:
    
    @staticmethod
    def create_interactive_charts(df_result, total_amount, sum_warikan):
        """Plotlyインタラクティブグラフ"""
        
        # カラーマップ
        role_colors = {
            '事業部長': '#FF6B6B', '部長': '#4ECDC4', '課長': '#45B7D1',
            '主査': '#96CEB4', '担当': '#FFEAA7'
        }
        
        # 4つのサブプロット作成
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('個人別負担額', '役職別平均負担額', '負担額分布', '比率分析'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "scatter"}]]
        )
        
        # 1. 個人別負担額
        colors_list = [role_colors.get(role, '#95A5A6') for role in df_result['役職']]
        fig.add_trace(
            go.Bar(
                x=df_result['負担額_丸め'],
                y=df_result['名前'],
                orientation='h',
                marker_color=colors_list,
                text=[f'{int(x):,}円' for x in df_result['負担額_丸め']],
                textposition='outside',
                name='個人別'
            ),
            row=1, col=1
        )
        
        # 2. 役職別平均
        role_avg = df_result.groupby('役職')['負担額_丸め'].mean().sort_values(ascending=False)
        fig.add_trace(
            go.Bar(
                x=role_avg.index,
                y=role_avg.values,
                marker_color=[role_colors.get(role, '#95A5A6') for role in role_avg.index],
                text=[f'{int(x):,}円' for x in role_avg.values],
                textposition='outside',
                name='役職別平均'
            ),
            row=1, col=2
        )
        
        # 3. 負担額分布（円グラフ）
        fig.add_trace(
            go.Pie(
                labels=df_result['名前'],
                values=df_result['負担額_丸め'],
                marker_colors=colors_list,
                textinfo='label+percent+value',
                texttemplate='%{label}<br>%{percent}<br>%{value:,}円',
                name='分布'
            ),
            row=2, col=1
        )
        
        # 4. 比率分析
        fig.add_trace(
            go.Scatter(
                x=df_result['役職'],
                y=df_result['負担額_丸め'],
                mode='markers+text',
                marker=dict(
                    size=[15]*len(df_result),
                    color=colors_list,
                    line=dict(width=2, color='white')
                ),
                text=df_result['名前'],
                textposition='top center',
                name='比率分析'
            ),
            row=2, col=2
        )
        
        # レイアウト調整
        fig.update_layout(
            height=800,
            title=f'割り勘分析ダッシュボード<br>合計: {sum_warikan:,}円 (目標: {total_amount:,}円)',
            showlegend=False,
            font=dict(family=current_font, size=12)
        )
        
        return fig
    
    @staticmethod
    def create_matplotlib_chart(df_result, total_amount, sum_warikan):
        """matplotlib日本語グラフ"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # フォント明示指定
        font_props = {'fontfamily': current_font, 'fontsize': 10}
        title_props = {'fontfamily': current_font, 'fontsize': 12, 'fontweight': 'bold'}
        
        # カラー設定
        role_colors = {
            '事業部長': '#FF6B6B', '部長': '#4ECDC4', '課長': '#45B7D1',
            '主査': '#96CEB4', '担当': '#FFEAA7'
        }
        colors = [role_colors.get(role, '#95A5A6') for role in df_result['役職']]
        
        # 1. 個人別負担額
        y_pos = np.arange(len(df_result))
        bars1 = ax1.barh(y_pos, df_result['負担額_丸め'], color=colors, alpha=0.8)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels([f"{name}\n({role})" for name, role in 
                            zip(df_result['名前'], df_result['役職'])], **font_props)
        ax1.set_xlabel('負担額 (円)', **font_props)
        ax1.set_title('個人別負担額', **title_props)
        
        # 金額ラベル
        for bar, amount in zip(bars1, df_result['負担額_丸め']):
            ax1.text(bar.get_width() + max(df_result['負担額_丸め']) * 0.01,
                    bar.get_y() + bar.get_height()/2,
                    f'{int(amount):,}円', ha='left', va='center', **font_props)
        
        # 2. 役職別平均
        role_avg = df_result.groupby('役職')['負担額_丸め'].mean().sort_values(ascending=False)
        bars2 = ax2.bar(range(len(role_avg)), role_avg.values,
                       color=[role_colors.get(role, '#95A5A6') for role in role_avg.index])
        ax2.set_xticks(range(len(role_avg)))
        ax2.set_xticklabels(role_avg.index, rotation=45, ha='right', **font_props)
        ax2.set_ylabel('平均負担額 (円)', **font_props)
        ax2.set_title('役職別平均負担額', **title_props)
        
        for bar, amount in zip(bars2, role_avg.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(role_avg) * 0.02,
                    f'{int(amount):,}円', ha='center', va='bottom', **font_props)
        
        # 3. 円グラフ
        wedges, texts, autotexts = ax3.pie(df_result['負担額_丸め'], 
                                          labels=df_result['名前'],
                                          colors=colors,
                                          autopct='%1.1f%%',
                                          startangle=90)
        ax3.set_title('負担額分布', **title_props)
        
        # 円グラフのフォント設定
        for text in texts:
            text.set_fontfamily(current_font)
        for autotext in autotexts:
            autotext.set_fontfamily(current_font)
        
        # 4. 統計サマリ
        ax4.axis('off')
        stats_text = f"""統計サマリ

目標金額: {total_amount:,}円
計算後合計: {sum_warikan:,}円
差額: {sum_warikan - total_amount:+,}円

参加者数: {len(df_result)}人
平均負担額: {int(df_result['負担額_丸め'].mean()):,}円
最高負担額: {int(df_result['負担額_丸め'].max()):,}円
最低負担額: {int(df_result['負担額_丸め'].min()):,}円

フォント: {current_font}
日本語対応: {'✅' if is_japanese_font else '❌'}"""
        
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, 
                fontsize=12, verticalalignment='top', **font_props)
        
        # メインタイトル
        fig.suptitle(f'割り勘計算結果詳細分析\nセッション: {st.session_state.session_id[-8:]}', 
                    fontsize=16, fontweight='bold', fontfamily=current_font)
        
        plt.tight_layout()
        return fig

# ==== メイン Web アプリ ====
def main():
    # セッション初期化
    init_session_state()
    db_conn = init_database()
    
    # ヘッダー
    st.markdown('<div class="main-header"><h1>🍻 AI割り勘システム Web版</h1><p>日本語フォント対応 × リアルタイム計算 × インタラクティブ可視化</p></div>', unsafe_allow_html=True)
    
    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # フォント情報
        st.info(f"🔤 フォント: {current_font}\n📝 日本語: {'✅' if is_japanese_font else '❌'}")
        
        # 基本設定
        st.session_state.total_amount = st.number_input(
            "💰 合計金額（円）",
            min_value=100,
            max_value=1000000,
            value=st.session_state.total_amount,
            step=500
        )
        
        marume_unit = st.selectbox("🔄 丸め単位", [500, 1000], index=0)
        
        # セッション情報
        st.write("📋 セッション情報")
        st.text(f"ID: {st.session_state.session_id[-8:]}")
        st.text(f"参加者: {len(st.session_state.participants)}人")
        
        # データリセット
        if st.button("🔄 データリセット"):
            st.session_state.participants = []
            st.session_state.calculation_results = None
            st.success("データをリセットしました")
            st.rerun()
    
    # メインエリア
    tab1, tab2, tab3 = st.tabs(["👥 参加者管理", "🧮 計算実行", "📊 結果分析"])
    
    with tab1:
        st.header("👥 参加者管理")
        
        # 参加者追加
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            new_name = st.text_input("👤 名前", placeholder="例: 田中太郎")
        
        with col2:
            new_role = st.selectbox("💼 役職", 
                                   ['事業部長', '部長', '課長', '主査', '担当'],
                                   index=4)
        
        with col3:
            if st.button("➕ 追加", type="primary"):
                if new_name:
                    participant = {
                        'id': len(st.session_state.participants),
                        '名前': new_name,
                        '役職': new_role,
                        '追加時刻': datetime.now().strftime('%H:%M:%S')
                    }
                    st.session_state.participants.append(participant)
                    st.success(f"✅ {new_name}さんを追加しました！")
                    st.rerun()
                else:
                    st.error("名前を入力してください")
        
        # 現在の参加者一覧
        if st.session_state.participants:
            st.subheader("📋 現在の参加者")
            
            df_participants = pd.DataFrame(st.session_state.participants)
            
            # 参加者カード表示
            for idx, participant in enumerate(st.session_state.participants):
                col_info, col_delete = st.columns([4, 1])
                
                with col_info:
                    st.markdown(f"""
                    <div class="participant-card">
                        <strong>{participant['名前']}</strong> ({participant['役職']})<br>
                        <small>追加時刻: {participant['追加時刻']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_delete:
                    if st.button("🗑️", key=f"delete_{idx}"):
                        st.session_state.participants.pop(idx)
                        st.rerun()
            
            # 役職分布
            st.subheader("📊 役職分布")
            role_counts = df_participants['役職'].value_counts()
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                fig_pie = px.pie(
                    values=role_counts.values,
                    names=role_counts.index,
                    title="役職別人数分布"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_chart2:
                fig_bar = px.bar(
                    x=role_counts.index,
                    y=role_counts.values,
                    title="役職別人数"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        
        else:
            st.info("👆 参加者を追加してください")
    
    with tab2:
        st.header("🧮 AI最適化計算")
        
        if not st.session_state.participants:
            st.warning("⚠️ 参加者を先に追加してください")
            return
        
        df_participants = pd.DataFrame(st.session_state.participants)
        
        # 計算前の確認
        col_preview1, col_preview2 = st.columns(2)
        
        with col_preview1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("💰 合計金額", f"{st.session_state.total_amount:,}円")
            st.metric("👥 参加者数", f"{len(df_participants)}人")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_preview2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            avg_amount = st.session_state.total_amount / len(df_participants)
            st.metric("📊 単純平均", f"{int(avg_amount):,}円")
            st.metric("🔄 丸め単位", f"{marume_unit}円")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 計算実行
        st.subheader("🤖 AI最適化実行")
        
        if st.button("⚡ 計算開始", type="primary", use_container_width=True):
            
            with st.container():
                st.write("🚀 AI遺伝的アルゴリズムによる最適化を開始...")
                
                optimizer = WebWarikanOptimizer()
                
                # 最適化実行
                result = optimizer.optimize_warikan(
                    df_participants, 
                    st.session_state.total_amount, 
                    marume_unit
                )
                
                if result[0] is not None:
                    df_result, sum_warikan, diff, best_params = result
                    
                    # 結果保存
                    st.session_state.calculation_results = {
                        'df_result': df_result,
                        'sum_warikan': sum_warikan,
                        'diff': diff,
                        'best_params': best_params,
                        'timestamp': datetime.now()
                    }
                    
                    # 結果表示
                    st.markdown('<div class="result-highlight">', unsafe_allow_html=True)
                    st.success("🎉 最適化完了！")
                    
                    col_res1, col_res2, col_res3 = st.columns(3)
                    col_res1.metric("目標金額", f"{st.session_state.total_amount:,}円")
                    col_res2.metric("計算後合計", f"{sum_warikan:,}円")
                    col_res3.metric("差額", f"{diff:+,}円")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 個別結果
                    st.subheader("💰 個人別負担額")
                    
                    result_display = df_result[['名前', '役職', '負担額_丸め']].copy()
                    result_display.columns = ['名前', '役職', '負担額（円）']
                    result_display['負担額（円）'] = result_display['負担額（円）'].apply(lambda x: f"{int(x):,}円")
                    
                    st.dataframe(result_display, use_container_width=True)
                    
                    # CSVダウンロード
                    csv = result_display.to_csv(index=False)
                    st.download_button(
                        "📥 結果をCSVダウンロード",
                        csv,
                        "warikan_result.csv",
                        "text/csv"
                    )
                    
                else:
                    st.error("❌ 計算に失敗しました")
    
    with tab3:
        st.header("📊 結果分析")
        
        if st.session_state.calculation_results is None:
            st.info("💡 先に計算を実行してください")
            return
        
        results = st.session_state.calculation_results
        df_result = results['df_result']
        sum_warikan = results['sum_warikan']
        diff = results['diff']
        
        # サマリー表示
        st.subheader("📈 計算サマリー")
        
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        col_sum1.metric("目標金額", f"{st.session_state.total_amount:,}円")
        col_sum2.metric("計算後合計", f"{sum_warikan:,}円")  
        col_sum3.metric("差額", f"{diff:+,}円")
        col_sum4.metric("平均負担額", f"{int(df_result['負担額_丸め'].mean()):,}円")
        
        # グラフ選択
        chart_type = st.radio(
            "📊 表示するグラフを選択",
            ["Plotly インタラクティブ", "matplotlib 日本語版", "両方表示"],
            horizontal=True
        )
        
        chart_generator = WebChartGenerator()
        
        if chart_type in ["Plotly インタラクティブ", "両方表示"]:
            st.subheader("🎮 インタラクティブ ダッシュボード")
            fig_plotly = chart_generator.create_interactive_charts(
                df_result, st.session_state.total_amount, sum_warikan
            )
            st.plotly_chart(fig_plotly, use_container_width=True)
        
        if chart_type in ["matplotlib 日本語版", "両方表示"]:
            st.subheader("🎌 日本語グラフ（matplotlib）")
            fig_matplotlib = chart_generator.create_matplotlib_chart(
                df_result, st.session_state.total_amount, sum_warikan
            )
            st.pyplot(fig_matplotlib)
        
        # 詳細分析
        st.subheader("🔍 詳細分析")
        
        col_detail1, col_detail2 = st.columns(2)
        
        with col_detail1:
            st.write("**役職別統計**")
            role_stats = df_result.groupby('役職')['負担額_丸め'].agg(['mean', 'min', 'max']).round(0)
            role_stats.columns = ['平均', '最小', '最大']
            role_stats = role_stats.astype(int)
            st.dataframe(role_stats)
        
        with col_detail2:
            st.write("**最適化パラメータ**")
            params_df = pd.DataFrame([
                {'役職': k, '比率': f"{v:.3f}"}
                for k, v in results['best_params'].items()
            ])
            st.dataframe(params_df, hide_index=True)

if __name__ == "__main__":
    main()