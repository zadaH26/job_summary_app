import streamlit as st
import pandas as pd
import pdfplumber
import streamlit.components.v1 as components

st.title("Job Summary - Exact Copy Layout")

# Sidebar settings
round_increment = st.sidebar.selectbox("Round hours to:", [0.25, 0.5, 1.0], index=0)
num_weeks = 3  # number of rows to show

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
                text = ""
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                data = []
                for line in text.split("\n"):
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        try:
                            job = parts[0]
                            straight = round_hours(parts[1])
                            overtime = round_hours(parts[2])
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

        for _, row in df.iterrows():
            job = str(row['Job Number'] if 'Job Number' in row else row['Job'])
            straight = round_hours(row['STRAIGHT'])
            overtime = round_hours(row['OVERTIME'])

            if job not in jobs:
                jobs[job] = {}
            jobs[job][week_name] = (overtime, straight)

    for job, weeks in jobs.items():
        st.subheader(f"Job {job}")
        display_rows = []

        # build rows exactly num_weeks
        for w in range(1,num_weeks+1):
            week_name = f"Week {w}"
            if week_name in weeks:
                display_rows.append(list(weeks[week_name]))
            else:
                display_rows.append([0.0,0.0])

        # Display table
        table_str = "\n".join([f"{r[0]:.2f}\t{r[1]:.2f}" for r in display_rows])
        st.text(table_str)  # shows exactly the layout you want

        # Copy button - one click copy
        html_code = f"""
        <button onclick="
            const text = `{table_str}`;
            navigator.clipboard.writeText(text);
            alert('Copied!');
        ">📋 Copy Numbers</button>
        """
        components.html(html_code, height=50)
