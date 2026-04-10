from __future__ import annotations

import pandas as pd
import streamlit as st

from app.dashboard_data import (
    get_failure_predictions,
    get_overview_summary,
    get_recommendation_snapshot,
    get_recommendations_for_state,
    get_station_daily_metrics,
    get_station_health,
    run_rag_query,
)


st.set_page_config(
    page_title="ChargeFlow Ops Console",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(38, 166, 154, 0.08), transparent 28%),
                    radial-gradient(circle at top right, rgba(255, 167, 38, 0.10), transparent 24%),
                    linear-gradient(180deg, #08111f 0%, #0d1726 100%);
                color: #e6edf7;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0e1a2c 0%, #0a1320 100%);
                border-right: 1px solid rgba(255,255,255,0.06);
            }
            .hero {
                padding: 1.2rem 1.4rem;
                border-radius: 22px;
                background: linear-gradient(135deg, rgba(16, 27, 45, 0.96), rgba(14, 46, 58, 0.92));
                border: 1px solid rgba(255,255,255,0.08);
                box-shadow: 0 18px 50px rgba(0,0,0,0.24);
                margin-bottom: 1rem;
            }
            .hero h1 {
                margin: 0 0 0.4rem 0;
                font-size: 2.3rem;
                color: #f7fbff;
            }
            .hero p {
                margin: 0;
                color: #a8b7cc;
                line-height: 1.55;
            }
            .section-card {
                background: rgba(10, 20, 35, 0.82);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 18px;
                padding: 1rem 1.05rem;
                margin-bottom: 1rem;
                box-shadow: 0 14px 35px rgba(0,0,0,0.20);
            }
            .section-title {
                font-size: 1.05rem;
                font-weight: 700;
                color: #f8fbff;
                margin-bottom: 0.35rem;
            }
            .section-copy {
                color: #9fb0c6;
                font-size: 0.92rem;
                line-height: 1.5;
                margin-bottom: 0.8rem;
            }
            .rec-card {
                padding: 0.95rem 1rem;
                border-radius: 16px;
                background: linear-gradient(180deg, rgba(18, 31, 50, 0.94), rgba(12, 24, 40, 0.95));
                border: 1px solid rgba(255,255,255,0.08);
                margin-bottom: 0.8rem;
            }
            .rec-card h4 {
                margin: 0 0 0.2rem 0;
                color: #f8fbff;
                font-size: 1rem;
            }
            .rec-meta {
                color: #88d3c7;
                font-size: 0.84rem;
                margin-bottom: 0.35rem;
            }
            .rec-body {
                color: #adbbcf;
                font-size: 0.9rem;
                line-height: 1.5;
            }
            .evidence {
                padding: 0.8rem 0.95rem;
                border-radius: 14px;
                background: rgba(8, 17, 30, 0.86);
                border: 1px solid rgba(255,255,255,0.07);
                margin-bottom: 0.65rem;
            }
            .small-label {
                color: #7aa2ff;
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }
            div[data-testid="stMetric"] {
                background: rgba(11, 22, 37, 0.80);
                border: 1px solid rgba(255,255,255,0.08);
                padding: 0.8rem 0.9rem;
                border-radius: 16px;
            }
            div[data-testid="stMetricLabel"] {
                color: #8ea1ba;
            }
            div[data-testid="stMetricValue"] {
                color: #f7fbff;
            }
            .stDataFrame, .stTable {
                border-radius: 16px;
                overflow: hidden;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    overview = get_overview_summary()
    station_health = get_station_health()
    station_daily = get_station_daily_metrics()
    failure_predictions = get_failure_predictions()
    recommendation_snapshot = get_recommendation_snapshot()

    recommendation_snapshot["recommendation_score"] = recommendation_snapshot["recommendation_score"].astype(float)
    recommendation_snapshot["predicted_failure_probability"] = recommendation_snapshot["predicted_failure_probability"].astype(float)
    station_health["failure_rate_per_100_sessions"] = pd.to_numeric(
        station_health["failure_rate_per_100_sessions"], errors="coerce"
    ).fillna(0.0)
    station_health["avg_queue_minutes"] = pd.to_numeric(station_health["avg_queue_minutes"], errors="coerce").fillna(0.0)
    station_daily["metric_date"] = pd.to_datetime(station_daily["metric_date"])
    failure_predictions["metric_date"] = pd.to_datetime(failure_predictions["metric_date"])
    failure_predictions["predicted_failure_probability"] = pd.to_numeric(
        failure_predictions["predicted_failure_probability"], errors="coerce"
    ).fillna(0.0)

    available_states = sorted(recommendation_snapshot["state"].dropna().unique().tolist())

    with st.sidebar:
        st.markdown("## ChargeFlow")
        st.caption("Local operations dashboard")
        state_filter = st.selectbox("Focus State", available_states, index=0)
        top_k = st.slider("Top Recommendation Count", min_value=3, max_value=8, value=5)
        st.markdown("---")
        st.markdown("### What This Dashboard Shows")
        st.markdown(
            """
            - Current portfolio-scale demand footprint
            - Station reliability and queue pressure
            - Highest-confidence station recommendations
            - Highest predicted station-day risk
            - Grounded maintenance and SOP retrieval
            """
        )

    row_counts = overview["summary"]["row_counts"]
    failure_summary = overview["summary"]["failure_summary"]
    demand_summary = overview["summary"]["demand_summary"]

    st.markdown(
        """
        <div class="hero">
            <h1>ChargeFlow Operations Console</h1>
            <p>
                A local companion dashboard for EV charging operations. This view combines warehouse marts,
                baseline ML outputs, recommendation scoring, and retrieval over maintenance knowledge into one
                operator-style console.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Tracked States", row_counts["states"], help="Number of states represented in the demand mart.")
    metric_cols[1].metric("Stations in Scope", row_counts["stations"], help="Total stations available across the modeled network.")
    metric_cols[2].metric(
        "Avg Daily Sessions",
        demand_summary["avg_daily_sessions"],
        help="Average daily charging sessions across the demand forecast dataset.",
    )
    metric_cols[3].metric(
        "Observed Failure Days",
        failure_summary["positive_failure_days"],
        help="Count of station-day records with at least one failure event in the ML dataset.",
    )

    st.markdown("")
    col_left, col_right = st.columns([1.35, 0.95], gap="large")

    with col_left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">State Demand and Incident Trend</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">Shows how session volume and failure events move over time for the selected state. '
            'This helps an operator see whether reliability issues are rising with demand pressure.</div>',
            unsafe_allow_html=True,
        )
        filtered_daily = station_daily[station_daily["state"] == state_filter].copy()
        daily_state = (
            filtered_daily.groupby("metric_date", as_index=False)[["session_count", "failure_event_count", "total_energy_kwh"]]
            .sum()
            .sort_values("metric_date")
        )
        st.line_chart(daily_state.set_index("metric_date")[["session_count", "failure_event_count"]], height=320)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Most Fragile Stations in View</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">Ranks stations in the selected state by historical failure rate and queue pressure. '
            'This is the table an operations lead would use to spot where to intervene first.</div>',
            unsafe_allow_html=True,
        )
        fragile = (
            station_health[station_health["state"] == state_filter]
            .sort_values(["failure_rate_per_100_sessions", "avg_queue_minutes"], ascending=[False, False])
            .head(12)
            .rename(
                columns={
                    "station_id": "Station",
                    "total_sessions": "Sessions",
                    "total_failures": "Failures",
                    "total_downtime_minutes": "Downtime Min",
                    "avg_queue_minutes": "Avg Queue Min",
                    "failure_rate_per_100_sessions": "Failure Rate / 100 Sessions",
                }
            )
        )
        st.dataframe(fragile, use_container_width=True, hide_index=True, height=330)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top Recommended Stations</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">This panel surfaces the best station choices in the selected state. '
            'The score blends predicted failure risk, historical reliability, queue pressure, and recent throughput.</div>',
            unsafe_allow_html=True,
        )
        recommendations = get_recommendations_for_state(state_filter, top_k=top_k)
        for item in recommendations:
            st.markdown(
                f"""
                <div class="rec-card">
                    <h4>{item['station_name']}</h4>
                    <div class="rec-meta">{item['city']}, {item['state']} · score {item['recommendation_score']}</div>
                    <div class="rec-body">
                        Predicted failure probability: {item['predicted_failure_probability']}<br/>
                        {item['explanation']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Latest High-Risk Station-Days</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">These are the most elevated model-scored station-days from the latest prediction window. '
            'Use this to prioritize inspections or preventive outreach.</div>',
            unsafe_allow_html=True,
        )
        risk_snapshot = failure_predictions.sort_values(
            ["metric_date", "predicted_failure_probability"], ascending=[False, False]
        ).head(12)
        st.dataframe(
            risk_snapshot.rename(
                columns={
                    "station_id": "Station",
                    "metric_date": "Date",
                    "failure_target": "Observed Failure",
                    "predicted_failure_probability": "Predicted Failure Probability",
                }
            ),
            use_container_width=True,
            hide_index=True,
            height=330,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Grounded Ops Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Ask a maintenance or SOP question. The assistant retrieves evidence from synthetic maintenance notes, '
        'tickets, and SOP documents, then returns a grounded response rather than an unstructured chatbot answer.</div>',
        unsafe_allow_html=True,
    )
    default_query = "How should I respond to a cooling alarm?"
    query = st.text_area("Operator Question", value=default_query, height=120)
    if st.button("Run Retrieval", use_container_width=False):
        response = run_rag_query(query, top_k=3)
        st.success(response["answer"])
        st.markdown('<div class="small-label">Retrieved Evidence</div>', unsafe_allow_html=True)
        for source in response["sources"]:
            st.markdown(
                f"""
                <div class="evidence">
                    <strong>{source['title']}</strong><br/>
                    <span style="color:#84a2c6;">{source['source_type']} · score {source['score']}</span>
                    <p style="margin:8px 0 0 0;color:#b6c4d8;">{source['content'][:240]}...</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("What each dashboard section means"):
        st.markdown(
            """
            **Tracked States / Stations / Avg Daily Sessions / Observed Failure Days**
            These top KPIs summarize the current scope of the modeled network and the size of the analytical dataset.

            **State Demand and Incident Trend**
            This compares session volume against failure-event counts over time for the selected state. It helps answer:
            “Are reliability issues increasing when demand rises?”

            **Most Fragile Stations in View**
            This is a station-health triage table. It highlights where operators may need maintenance focus based on failure rate,
            downtime, and queue pressure.

            **Top Recommended Stations**
            This is the decision-support panel. It surfaces the best stations to route users toward by combining:
            lower predicted failure risk, better historical reliability, lower queue pressure, and stronger recent throughput.

            **Latest High-Risk Station-Days**
            This is the ML monitoring panel. It shows the most concerning recent station-day predictions so operators can intervene early.

            **Grounded Ops Assistant**
            This is the retrieval layer. It answers maintenance questions using stored notes, tickets, and SOPs so the response is grounded in evidence.
            """
        )


if __name__ == "__main__":
    main()
