import streamlit as st
import pandas as pd
import pdfplumber
import io
import re
from decimal import Decimal, ROUND_HALF_UP
import streamlit.components.v1 as components

# -------------------------------
# Helper functions
# -------------------------------

def round_hours(x, increment):
    try:
        x = Decimal(str(x))
        increment = Decimal(str(increment))
        rounded = (x / increment).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * increment
        return float(rounded)
    except Exception:
        return 0.0

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def parse_text_to_df(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    rows = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            try:
                job = parts[-1]  # Job Number is last
                straight = float(parts[0])
                overtime = float(parts[1])
                rows.append({"Job Number": job, "STRAIGHT": straight, "OVERTIME": overtime})
            except:
                continue
    if rows:
        return pd.DataFrame(rows)
    else:
        return pd.DataFrame(columns=["Job Number", "STRAIGHT", "OVERTIME"])

def process_file(file, file_type, rounding_increment):
    if file_type == "csv":
        df = pd.read_csv(file)
    elif file_type in ["xlsx", "xls"]:
        df = pd.read_excel(file)
    elif file_type == "pdf":
        text = extract_text_from_pdf(file)
        df = parse_text_to_df(text)
        return df
    else:
        return pd.DataFrame(columns=["Job Number", "STRAIGHT", "OVERTIME"])

    df.columns = [c.strip().lower() for c in df.columns]

    if "job number" not in df.columns:
        df = parse_text_to_df(df.to_string())
        return df

    if "regular" in df.columns:
        df = df.rename(columns={"regular": "STRAIGHT"})
    if "overtime" in df.columns:
        df = df.rename(columns={"overtime": "OVERTIME"})

    df["STRAIGHT"] = pd.to_numeric(df.get("STRAIGHT", 0), errors='coerce').fillna(0)
    df["OVERTIME"] = pd.to_numeric(df.get("OVERTIME", 0), errors='coerce').fillna(0)

    df["STRAIGHT"] = df["STRAIGHT"].apply(lambda x: round_hours(x, rounding_increment))
    df["OVERTIME"] = df["OVERTIME"].apply(lambda x: round_hours(x, rounding_increment))

    return df[["Job Number", "STRAIGHT", "OVERTIME"]]

def detect_week_number(filename, default_index):
    match = re.search(r"week[_\s]?(\d+)", filename, re.IGNORECASE)
    if match:
        return f"Week {int(match.group(1))}"
    else:
        return f"Week {default_index + 1}"

# -------------------------------
# Streamlit UI
# -------------------------------

st.set_page_config(page_title="Job Summary App", layout="wide")
st.title("📊 Job Summary to Weekly Hours")

st.markdown("""
Upload CSV, Excel, or PDF files for multiple weeks.  
The app will extract Job Number, Straight (Regular), and Overtime hours,  
round them to your chosen increment, and display weekly summaries.
""")

# Rounding selector
rounding_increment = st.selectbox(
    "Select rounding increment (hours):",
    options=[0.25, 0.5, 1.0],
    index=0
)

uploaded_files = st.file_uploader(
    "Choose files (CSV, Excel, PDF)",
    type=["csv", "xlsx", "xls", "pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    all_weeks = {}
    for i, file in enumerate(uploaded_files):
        week_num = detect_week_number(file.name, i)
        file_ext = file.name.split(".")[-1].lower()
        df = process_file(file, file_ext, rounding_increment)
        if not df.empty:
            all_weeks[week_num] = df

    if all_weeks:
        st.success("✅ Files processed successfully!")

        # Sort weeks by number
        def week_sort_key(w):
            match = re.search(r"Week (\d+)", w)
            return int(match.group(1)) if match else 0

        sorted_weeks = sorted(all_weeks.keys(), key=week_sort_key)
        job_numbers = sorted({job for week in all_weeks.values() for job in week["Job Number"]})

        # Display results
        for job in job_numbers:
            st.subheader(f"Job {job}")
            display_rows = []

            for week_name in sorted_weeks:
                df = all_weeks[week_name]
                job_row = df[df["Job Number"] == job]
                if not job_row.empty:
                    straight = float(job_row.iloc[0]["STRAIGHT"])
                    overtime = float(job_row.iloc[0]["OVERTIME"])
                else:
                    straight = 0.0
                    overtime = 0.0

                straight = round_hours(straight, rounding_increment)
                overtime = round_hours(overtime, rounding_increment)
                display_rows.append([overtime, straight])  # Overtime first, Straight second

            # Build table string with EXACT layout
            table_str = "\n".join([f"{r[0]:.2f}\t{r[1]:.2f}" for r in display_rows])
            st.text(table_str)

            # One-click copy button
            html_code = f"""
            <button onclick="
                const text = `{table_str}`;
                navigator.clipboard.writeText(text);
                alert('Copied!');
            ">📋 Copy Numbers</button>
            """
            components.html(html_code, height=50)
