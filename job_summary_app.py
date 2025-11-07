import streamlit as st
import pandas as pd
import pdfplumber
import streamlit.components.v1 as components
import re

st.title("Job Summary - Exact Copy Layout")

# Sidebar: rounding increment
round_increment = st.sidebar.selectbox("Round hours to:", [0.25, 0.5, 1.0], index=0)
num_weeks = 3  # default number of rows per job

def round_hours(val):
    try:
        return round(float(val)/round_increment)*round_increment
    except:
        return 0.0

# Upload files
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
                data = []
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        for line in text.split("\n"):
                            # Try to detect lines with numeric Regular and Overtime
                            parts = line.strip().split()
                            if len(parts) < 3:
                                continue
                            # Attempt to parse numbers from the line
                            numbers = []
                            for p in parts:
                                try:
                                    numbers.append(float(p))
                                except:
                                    pass
                            if len(numbers) >= 2:
                                # Last number is job number OR first number? detect
                                overtime, straight = numbers[0], numbers[1]
                                # Try to detect job number
                                job_match = re.search(r'\b\d{3,5}\b', line)
                                if job_match:
                                    job = job_match.group()
                                    straight = round_hours(straight)
                                    overtime = round_hours(overtime)
                                    data.append({"Job": job, "STRAIGHT": straight, "OVERTIME": overtime})
                df = pd.DataFrame(data)
            else:
                continue
        except Exception as e:
            st.warning(f"Could not read {file.name}: {e}")
            continue

        # Standardize column names
        if 'Regular' in df.columns and 'STRAIGHT' not in df.columns:
            df.rename(columns={'Regular':'STRAIGHT'}, inplace=True)
        if 'Overtime' in df.columns and 'OVERTIME' not in df.columns:
            df.rename(columns={'Overtime':'OVERTIME'}, inplace=True)

        for _, row in df.iterrows():
            job = str(row.get('Job Number') or row.get('Job'))
            straight = round_hours(row['STRAIGHT'])
            overtime = round_hours(row['OVERTIME'])

            # Only keep jobs with non-zero hours
            if straight == 0.0 and overtime == 0.0:
                continue

            if job not in jobs:
                jobs[job] = {}
            jobs[job][week_name] = (overtime, straight)

    # Display each job
    for job, weeks in jobs.items():
        st.subheader(f"Job {job}")
        display_rows = []

        # Ensure always num_weeks rows
        for w in range(1, num_weeks+1):
            week_name = f"Week {w}"
            if week_name in weeks:
                display_rows.append(list(weeks[week_name]))
            else:
                display_rows.append([0.0, 0.0])

        # Display table exactly like you want
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

