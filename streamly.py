import streamlit as st
import re
import json
import google.generativeai as genai
import plotly.graph_objects as go

# ------------------------------------------------------------
# Configure your Google Generative AI API key
# ------------------------------------------------------------
GOOGLE_API_KEY = st.secrets["google"]["api_key"]
genai.configure(api_key=GOOGLE_API_KEY)

GEMINI_MODEL = "gemini-2.0-flash"

# ------------------------------------------------------------
# Custom CSS for Dark Theme
# ------------------------------------------------------------
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Headings */
h1 {
    font-weight: 800;
    font-size: 2.5rem;
    letter-spacing: -0.025em;
    line-height: 1.2;
    margin-bottom: 1rem;
    color: #6c7ed6;
}
h2 {
    font-weight: 700;
    font-size: 1.8rem;
    letter-spacing: -0.025em;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}
h3 {
    font-weight: 600;
    font-size: 1.3rem;
    margin-top: 1.25rem;
    margin-bottom: 0.5rem;
}
p {
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* Sidebar styling - dark theme */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding-top: 2rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}
[data-testid="stSidebar"] h1 {
    font-size: 1.5rem;
    color: #6c7ed6;
    margin-bottom: 2rem;
}

/* Custom form inputs for dark theme */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] {
    border-radius: 6px;
    padding: 12px;
    width: 100%;
    margin-bottom: 1rem;
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: white;
    font-size: 16px;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #6c7ed6;
    box-shadow: 0 0 0 2px rgba(108, 126, 214, 0.3);
}

/* Style number input */
[data-testid="stNumberInput"] div[data-baseweb="input"] {
    background-color: transparent !important;
}

/* Hide standard number input controls */
[data-testid="stNumberInput"] div[data-baseweb="input-container"] div[role="button"] {
    display: none !important;
}

/* Button styling for dark theme */
[data-testid="baseButton-secondary"], 
.stButton button {
    background: rgba(108, 126, 214, 0.8) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.5rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.025em !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    width: 100% !important;
}
[data-testid="baseButton-secondary"]:hover, 
.stButton button:hover {
    background: rgba(138, 148, 227, 0.9) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4) !important;
}
[data-testid="baseButton-secondary"]:active, 
.stButton button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
}

/* Plus/minus buttons */
.stButton button[kind="secondary"] {
    background: rgba(70, 70, 70, 0.3) !important;
    border-radius: 50% !important;
    width: 30px !important;
    height: 30px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Card styling for dark theme */
.card {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2), 0 10px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.3), 0 20px 30px rgba(0, 0, 0, 0.2);
}

/* Landing page title styling for dark theme */
.landing-title {
    font-size: 3.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6c7ed6 0%, #8a94e3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    letter-spacing: -0.05em;
    line-height: 1;
    text-align: center;
}
.landing-subtitle {
    font-size: 1.25rem;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 2rem;
    text-align: center;
}

/* Logo styling */
.logo {
    display: flex;
    align-items: center;
    margin-bottom: 2rem;
}
.logo-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #5a67d8 0%, #4c51bf 100%);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    color: white;
    font-weight: 700;
    font-size: 1.25rem;
}
.logo-text {
    font-size: 1.5rem;
    font-weight: 800;
    color: #5a67d8;
}

/* Section header */
.section-header {
    display: flex;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e2e8f0;
}
.section-icon {
    width: 32px;
    height: 32px;
    background: #ebf4ff;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    color: #5a67d8;
    font-weight: 700;
    font-size: 1rem;
}

/* Decision box for dark theme */
.decision-box {
    background: rgba(108, 126, 214, 0.1);
    border-radius: 12px;
    padding: 2rem 1.5rem;
    margin-top: 2rem;
    border: 1px solid rgba(108, 126, 214, 0.3);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25), 0 4px 10px rgba(0, 0, 0, 0.15);
    text-align: center;
    animation: fadeInUp 0.5s ease-out forwards;
    transform: translateY(20px);
    opacity: 0;
}
.decision-box h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #8a94e3;
    margin-bottom: 1.5rem;
}
.decision-box .score {
    font-size: 3rem;
    font-weight: 800;
    color: #8a94e3;
    margin: 1rem 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
}
.recommendation {
    margin-top: 1rem;
    font-size: 1.25rem;
    font-weight: 600;
}
.recommendation.positive {
    color: #48bb78;
}
.recommendation.negative {
    color: #f56565;
}
.recommendation.neutral {
    color: #ed8936;
}

/* Factor cards for dark theme */
.factor-card {
    display: flex;
    align-items: center;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transition: all 0.2s ease;
    border-left: 4px solid #6c7ed6;
}
.factor-card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
    transform: translateX(3px);
}
.factor-card .factor-letter {
    font-size: 1.25rem;
    font-weight: 700;
    color: #8a94e3;
    margin-right: 1rem;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(108, 126, 214, 0.2);
    border-radius: 50%;
}
.factor-card .factor-description {
    flex: 1;
}
.factor-card .factor-value {
    font-size: 1.25rem;
    font-weight: 700;
    margin-left: auto;
}
.factor-card .factor-value.positive {
    color: #68d391;
}
.factor-card .factor-value.negative {
    color: #fc8181;
}
.factor-card .factor-value.neutral {
    color: #cbd5e0;
}

/* Item card styles for dark theme */
.item-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
}
.item-icon {
    width: 40px;
    height: 40px;
    background: rgba(108, 126, 214, 0.3);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 1rem;
    color: #8a94e3;
    font-weight: 700;
    font-size: 1.25rem;
}
.item-details {
    flex: 1;
}
.item-name {
    font-weight: 600;
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.9);
}
.item-cost {
    font-weight: 700;
    font-size: 1.2rem;
    color: #8a94e3;
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
# Function removed as we're using inline styling instead

# Function removed as we're using inline styling directly in the main flow

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
        fillcolor='rgba(90, 103, 216, 0.2)',
        line=dict(color='#5a67d8', width=2),
        name='Factors'
    ))
    # Reference lines
    for i in [-2, -1, 0, 1, 2]:
        fig.add_trace(go.Scatterpolar(
            r=[i]*len(categories),
            theta=categories,
            line=dict(color='rgba(200,200,200,0.5)', width=1, dash='dash'),
            showlegend=False
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[-3,3],
                tickvals=[-2,-1,0,1,2],
                gridcolor='rgba(200,200,200,0.3)'
            ),
            angularaxis=dict(gridcolor='rgba(200,200,200,0.3)'),
            bgcolor='rgba(255,255,255,0.9)'
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=20, b=20),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_pds_gauge(pds):
    if pds >= 5:
        color = "#48bb78"
    elif pds < 0:
        color = "#f56565"
    else:
        color = "#ed8936"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pds,
        domain={'x':[0,1],'y':[0,1]},
        gauge={
            'axis': {'range':[-10,10]},
            'bar': {'color':color},
            'bgcolor':"white",
            'borderwidth':2,
            'bordercolor':"#e2e8f0",
            'steps': [
                {'range':[-10,0], 'color':'#fed7d7'},
                {'range':[0,5], 'color':'#feebc8'},
                {'range':[5,10], 'color':'#c6f6d5'}
            ],
        }
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color':"#2d3748", 'family':"Inter, sans-serif"}
    )
    return fig

# ------------------------------------------------------------
# AI Logic
# ------------------------------------------------------------
def get_factors_from_gemini(leftover_income, has_high_interest_debt,
                            main_financial_goal, purchase_urgency,
                            item_name, item_cost, extra_context=None):
    """
    Returns factor assignments (D,O,G,L,B) from -2..+2 plus brief explanations.
    """
    extra_text = f"\nAdditional user context: {extra_context}" if extra_context else ""
    
    prompt = f"""
We have a Purchase Decision Score (PDS) formula:
PDS = D + O + G + L + B, each factor is -2 to 2.

Guidelines:
1. D: Higher if leftover_income >> item_cost
2. O: Positive if no high-interest debt, negative if debt
3. G: Positive if aligns with main_financial_goal, negative if conflicts
4. L: Positive if long-term benefit, negative if extra cost
5. B: Positive if urgent need, negative if impulsive want

Evaluate:
- Item: {item_name}
- Cost: {item_cost}
- leftover_income: {leftover_income}
- high_interest_debt: {has_high_interest_debt}
- main_financial_goal: {main_financial_goal}
- purchase_urgency: {purchase_urgency}
{extra_text}

Return valid JSON:
{{
  "D": 2,
  "O": 1,
  "G": 0,
  "L": -1,
  "B": 2,
  "D_explanation": "...",
  ...
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
    return sum(factors.get(f,0) for f in ["D","O","G","L","B"])

def get_recommendation(pds):
    if pds >= 5:
        return "Buy it.", "positive"
    elif pds < 0:
        return "Don't buy it.", "negative"
    else:
        return "Consider carefully.", "neutral"

# ------------------------------------------------------------
# Additional UI Helpers
# ------------------------------------------------------------
# Functions removed as we're using inline styling directly in the main flow

# ------------------------------------------------------------
# Main App
# ------------------------------------------------------------
def main():
    with st.sidebar:
        # Simple logo with just text
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="color: #6c7ed6; font-size: 1.5rem; font-weight: 700;">Decision Assistant</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Radio selection for tools
        pages = ["Decision Tool", "Advanced Tool"]
        selection = st.radio("", pages, label_visibility="collapsed")
        
        st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
        st.markdown("### Quick Tips")
        st.markdown("""
        - Just enter the item and cost
        - Or use Advanced Tool for more control
        - Score above 5 = buy
        """)
        
        st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
        st.markdown("<div style='opacity: 0.7; font-size: 0.8rem;'>© 2025 Munger AI</div>", unsafe_allow_html=True)
    
    # Main heading (always shown)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 3rem; font-weight: 800; color: #6c7ed6; margin-bottom: 0.5rem;">Munger AI</h1>
        <p style="font-size: 1.1rem; opacity: 0.7; margin-bottom: 2rem;">Should you buy it? Our AI decides in seconds.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # -----------------------------------
    # 1. Basic Decision Tool
    # -----------------------------------
    if selection == "Decision Tool":
        # Icon and heading
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <div style="background-color: #fff; border-radius: 10px; padding: 10px; margin-right: 15px;">
                <span style="font-size: 24px;">🛍️</span>
            </div>
            <h1 style="font-size: 36px; color: #6c7ed6; margin: 0;">What are you buying?</h1>
        </div>
        <hr style="margin-bottom: 30px; border-color: rgba(255,255,255,0.1);">
        """, unsafe_allow_html=True)
        
        # Basic form with larger input fields
        with st.form("basic_form"):
            st.markdown('<p style="font-size: 18px; margin-bottom: 5px;">What are you buying?</p>', unsafe_allow_html=True)
            item_name = st.text_input("", value="New Laptop", label_visibility="collapsed")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown('<p style="font-size: 18px; margin-bottom: 5px;">Cost ($)</p>', unsafe_allow_html=True)
            with col2:
                cost = st.number_input("", min_value=1.0, value=500.0, step=50.0, label_visibility="collapsed")
            with col3:
                st.write("")
                st.write("")
                minus, plus = st.columns(2)
                with minus:
                    st.button("-", key="minus")
                with plus:
                    st.button("+", key="plus")
            
            # Centered button with custom styling
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_btn = st.form_submit_button("Should I Buy It?")
        
        if submit_btn:
            with st.spinner("Analyzing with AI..."):
                # Minimal logic for leftover etc. (could be expanded)
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
                
                # Item card
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1rem; 
                            margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                            border: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center;">
                    <div style="width: 40px; height: 40px; background: rgba(108, 126, 214, 0.3); 
                                border-radius: 8px; display: flex; align-items: center; justify-content: center;
                                margin-right: 1rem; color: #8a94e3; font-weight: 700; font-size: 1.25rem;">
                        {"💼" if cost >= 1000 else "🛍️"}
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 1.1rem; color: rgba(255, 255, 255, 0.9);">
                            {item_name}
                        </div>
                    </div>
                    <div style="font-weight: 700; font-size: 1.2rem; color: #8a94e3;">
                        ${cost:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Decision box with PDS score
                st.markdown(f"""
                <div style="background: rgba(108, 126, 214, 0.1); border-radius: 12px; padding: 2rem 1.5rem;
                            margin-top: 2rem; border: 1px solid rgba(108, 126, 214, 0.3);
                            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25), 0 4px 10px rgba(0, 0, 0, 0.15);
                            text-align: center; animation: fadeInUp 0.5s ease-out forwards;">
                    <h2 style="font-size: 1.75rem; font-weight: 700; color: #8a94e3; margin-bottom: 1.5rem;">
                        Purchase Decision Score
                    </h2>
                    <div style="font-size: 3rem; font-weight: 800; color: #8a94e3; margin: 1rem 0;
                                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);">
                        {pds}
                    </div>
                    <div style="margin-top: 1rem; font-size: 1.25rem; font-weight: 600; 
                                color: {'#68d391' if rec_class == 'positive' else '#fc8181' if rec_class == 'negative' else '#ed8936'};">
                        {rec_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Decision Factors")
                    factor_labels = {
                        "D": "Discretionary Income",
                        "O": "Opportunity Cost",
                        "G": "Goal Alignment",
                        "L": "Long-Term Impact",
                        "B": "Behavioral"
                    }
                    
                    for f in ["D","O","G","L","B"]:
                        value = factors[f]
                        val_class = "positive" if value > 0 else "negative" if value < 0 else "neutral"
                        val_color = "#68d391" if value > 0 else "#fc8181" if value < 0 else "#cbd5e0"
                        
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; background-color: rgba(255, 255, 255, 0.05);
                                    border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; 
                                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); transition: all 0.2s ease;
                                    border-left: 4px solid #6c7ed6;">
                            <div style="font-size: 1.25rem; font-weight: 700; color: #8a94e3; margin-right: 1rem;
                                        width: 2rem; height: 2rem; display: flex; align-items: center; 
                                        justify-content: center; background-color: rgba(108, 126, 214, 0.2); 
                                        border-radius: 50%;">
                                {f}
                            </div>
                            <div style="flex: 1;">
                                {factor_labels[f]}
                            </div>
                            <div style="font-size: 1.25rem; font-weight: 700; margin-left: auto; color: {val_color};">
                                {value:+d}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if f"{f}_explanation" in factors:
                            st.caption(factors[f"{f}_explanation"])
                with c2:
                    st.markdown("### Factor Analysis")
                    radar_fig = create_radar_chart(factors)
                    st.plotly_chart(radar_fig, use_container_width=True)
                    
                    gauge_fig = create_pds_gauge(pds)
                    st.plotly_chart(gauge_fig, use_container_width=True)
    
    # -----------------------------------
    # 2. Advanced Tool
    # -----------------------------------
    else:  # selection == "Advanced Tool"
        # Icon and heading
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <div style="background-color: #fff; border-radius: 10px; padding: 10px; margin-right: 15px;">
                <span style="font-size: 24px;">⚙️</span>
            </div>
            <h1 style="font-size: 36px; color: #6c7ed6; margin: 0;">Advanced Purchase Query</h1>
        </div>
        <hr style="margin-bottom: 30px; border-color: rgba(255,255,255,0.1);">
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <p style="font-size: 16px; opacity: 0.8;">Customize <strong>all</strong> parameters for a more precise analysis.</p>
        """, unsafe_allow_html=True)
        
        with st.form("advanced_form"):
            st.subheader("Purchase Details")
            item_name = st.text_input("Item Name", "High-End Laptop")
            item_cost = st.number_input("Item Cost ($)", min_value=1.0, value=2000.0, step=100.0)
            
            st.subheader("User-Financial Data")
            leftover_income = st.number_input("Monthly Leftover Income ($)", min_value=0.0, value=1500.0, step=100.0)
            has_debt = st.selectbox("High-Interest Debt?", ["No", "Yes"])
            main_goal = st.text_input("Main Financial Goal", "Build an emergency fund")
            urgency = st.selectbox("Purchase Urgency", ["Urgent Needs","Mixed","Mostly Wants"])
            
            st.subheader("Optional Extra Context")
            extra_notes = st.text_area("Any additional context or notes?")
            
            advanced_submit = st.form_submit_button("Analyze My Purchase")
        
        if advanced_submit:
            with st.spinner("Contacting AI for advanced analysis..."):
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
                
                # Item card
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1rem; 
                            margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                            border: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center;">
                    <div style="width: 40px; height: 40px; background: rgba(108, 126, 214, 0.3); 
                                border-radius: 8px; display: flex; align-items: center; justify-content: center;
                                margin-right: 1rem; color: #8a94e3; font-weight: 700; font-size: 1.25rem;">
                        {"💼" if item_cost >= 1000 else "🛍️"}
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 1.1rem; color: rgba(255, 255, 255, 0.9);">
                            {item_name}
                        </div>
                    </div>
                    <div style="font-weight: 700; font-size: 1.2rem; color: #8a94e3;">
                        ${item_cost:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Decision box with PDS score
                st.markdown(f"""
                <div style="background: rgba(108, 126, 214, 0.1); border-radius: 12px; padding: 2rem 1.5rem;
                            margin-top: 2rem; border: 1px solid rgba(108, 126, 214, 0.3);
                            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25), 0 4px 10px rgba(0, 0, 0, 0.15);
                            text-align: center; animation: fadeInUp 0.5s ease-out forwards;">
                    <h2 style="font-size: 1.75rem; font-weight: 700; color: #8a94e3; margin-bottom: 1.5rem;">
                        Purchase Decision Score
                    </h2>
                    <div style="font-size: 3rem; font-weight: 800; color: #8a94e3; margin: 1rem 0;
                                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);">
                        {pds}
                    </div>
                    <div style="margin-top: 1rem; font-size: 1.25rem; font-weight: 600; 
                                color: {'#68d391' if rec_class == 'positive' else '#fc8181' if rec_class == 'negative' else '#ed8936'};">
                        {rec_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Decision Factors")
                    factor_labels = {
                        "D": "Discretionary Income",
                        "O": "Opportunity Cost",
                        "G": "Goal Alignment",
                        "L": "Long-Term Impact",
                        "B": "Behavioral"
                    }
                    
                    for f in ["D","O","G","L","B"]:
                        value = factors[f]
                        val_class = "positive" if value > 0 else "negative" if value < 0 else "neutral"
                        val_color = "#68d391" if value > 0 else "#fc8181" if value < 0 else "#cbd5e0"
                        
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; background-color: rgba(255, 255, 255, 0.05);
                                    border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; 
                                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); transition: all 0.2s ease;
                                    border-left: 4px solid #6c7ed6;">
                            <div style="font-size: 1.25rem; font-weight: 700; color: #8a94e3; margin-right: 1rem;
                                        width: 2rem; height: 2rem; display: flex; align-items: center; 
                                        justify-content: center; background-color: rgba(108, 126, 214, 0.2); 
                                        border-radius: 50%;">
                                {f}
                            </div>
                            <div style="flex: 1;">
                                {factor_labels[f]}
                            </div>
                            <div style="font-size: 1.25rem; font-weight: 700; margin-left: auto; color: {val_color};">
                                {value:+d}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if f"{f}_explanation" in factors:
                            st.caption(factors[f"{f}_explanation"])
                with c2:
                    st.markdown("### Factor Analysis")
                    radar_fig = create_radar_chart(factors)
                    st.plotly_chart(radar_fig, use_container_width=True)
                    
                    gauge_fig = create_pds_gauge(pds)
                    st.plotly_chart(gauge_fig, use_container_width=True)

# ------------------------------------------------------------
# Configure the theme to dark mode
# ------------------------------------------------------------
def setup_dark_theme():
    # Create a .streamlit directory if it doesn't exist
    import os
    if not os.path.exists(".streamlit"):
        os.makedirs(".streamlit")
    
    # Write dark theme config
    with open(".streamlit/config.toml", "w") as f:
        f.write("[theme]\nbase = \"dark\"\n")

# ------------------------------------------------------------
# Run the App
# ------------------------------------------------------------
if __name__ == "__main__":
    setup_dark_theme()
    main()
