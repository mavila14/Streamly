import streamlit as st
import re
import json
import google.generativeai as genai
import plotly.graph_objects as go
import os

# ------------------------------------------------------------
# Configure your Google Generative AI API key
# ------------------------------------------------------------
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
genai.configure(api_key=GOOGLE_API_KEY)

GEMINI_MODEL = "gemini-2.0-flash"

# ------------------------------------------------------------
# Custom CSS for a Streamly-like style
# ------------------------------------------------------------
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
    background: #1e1e1e; /* Overall dark background */
    color: #ffffff;
}

/* Headings */
h1, h2, h3 {
    margin: 0 0 1rem 0;
    font-weight: 800;
}
h1 {
    font-size: 2.5rem;
    color: #ff0080; /* Pink highlight */
}
h2 {
    font-size: 1.8rem;
    color: #ff0080;
}
h3 {
    font-size: 1.4rem;
}

/* Paragraphs */
p {
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #1e1e1e;
    border-right: 1px solid #444;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding: 2rem 1rem;
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] {
    border-radius: 6px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    background-color: rgba(255, 255, 255, 0.05) !important;
    color: #fff !important;
    padding: 0.75rem !important;
}

/* Buttons */
.stButton button {
    background: linear-gradient(135deg, #7928CA 0%, #FF0080 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.5rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}
.stButton button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}
.stButton button:active {
    transform: translateY(0) !important;
}

/* Cards */
.card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.1);
}

/* Decision box styling */
.decision-box {
    background: rgba(255, 0, 128, 0.08);
    border-radius: 12px;
    padding: 2rem 1.5rem;
    margin-top: 2rem;
    border: 1px solid rgba(255, 0, 128, 0.2);
    text-align: center;
    animation: fadeInUp 0.5s ease-out forwards;
    transform: translateY(20px);
    opacity: 0;
}
.decision-box h2 {
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: #ff0080;
}
.decision-box .score {
    font-size: 3rem;
    font-weight: 800;
    color: #ff0080;
    margin: 1rem 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Radar chart background fix */
.js-plotly-plot .plotly .modebar {
    background: rgba(0, 0, 0, 0.4);
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ------------------------------------------------------------
# Plotly Charts
# ------------------------------------------------------------
def create_radar_chart(factors):
    categories = ["Discretionary Income","Opportunity Cost","Goal Alignment","Long-Term Impact","Behavioral"]
    vals = [factors["D"], factors["O"], factors["G"], factors["L"], factors["B"]]
    vals.append(vals[0])  # close shape
    categories.append(categories[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals,
        theta=categories,
        fill='toself',
        fillcolor='rgba(255, 0, 128, 0.2)',
        line=dict(color='#ff0080', width=2),
        name='Factors'
    ))
    # Reference lines
    for i in [-2, -1, 0, 1, 2]:
        fig.add_trace(go.Scatterpolar(
            r=[i]*len(categories),
            theta=categories,
            line=dict(color='rgba(255,255,255,0.1)', width=1, dash='dash'),
            showlegend=False
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[-3,3],
                tickvals=[-2,-1,0,1,2],
                gridcolor='rgba(255,255,255,0.1)'
            ),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=20, b=20),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_pds_gauge(pds):
    # Color depends on PDS range
    if pds >= 5:
        color = "#68d391"  # green
    elif pds < 0:
        color = "#fc8181"  # red
    else:
        color = "#ed8936"  # orange

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pds,
        domain={'x': [0,1], 'y': [0,1]},
        gauge={
            'axis': {'range': [-10, 10]},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [-10, 0], 'color': '#fed7d7'},
                {'range': [0, 5], 'color': '#feebc8'},
                {'range': [5, 10], 'color': '#c6f6d5'}
            ],
        }
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#ffffff", 'family': "Inter, sans-serif"}
    )
    return fig

# ------------------------------------------------------------
# AI Logic
# ------------------------------------------------------------
def get_factors_from_gemini(leftover_income, has_high_interest_debt,
                            main_financial_goal, purchase_urgency,
                            item_name, item_cost, extra_context=None):
    """
    Returns factor assignments (D,O,G,L,B) from -2..+2 plus brief explanations
    using Google Generative AI (Gemini).
    """
    extra_text = f"\nAdditional user context: {extra_context}" if extra_context else ""
    
    prompt = f"""
We have a Purchase Decision Score (PDS) formula:
PDS = D + O + G + L + B, each factor is -2 to 2.

Guidelines:
1. D: Higher if leftover_income >> item_cost
2. O: Positive if no high-interest debt, negative if debt
3. G: Positive if aligns with main_financial_goal, negative if conflicts
4. L: Positive if long-term benefit, negative if ongoing cost
5. B: Positive if urgent need, negative if impulsive want

Evaluate:
- Item: {item_name}
- Cost: {item_cost}
- leftover_income: {leftover_income}
- high_interest_debt: {has_high_interest_debt}
- main_financial_goal: {main_financial_goal}
- purchase_urgency: {purchase_urgency}
{extra_text}

Return valid JSON exactly in the format:
{{
  "D": 2,
  "O": 1,
  "G": 0,
  "L": -1,
  "B": 2,
  "D_explanation": "...",
  "O_explanation": "...",
  "G_explanation": "...",
  "L_explanation": "...",
  "B_explanation": "..."
}}
    """.strip()
    
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=512
            )
        )
        if not resp:
            st.error("No response from Gemini.")
            return {"D":0,"O":0,"G":0,"L":0,"B":0}
        text = resp.text
        # Attempt to find JSON in the response
        candidates = re.findall(r"(\{[\s\S]*?\})", text)
        for c in candidates:
            try:
                data = json.loads(c)
                if all(k in data for k in ["D","O","G","L","B"]):
                    return data
            except json.JSONDecodeError:
                pass
        st.error("Unable to parse valid JSON from AI output.")
        return {"D":0,"O":0,"G":0,"L":0,"B":0}
    except Exception as e:
        st.error(f"Error calling Gemini: {e}")
        return {"D":0,"O":0,"G":0,"L":0,"B":0}

def compute_pds(factors):
    return sum(factors.get(k,0) for k in ["D","O","G","L","B"])

def get_recommendation(pds):
    if pds >= 5:
        return "Buy it.", "positive"
    elif pds < 0:
        return "Don't buy it.", "negative"
    else:
        return "Consider carefully.", "neutral"

# ------------------------------------------------------------
# Set up theme config (if needed)
# ------------------------------------------------------------
def setup_dark_theme():
    """Write a Streamlit config.toml to enforce dark theme."""
    if not os.path.exists(".streamlit"):
        os.makedirs(".streamlit")
    with open(".streamlit/config.toml", "w") as f:
        f.write("[theme]\nbase = \"dark\"\n")

# ------------------------------------------------------------
# Main App
# ------------------------------------------------------------
def main():
    # Sidebar
    with st.sidebar:
        # Streamly avatar
        st.image("avatar_streamly.png", width=100)
        st.markdown("<h2 style='color:#ff0080;'>Streamly</h2>", unsafe_allow_html=True)
        
        pages = ["Decision Tool", "Advanced Tool"]
        selection = st.radio("", pages, label_visibility="collapsed")
        
        st.markdown("<hr style='margin: 1rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
        st.markdown("**Quick Tips**")
        st.markdown("- Enter item & cost\n- Score ≥ 5 → likely buy\n- Score < 0 → likely skip")
        st.markdown("<hr style='margin: 1rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
        
        # Footer note
        st.markdown(
            "<div style='font-size:0.8rem; opacity:0.6;'>© 2025 Streamly</div>",
            unsafe_allow_html=True
        )

    # Main header area
    st.markdown("""
    <div style="text-align:center; margin: 2rem 0;">
        <img src="streamlit128.png" width="120" style="margin-bottom:1rem;" />
        <h1 style="font-size:3rem;">Streamly Purchase Assistant</h1>
        <p style="font-size:1.2rem; opacity:0.8;">
          "Should you buy it? Let our AI help you decide."
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------
    # 1. Decision Tool (Basic)
    # ------------------------------------------------
    if selection == "Decision Tool":
        st.markdown("""
        <h2>Quick Decision Tool</h2>
        <p style="opacity:0.8;">
          Enter a single item and cost to get a fast recommendation.
        </p>
        """, unsafe_allow_html=True)

        with st.form("basic_form"):
            item_name = st.text_input("What are you buying?", "Wireless Headphones")
            cost = st.number_input("Cost ($)", min_value=1.0, value=200.0, step=10.0)
            submit_btn = st.form_submit_button("Should I Buy It?")

        if submit_btn:
            with st.spinner("Analyzing..."):
                # Minimal placeholders
                leftover_income = max(1000, cost * 2)
                has_high_interest_debt = "No"
                main_financial_goal = "Save for emergencies"
                purchase_urgency = "Mixed"
                
                factors = get_factors_from_gemini(
                    leftover_income,
                    has_high_interest_debt,
                    main_financial_goal,
                    purchase_urgency,
                    item_name,
                    cost
                )
                pds = compute_pds(factors)
                rec_text, rec_class = get_recommendation(pds)

                # Display item card
                st.markdown(f"""
                <div class="card" style="display:flex;align-items:center;">
                    <div style="margin-right:1rem;font-size:2rem;">
                        {"💼" if cost >= 500 else "🛍️"}
                    </div>
                    <div style="flex:1;">
                        <h3 style="margin-bottom:0.25rem;">{item_name}</h3>
                        <small style="opacity:0.7;">Cost: ${cost:,.2f}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Decision box
                st.markdown(f"""
                <div class="decision-box">
                    <h2>Purchase Decision Score</h2>
                    <div class="score">{pds}</div>
                    <div style="margin-top:1rem; font-size:1.25rem; font-weight:600;
                                color:{'#68d391' if rec_class=='positive' else '#fc8181' if rec_class=='negative' else '#ed8936'};">
                        {rec_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Factor details
                factor_labels = {
                    "D": "Discretionary Income",
                    "O": "Opportunity Cost",
                    "G": "Goal Alignment",
                    "L": "Long-Term Impact",
                    "B": "Behavioral"
                }
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Decision Factors")
                    for f in ["D","O","G","L","B"]:
                        val = factors[f]
                        color = "#68d391" if val>0 else "#fc8181" if val<0 else "#cbd5e0"
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;
                                    background-color:rgba(255,255,255,0.05);
                                    border-left:4px solid #ff0080;
                                    padding:0.75rem;margin-bottom:0.5rem;border-radius:6px;">
                            <strong style="margin-right:0.75rem;">{f}</strong>
                            <span style="flex:1;">{factor_labels[f]}</span>
                            <span style="color:{color};font-weight:700;">{val:+d}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        if f"{f}_explanation" in factors:
                            st.caption(factors[f"{f}_explanation"])

                with col2:
                    st.markdown("### Visual Analysis")
                    radar_fig = create_radar_chart(factors)
                    st.plotly_chart(radar_fig, use_container_width=True)
                    
                    gauge_fig = create_pds_gauge(pds)
                    st.plotly_chart(gauge_fig, use_container_width=True)

    # ------------------------------------------------
    # 2. Advanced Tool
    # ------------------------------------------------
    else:
        st.markdown("""
        <h2>Advanced Purchase Query</h2>
        <p style="opacity:0.8;">Control all parameters for a more in-depth analysis.</p>
        """, unsafe_allow_html=True)

        with st.form("advanced_form"):
            st.subheader("Purchase Details")
            item_name = st.text_input("Item Name", "High-End Laptop")
            item_cost = st.number_input("Item Cost ($)", min_value=1.0, value=1200.0, step=50.0)

            st.subheader("User-Financial Data")
            leftover_income = st.number_input("Monthly Leftover Income ($)", min_value=0.0, value=1500.0, step=50.0)
            has_debt = st.selectbox("Do you have high-interest debt?", ["No", "Yes"])
            main_goal = st.text_input("Your Main Financial Goal", "Build an emergency fund")
            urgency = st.selectbox("How urgent is this purchase?", ["Urgent Needs","Mixed","Mostly Wants"])

            st.subheader("Extra Context (Optional)")
            extra_notes = st.text_area("Provide any additional context here...")

            adv_submit = st.form_submit_button("Analyze My Purchase")

        if adv_submit:
            with st.spinner("Contacting AI..."):
                factors = get_factors_from_gemini(
                    leftover_income,
                    has_debt,
                    main_goal,
                    urgency,
                    item_name,
                    item_cost,
                    extra_context=extra_notes
                )
                pds = compute_pds(factors)
                rec_text, rec_class = get_recommendation(pds)

                # Display item card
                st.markdown(f"""
                <div class="card" style="display:flex;align-items:center;">
                    <div style="margin-right:1rem;font-size:2rem;">
                        {"💼" if item_cost >= 500 else "🛍️"}
                    </div>
                    <div style="flex:1;">
                        <h3 style="margin-bottom:0.25rem;">{item_name}</h3>
                        <small style="opacity:0.7;">Cost: ${item_cost:,.2f}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Decision box
                st.markdown(f"""
                <div class="decision-box">
                    <h2>Purchase Decision Score</h2>
                    <div class="score">{pds}</div>
                    <div style="margin-top:1rem; font-size:1.25rem; font-weight:600;
                                color:{'#68d391' if rec_class=='positive' else '#fc8181' if rec_class=='negative' else '#ed8936'};">
                        {rec_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Factor details
                factor_labels = {
                    "D": "Discretionary Income",
                    "O": "Opportunity Cost",
                    "G": "Goal Alignment",
                    "L": "Long-Term Impact",
                    "B": "Behavioral"
                }
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Decision Factors")
                    for f in ["D","O","G","L","B"]:
                        val = factors[f]
                        color = "#68d391" if val>0 else "#fc8181" if val<0 else "#cbd5e0"
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;
                                    background-color:rgba(255,255,255,0.05);
                                    border-left:4px solid #ff0080;
                                    padding:0.75rem;margin-bottom:0.5rem;border-radius:6px;">
                            <strong style="margin-right:0.75rem;">{f}</strong>
                            <span style="flex:1;">{factor_labels[f]}</span>
                            <span style="color:{color};font-weight:700;">{val:+d}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        if f"{f}_explanation" in factors:
                            st.caption(factors[f"{f}_explanation"])

                with col2:
                    st.markdown("### Visual Analysis")
                    radar_fig = create_radar_chart(factors)
                    st.plotly_chart(radar_fig, use_container_width=True)

                    gauge_fig = create_pds_gauge(pds)
                    st.plotly_chart(gauge_fig, use_container_width=True)


# ------------------------------------------------------------
# Run the App
# ------------------------------------------------------------
if __name__ == "__main__":
    setup_dark_theme()
    main()
