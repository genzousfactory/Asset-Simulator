"""
複利×副業 資産シミュレーター
streamlit run app.py
pip install streamlit plotly --break-system-packages
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="複利×副業 資産シミュレーター", page_icon="📈", layout="wide")

st.markdown("""
<style>
.main-header{background:linear-gradient(135deg,#0f3460,#185FA5);padding:1.5rem 2rem;border-radius:12px;margin-bottom:1.5rem;color:white}
.metric-card{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:1rem;text-align:center}
.metric-value{font-size:28px;font-weight:700;color:#185FA5}
.metric-label{font-size:12px;color:#888;margin-bottom:4px}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
  <h1>📈 複利×副業 資産シミュレーター</h1>
  <p>複利の力＋副業収入で、あなたの資産形成をシミュレーション</p>
  <strong>✦ API不要 &nbsp;|&nbsp; ✦ 完全無料 &nbsp;|&nbsp; ✦ インストール不要</strong>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ シミュレーション設定")
    init = st.slider("初期投資額", 0, 5_000_000, 500_000, 50_000, format="%d円")
    monthly = st.slider("月次積立額", 0, 200_000, 30_000, 5_000, format="%d円")
    rate = st.slider("年利（想定）", 1.0, 20.0, 5.0, 0.5, format="%.1f%%")
    years = st.slider("運用期間", 1, 40, 20, 1, format="%d年")
    st.divider()
    st.subheader("💼 副業設定")
    side = st.slider("副業月収", 0, 200_000, 50_000, 5_000, format="%d円")
    reinvest = st.slider("副業再投資率", 0, 100, 50, 5, format="%d%%")
    st.divider()
    st.subheader("🔥 FIRE設定")
    expense = st.slider("月の生活費", 100_000, 500_000, 200_000, 10_000, format="%d円")
    withdraw_rate = st.slider("取り崩し率", 2.0, 6.0, 4.0, 0.1, format="%.1f%%")

def calc(init, monthly, rate, years, side_monthly, reinvest_rate):
    val = init
    r = rate / 100 / 12
    rows = []
    principal = init
    side_accum = 0
    for y in range(1, years + 1):
        for m in range(12):
            val = val * (1 + r) + monthly + side_monthly * reinvest_rate / 100
            principal += monthly + side_monthly * reinvest_rate / 100
            side_accum += side_monthly * reinvest_rate / 100
        rows.append({
            "year": y,
            "total": round(val),
            "principal": round(principal),
            "interest": round(val - principal),
            "side": round(side_accum),
        })
    return rows

def fmt(n):
    if n >= 100_000_000: return f"{n/100_000_000:.1f}億円"
    if n >= 10_000: return f"{round(n/10_000)}万円"
    return f"{round(n):,}円"

rows = calc(init, monthly, rate, years, side, reinvest)
last = rows[-1]
principal_only = last["principal"] - last["side"]
fire_target = expense * 12 / (withdraw_rate / 100)

tab1, tab2, tab3, tab4 = st.tabs(["📊 シミュレーター", "🏆 マイルストーン", "⚔️ 戦略比較", "🔥 FIRE計算"])

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="metric-card"><div class="metric-label">最終資産</div><div class="metric-value" style="color:#185FA5">{fmt(last["total"])}</div><div style="font-size:11px;color:#888">元本の{last["total"]/max(1,last["principal"]):.1f}倍</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><div class="metric-label">元本合計</div><div class="metric-value" style="color:#3B6D11">{fmt(last["principal"])}</div><div style="font-size:11px;color:#888">投資した金額</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><div class="metric-label">複利益</div><div class="metric-value" style="color:#BA7517">{fmt(last["interest"])}</div><div style="font-size:11px;color:#888">資産全体の{round(last["interest"]/max(1,last["total"])*100)}%</div></div>', unsafe_allow_html=True)

    st.divider()
    yrs = [r["year"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=yrs, y=[r["principal"]-r["side"] for r in rows], name="元本", marker_color="#185FA5"))
    fig.add_trace(go.Bar(x=yrs, y=[r["interest"] for r in rows], name="複利益", marker_color="#3B6D11"))
    fig.add_trace(go.Bar(x=yrs, y=[r["side"] for r in rows], name="副業投資分", marker_color="#BA7517"))
    fig.update_layout(barmode="stack", title="資産推移グラフ（積み上げ）", xaxis_title="年数", yaxis_title="資産額（円）",
                      height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("年別推移表")
    import pandas as pd
    df = pd.DataFrame([{"年": f"{r['year']}年目", "資産総額": fmt(r["total"]),
                        "元本": fmt(r["principal"]), "複利益": fmt(r["interest"]), "副業分": fmt(r["side"])} for r in rows])
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    targets = [
        (1_000_000, "100万円突破", "🟢"),
        (5_000_000, "500万円突破", "🔵"),
        (10_000_000, "1,000万円突破", "🟡"),
        (30_000_000, "3,000万円突破（老後安心）", "🟠"),
        (50_000_000, "5,000万円突破", "🔴"),
        (100_000_000, "1億円達成 🎉", "💎"),
    ]
    rows60 = calc(init, monthly, rate, 60, side, reinvest)
    for amount, label, icon in targets:
        hit = next((r for r in rows60 if r["total"] >= amount), None)
        if hit:
            st.success(f"{icon} **{label}** — 運用開始から **{hit['year']}年目** に達成（資産: {fmt(hit['total'])}）")
        else:
            st.error(f"❌ **{label}** — 現在の設定では60年以内に達成できません")

with tab3:
    savings = [init + monthly * 12 * y for y in range(1, years + 1)]
    invest_only = [r["total"] for r in calc(init, monthly, rate, years, 0, 0)]
    full = [r["total"] for r in rows]
    yrs = list(range(1, years + 1))
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=yrs, y=savings, name="貯金のみ", line=dict(color="#B4B2A9", dash="dash", width=2)))
    fig2.add_trace(go.Scatter(x=yrs, y=invest_only, name="投資のみ", line=dict(color="#185FA5", width=2), fill="tozeroy", fillcolor="rgba(24,95,165,0.06)"))
    fig2.add_trace(go.Scatter(x=yrs, y=full, name="投資＋副業 ⭐", line=dict(color="#3B6D11", width=3), fill="tozeroy", fillcolor="rgba(59,109,17,0.06)"))
    fig2.update_layout(title="3戦略の資産推移比較", xaxis_title="年数", yaxis_title="資産額（円）",
                       height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h"))
    st.plotly_chart(fig2, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("貯金のみ", fmt(savings[-1]), f"元本比 {savings[-1]/max(1,init+monthly*12*years):.1f}x")
    col2.metric("投資のみ", fmt(invest_only[-1]), f"元本比 {invest_only[-1]/max(1,init+monthly*12*years):.1f}x")
    col3.metric("投資＋副業 ⭐", fmt(full[-1]), f"元本比 {full[-1]/max(1,init+monthly*12*years):.1f}x")

with tab4:
    col1, col2 = st.columns(2)
    col1.metric("FIRE必要資産", fmt(fire_target), f"月{fmt(expense)}×12÷{withdraw_rate}%")
    rows_long = calc(init, monthly, rate, 60, side, reinvest)
    fire_hit = next((r for r in rows_long if r["total"] >= fire_target), None)
    if fire_hit:
        col2.metric("FIRE達成時期", f"{fire_hit['year']}年後", f"資産: {fmt(fire_hit['total'])}")
        st.success(f"🎉 運用開始から **{fire_hit['year']}年目** にFIRE達成！ その後は毎月 **{fmt(fire_target * withdraw_rate / 100 / 12)}** を取り崩せます。")
    else:
        col2.metric("FIRE達成時期", "60年超", "積立額を増やしましょう")
        st.warning("現在の設定では60年以内のFIRE達成は難しいです。月積立額か副業収入を増やしてみましょう。")

st.divider()
st.markdown('<div style="text-align:center;font-size:12px;color:#888">複利×副業 資産シミュレーター | API不要・完全フロントエンド</div>', unsafe_allow_html=True)
