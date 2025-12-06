def get_main_css() -> str:
    """Return Anthropic Light Inspired CSS to force theme application."""
    return """
<style>
/* 1. DEFINE FONTS MANUALLY (Since config.toml needs restart) */
@font-face {
    font-family: 'SpaceGrotesk';
    src: url('app/static/SpaceGrotesk-VariableFont_wght.ttf') format('truetype');
    font-weight: 300 700;
    font-style: normal;
}
@font-face {
    font-family: 'SpaceMono';
    src: url('app/static/SpaceMono-Bold.ttf') format('truetype');
    font-weight: 700;
    font-style: normal;
}
@font-face {
    font-family: 'SpaceMono';
    src: url('app/static/SpaceMono-Regular.ttf') format('truetype');
    font-weight: 400;
    font-style: normal;
}

/* 2. APPLY THEME COLORS & VARIABLES */
:root {
    --primary-color: #cb785c;
    --background-color: #fdfdf8;
    --secondary-background-color: #ecebe3;
    --text-color: #3d3a2a;
    --font: 'SpaceGrotesk', sans-serif;
    --code-font: 'SpaceMono', monospace;
    --border-color: #d3d2ca;
}

/* 3. GENERAL APP STYLING */
.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
    font-family: var(--font);
}

.stSidebar {
    background-color: #f0f0ec;
    border-right: 1px solid var(--border-color);
    min-width: 350px !important; /* Increased to 350px to fit full header logic */
    /* Streamlit's sidebar width is controlled by JS often, but min-width helps */
}
/* Also target the section that holds the width */
[data-testid="stSidebar"] {
    min-width: 350px !important;
}

/* 4. TYPOGRAPHY POLISH */
h1 {
    font-family: var(--font) !important;
    font-weight: 600 !important;
    font-size: 3rem !important;
    color: var(--text-color) !important;
    letter-spacing: -0.02em !important;
}

h2, h3 {
    font-family: var(--font) !important;
    font-weight: 500 !important;
    color: var(--text-color) !important;
}

p, div, label, .stMarkdown {
    font-family: var(--font) !important;
    color: var(--text-color);
    font-weight: 400;
}

code, .stCodeBlock, .stCodeBlock pre {
    font-family: var(--code-font) !important;
    background-color: #ecebe4 !important; /* Muted code background */
}

/* 5. ELEVATED CARD STYLING (Containers) */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-color: var(--border-color) !important;
    background-color: white !important; /* Cards pop against the cream bg */
    border-radius: 0.75rem !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* 6. BUTTONS & PILLS */
button[kind="primary"] {
    background-color: var(--primary-color) !important;
    border-radius: 9999px !important;
    border: none !important;
    color: white !important;
    font-weight: 500 !important;
    transition: all 0.2s ease;
}
button[kind="primary"]:hover {
    opacity: 0.9;
    box-shadow: 0 4px 6px rgba(203, 120, 92, 0.2);
}

button[kind="secondary"], button[kind="tertiary"] {
    border-radius: 9999px !important;
    color: var(--text-color) !important;
    font-weight: 500 !important;
}

[data-testid="stPills"] button {
    border-radius: 9999px !important;
    border: 1px solid var(--border-color) !important;
    background-color: white !important;
    font-family: var(--font) !important;
    font-size: 0.9rem !important;
}

[data-testid="stPills"] button[aria-selected="true"] {
    background-color: var(--secondary-background-color) !important;
    border-color: var(--primary-color) !important;
    color: var(--primary-color) !important;
    font-weight: 600 !important;
}

/* 7. CHAT INPUT */
.stChatInputContainer {
    padding-bottom: 20px;
}
.stChatInputContainer textarea {
    background-color: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 1.5rem !important;
    font-family: var(--font) !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}
.stChatInputContainer textarea:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 2px rgba(203, 120, 92, 0.1) !important;
}

/* 8. SIDEBAR REFINEMENTS */
[data-testid="stSidebar"] hr {
    margin: 1.5rem 0 !important;
    border-color: var(--border-color) !important;
}

/* Force left alignment & reduce button-ness for sidebar buttons */
/* 9. NUCLEAR SIDEBAR TEXT STYLING */
/* Target ALL buttons in sidebar to strip them naked */
[data-testid="stSidebar"] button {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    line-height: 1.5 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    color: var(--text-color) !important;
    font-weight: 400 !important;
    display: block !important;
    width: 100% !important;
}

/* Handle Hover/Focus/Active states to prevent gray box */
[data-testid="stSidebar"] button:hover,
[data-testid="stSidebar"] button:focus,
[data-testid="stSidebar"] button:active {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    color: var(--primary-color) !important;
    text-decoration: none !important;
    outline: none !important;
}

/* Specifically for the Container elements wrapping the button text */
[data-testid="stSidebar"] button div {
    display: inline !important;
}

/* Tertiary Buttons (Recent Chat Items) */
[data-testid="stSidebar"] button[kind="tertiary"] {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0.2rem 0 !important;
}

/* Delete Button (Trash Icon) - Target 2nd column */
[data-testid="stSidebar"] div[data-testid="column"]:nth-of-type(2) button {
    opacity: 0;
    transition: opacity 0.2s ease;
}

/* On Hover of the COLUMN CONTAINER (the row), show the delete button */
[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]:hover div[data-testid="column"]:nth-of-type(2) button {
    opacity: 1;
}

/* Active Chat Styling (Primary Button as Text) */
[data-testid="stSidebar"] button[kind="primary"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--primary-color) !important;
    font-weight: 700 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding-left: 0 !important;
}
/* Disable hover effect on primary to keep it static text-like */
[data-testid="stSidebar"] button[kind="primary"]:hover {
    background: transparent !important;
    box-shadow: none !important;
}


/* 10. CENTERING SUGGESTIONS (PILLS) */
/* Force the internal flex container of st.pills to center align */
/* Targeting multiple potential IDs for robustness */
[data-testid="stPills"] > div,
[data-testid="stButtonGroup"] > div,
[data-testid="stSegmentedControl"] > div {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    flex-wrap: wrap !important;
    width: 100% !important;
}

/* Ensure individual pills don't stretch weirdly */
[data-testid="stPills"] button,
[data-testid="stButtonGroup"] button,
[data-testid="stSegmentedControl"] button {
    flex: 0 1 auto !important;
}



</style>
"""

