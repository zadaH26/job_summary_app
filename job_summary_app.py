import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Static Copy Table", layout="centered")
st.title("Static Table Copy Example")

# -------------------------------
# Static table content
# -------------------------------
numbers_text = """0.00\t0.00
0.00\t0.00
0.00\t0.00"""

# Display table in text area
st.text_area("Numbers Table", numbers_text, height=120)

# -------------------------------
# One-click copy button using HTML/JS
# -------------------------------
html_code = f"""
<input type="text" value="{numbers_text}" id="copyInput" style="position:absolute; left:-1000px; top:-1000px;">
<button onclick="
    var copyText = document.getElementById('copyInput');
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(copyText.value);
    alert('Copied to clipboard!');
">📋 Copy Numbers</button>
"""
components.html(html_code, height=60)
