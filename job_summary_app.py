import streamlit as st
import pandas as pd
import pdfplumber
import streamlit.components.v1 as components

st.title("Job Summary - Exact Copy Layout")

# Sidebar: round increment
round_increment = st.sidebar.selectbox("Round hours to:", [0.25, 0.5, 1.0], index=0)
num_weeks = 5  # default to 5 weeks

def round_hours(val):
    try:
        return round(float(val)/round_increment)*round_increment
    except:
        return 0.0

uploaded_files = st.file_uploader(
    "Upload CSV, Excel, or PDF",
    type=['csv','xlsx','xls','pdf'],
    accept_multiple_files=True
)

if uploaded_files:
    jobs = {}

    for idx, file in enumerate(uploaded_files):
        week_num = idx + 1
        week_name = f"Week {week_num}"

        try:
            if file.name.endswith('csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('xlsx','xls')):
                df = pd.read_excel(file)
            elif file.name.endswith('pdf'):
                # Extract table-like lines
                text = ""
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                data = []
                for line in text.split("\n"):
                    parts = line.strip().split()
                    if len(parts) < 2:
                        continue
                    # Try to detect Job Number as last numeric token
                    job_candidate = parts[-1]
                    try:
                        job = str(int(job_candidate))
                        # STRAIGHT = first number, OVERTIME = second number (based on your sample)
                        straight = round_hours(parts[0])
                        overtime = round_hours(parts[1])
                        data.append({"Job": job, "STRAIGHT": straight, "OVERTIME": overtime})
                    except:
                        continue
                df = pd.DataFrame(data)
            else:
                continue
        except:
            continue

        # Standardize column names
        if 'Regular' in df.columns and 'STRAIGHT' not in df.columns:
            df.rename(columns={'Regular':'STRAIGHT'}, inplace=True)
        if 'Overtime' in df.columns and 'OVERTIME' not in df.columns:
            df.rename(columns={'Overtime':'OVERTIME'}, inplace=True)
        if 'Job Number' in df.columns:
            df.rename(columns={'Job Number':'Job'}, inplace=True)

        for _, row in df.iterrows():
            try:
                job = str(row['Job'])
                straight = round_hours(row['STRAIGHT'])
                overtime = round_hours(row['OVERTIME'])
                # Skip rows with invalid job
                if not job.isdigit():
                    continue
            except:
                continue

            if job not in jobs:
                jobs[job] = {}
            jobs[job][week_name] = (overtime, straight)

    # Display
    for job, weeks in jobs.items():
        st.subheader(f"Job {job}")
        display_rows = []
        for w in range(1, num_weeks+1):
            week_name = f"Week {w}"
            if week_name in weeks:_
