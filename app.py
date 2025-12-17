import streamlit as st
import pandas as pd
import time
import joblib
from model import recommend_hotel

# Page configuration
st.set_page_config(
    page_title="Hotel Recommendation System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: white;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 3rem 2rem;
        margin: -2rem -2rem 3rem -2rem;
        text-align: center;
        border-bottom: 4px solid #1E40AF;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .stButton>button {
        background: #1E40AF;
        color: white;
        border: none;
        padding: 1rem 2.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 1.125rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(30, 64, 175, 0.25);
    }
    
    .selected-pref-box {
    background: #f1f5f9;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 2rem;
    }

    .selected-pref-title {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
        color: #0F172A;
    }

    .selected-pref-chip {
        display: inline-block;
        background: #1E40AF;
        color: white;
        padding: 0.4rem 0.85rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .stButton>button:hover {
        background: #1E3A8A;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.35);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'country' not in st.session_state:
    st.session_state.country = None
if 'preferences' not in st.session_state:
    st.session_state.preferences = []
if 'custom_desc' not in st.session_state:
    st.session_state.custom_desc = ""
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

# Country data
countries = {
    "Austria": {"flag": "🇦🇹", "desc": "Vienna, Salzburg, Alpine charm", "color": "#DC2626"},
    "France": {"flag": "🇫🇷", "desc": "Paris, French Riviera, Loire Valley", "color": "#1E40AF"},
    "Italy": {"flag": "🇮🇹", "desc": "Rome, Florence, Venice", "color": "#059669"},
    "Netherlands": {"flag": "🇳🇱", "desc": "Amsterdam, Rotterdam, The Hague", "color": "#EA580C"},
    "Spain": {"flag": "🇪🇸", "desc": "Barcelona, Madrid, Costa del Sol", "color": "#CA8A04"},
    "United Kingdom": {"flag": "UK", "desc": "London, Edinburgh, Manchester", "color": "#7C3AED"}
}

# Travel preferences
preferences_data = [
    {"label": "Business Trip", "desc": "Business trip couple standard double room stayed 2 nights", "icon": "💼", "category": "Purpose", "color": "#1E40AF"},
    {"label": "Romantic Getaway", "desc": "Leisure trip couple suite stayed 3 nights", "icon": "❤️", "category": "Purpose", "color": "#BE123C"},
    {"label": "Family Vacation", "desc": "Leisure trip family with young children duplex double room stayed 5 nights", "icon": "👨‍👩‍👧‍👦", "category": "Purpose", "color": "#059669"},
    {"label": "Solo Traveler", "desc": "Leisure trip solo traveler single room stayed 2 nights", "icon": "🧳", "category": "Purpose", "color": "#7C3AED"},
    {"label": "Peaceful Retreat", "desc": "Leisure trip couple standard room stayed 4 nights quiet location", "icon": "🌊", "category": "Atmosphere", "color": "#0891B2"},
    {"label": "Duplex Suite", "desc": "Leisure trip couple duplex double room stayed 3 nights", "icon": "🛏️", "category": "Room Type", "color": "#EA580C"},
    {"label": "Weekend Getaway", "desc": "Leisure trip couple stayed 2 nights submitted from mobile device", "icon": "☕", "category": "Duration", "color": "#CA8A04"},
    {"label": "Luxury Stay", "desc": "Leisure trip couple executive double room stayed 4 nights", "icon": "✨", "category": "Style", "color": "#BE185D"},
    {"label": "Group Travel", "desc": "Leisure trip group triple room stayed 3 nights", "icon": "🏠", "category": "Purpose", "color": "#6366F1"}
]


def step_1_country_selection():
    """Step 1: Country Selection"""
    st.markdown("<h2 style='text-align: center; font-size: 2.25rem; font-weight: 700; color: white; margin-bottom: 0.75rem;'>Select Your Destination</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.125rem; color: #D6CFC7; margin-bottom: 3rem; font-weight: 400;'>Choose a country to discover the best hotels matching your preferences</p>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, (country, data) in enumerate(countries.items()):
        with cols[idx % 3]:
            is_selected = st.session_state.country == country
            
            if st.button(
                f"{data['flag']}\n\n**{country}**\n\n{data['desc']}", 
                key=f"country_{country}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.country = country
                st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.session_state.country:
            if st.button("Continue to Preferences →", key="next_step_1", type="primary", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
        else:
            st.button("Continue to Preferences →", key="next_step_1_disabled", disabled=True, use_container_width=True)

def step_2_preferences():
    """Step 2: Travel Preferences"""
    st.markdown("<h2 style='text-align: center; font-size: 2.25rem; font-weight: 700; color: white; margin-bottom: 0.75rem;'>Choose Your Travel Preferences</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.125rem; color: #D6CFC7; margin-bottom: 2rem; font-weight: 400;'>Select one or more options that best describe your ideal stay</p>", unsafe_allow_html=True)
    
    # --- Selected Preferences Summary ---
    if st.session_state.preferences:
        selected_html = """
        <div class="selected-pref-box">
            <div class="selected-pref-title">✅ Selected Preferences</div>
        """
        for pref in st.session_state.preferences:
            selected_html += f'<span class="selected-pref-chip">{pref}</span>'
        selected_html += "</div>"

        st.markdown(selected_html, unsafe_allow_html=True)

    if st.session_state.preferences:
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <span style='background: #1E40AF; color: white; padding: 0.875rem 1.75rem; 
                         border-radius: 0.5rem; font-weight: 600; font-size: 1rem;
                         box-shadow: 0 2px 8px rgba(30, 64, 175, 0.25);'>
                ✓ {len(st.session_state.preferences)} Preference(s) Selected
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, pref in enumerate(preferences_data):
        with cols[idx % 3]:
            is_selected = pref['label'] in st.session_state.preferences
            
            if st.button(
                f"{pref['icon']} {pref['label']}",
                key=f"pref_btn_{pref['label']}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                if is_selected:
                    st.session_state.preferences.remove(pref['label'])
                else:
                    st.session_state.preferences.append(pref['label'])
                st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("### Additional Requirements (Optional)")
    st.session_state.custom_desc = st.text_area(
        "Additional Requirements",
        value=st.session_state.custom_desc,
        placeholder="e.g., 'Need parking facilities, spa access, and proximity to city center'",
        height=100,
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Destinations", key="back_step_2", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    
    with col3:
        can_proceed = len(st.session_state.preferences) > 0 or st.session_state.custom_desc.strip()
        if can_proceed:
            if st.button("Find Hotels →", key="next_step_2", type="primary", use_container_width=True):
                st.session_state.step = 3
                st.rerun()
        else:
            st.button("Find Hotels →", key="next_step_2_disabled", disabled=True, use_container_width=True)

def step_3_results():
    """Step 3: Show Recommendations"""
    
    if st.session_state.recommendations is None:
        # Combine preferences
        combined_desc = ""
        if st.session_state.preferences:
            selected_prefs = [p for p in preferences_data if p['label'] in st.session_state.preferences]
            combined_desc = " ".join([p['desc'] for p in selected_prefs])
        if st.session_state.custom_desc.strip():
            combined_desc += " " + st.session_state.custom_desc.strip() if combined_desc else st.session_state.custom_desc.strip()
        
        # Get recommendations
        with st.spinner("Analyzing preferences with your model..."):
            
            try:
                # Call your model exactly like in your notebook
                results = recommend_hotel(
    st.session_state.country.lower(),
    combined_desc
)

                
                st.session_state.recommendations = results
                time.sleep(1)
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                import traceback
                with st.expander("Show error details"):
                    st.code(traceback.format_exc())
                st.session_state.recommendations = pd.DataFrame()
        
        st.rerun()
    
    # Display results
    if st.session_state.recommendations is not None and not st.session_state.recommendations.empty:
        st.markdown(
    f"<h3 style='color: black;'>🎉 Recommended Hotels in {st.session_state.country}</h3>",
    unsafe_allow_html=True
)
        st.markdown(f"<p style='color: black;'>Showing recommendations...</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        for idx in range(len(st.session_state.recommendations)):
            row = st.session_state.recommendations.iloc[idx]
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"<h2 style='color: black;'>{row['hotel_name']}</h2>",unsafe_allow_html=True)
                st.markdown(f"<p style='color: black;'>📍 {row['hotel_address']}</p>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<div style='background: #1E40AF; color: white; padding: 0.7rem; border-radius: 0.7rem; text-align: center; font-size: 1.2rem; font-weight: bold;'>⭐ {row['final_rating']}</div>", unsafe_allow_html=True)
            
            st.markdown("<hr style='border: 1px solid #48494B;'>", unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ No hotels found. Try different preferences.")
        with st.expander("Debug Info"):
            st.write("Recommendations:", st.session_state.recommendations)
    
    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back", key="back_step_3", use_container_width=True):
            st.session_state.step = 2
            st.session_state.recommendations = None
            st.rerun()
    with col3:
        if st.button("🔄 New Search", key="reset", type="primary", use_container_width=True):
            st.session_state.step = 1
            st.session_state.country = None
            st.session_state.preferences = []
            st.session_state.custom_desc = ""
            st.session_state.recommendations = None
            st.rerun()

def main():
    # Header
    st.markdown("""
    <div class='main-header'>
        <h1 style='color: white; font-size: 3rem; font-weight: 700; margin: 0;'>Hotel Recommendation System</h1>
        <p style='color: #CBD5E1; font-size: 1.1rem; margin-top: 0.75rem;'>
            Enterprise AI-Powered Hotel Discovery Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    
    # Show current step
    if st.session_state.step == 1:
        step_1_country_selection()
    elif st.session_state.step == 2:
        step_2_preferences()
    elif st.session_state.step == 3:
        step_3_results()

if __name__ == "__main__":
    main()