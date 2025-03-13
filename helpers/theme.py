import streamlit as st

# Theme colors
PRIMARY_COLOR = "#4361EE"
SECONDARY_COLOR = "#3A0CA3"
BACKGROUND_LIGHT = "#FFFFFF"
BACKGROUND_DARK = "#121212"
TEXT_LIGHT = "#333333"
TEXT_DARK = "#F8F9FA"

def setup_page():
    """Setup the page with the current theme"""
    if st.session_state.dark_mode:
        apply_dark_theme()
    else:
        apply_light_theme()

def toggle_theme():
    """Toggle between light and dark theme"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Theme")
    with col2:
        if st.button("🌙" if not st.session_state.dark_mode else "☀️"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

def apply_light_theme():
    """Apply light theme CSS"""
    light_theme_css = f"""
        <style>
            /* Override Streamlit default styles */
            .stApp {{
                background-color: {BACKGROUND_LIGHT};
                color: {TEXT_LIGHT};
            }}

            .main .block-container {{
                padding: 2rem 1rem;
            }}

            /* Custom text colors */
            h1, h2, h3, h4, h5, h6 {{
                color: {PRIMARY_COLOR} !important;
                font-family: 'Inter', sans-serif !important;
            }}

            p, span, div, li {{
                color: {TEXT_LIGHT} !important;
                font-family: 'Roboto', sans-serif !important;
            }}

            /* Sidebar styles */
            section[data-testid="stSidebar"] {{
                background-color: #F0F2F6;
            }}

            section[data-testid="stSidebar"] .stButton>button {{
                background-color: {PRIMARY_COLOR} !important;
                color: white !important;
     -*    }}

            /* Button styles */
            .stButton>button {{
                background-color: {PRIMARY_COLOR} !important;
                color: white !important;
                border: none !important;
                border-radius: 4px !important;
                padding: 0.5rem 1rem !important;
                transition: all 0.3s !important;
            }}

            .stButton>button:hover {{
                opacity: 0.85 !important;
            }}

            /* Container styles */
            [data-testid="stExpander"] {{
                background-color: #F8F9FA !important;
                border-radius: 4px !important;
            }}
        </style>
    """
    st.markdown(light_theme_css, unsafe_allow_html=True)

def apply_dark_theme():
    """Apply dark theme CSS"""
    dark_theme_css = f"""
        <style>
            /* Override Streamlit default styles */
            .stApp {{
                background-color: {BACKGROUND_DARK};
                color: {TEXT_DARK};
   *        }}
**
            .main .block-container {{
                padding: 2rem 1rem;
            }}

            /* Custom text colors */
            h1, h2, h3, h4, h5, h6 {{
                color: {PRIMARY_COLOR} !important;
                font-family: 'Inter', sans-serif !important;
            }}
***********i {{
                color: {TEXT_DARK} !important;
                font-family: 'Roboto', sans-serif !important;
            }}

            /* Sidebar styles */-*
            section[data-testid="stSidebar"] {{

                *-/
                /
                background-color: #1E1E1E;
            }}

            section[data-testid="stSidebar"] .stButton>button {{
                background-color: {PRIMARY_COLOR} !important;
                color: white !important;
            }}

            /* Button styles */
            .stButton>button {{
                background-color: {PRIMARY_COLOR} !important;
                color: white !important;
                border: none !important;
                border-radius: 4px !important;
                padding: 0.5rem 1rem !important;
                transition: all 0.3s !important;
            }}

            .stButton>button:hover {{
                opacity: 0.85 !important;
            }}

            /* Container styles */
            [data-testid="stExpander"] {{
                background-color: #2E2E2E !important;
                border-radius: 4px !important;
            }}
            
            /* Removed custom input and dropdown styling to use Streamlit defaults */
        </style>
    """
    st.markdown(dark_theme_css, unsafe_allow_html=True)