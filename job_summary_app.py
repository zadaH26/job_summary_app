import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.title("Job Summary - Weekly Hours Table")

# Sidebar: rounding
round_increment = st.sidebar.selectbox("Round to:", [0.25, 0.5, 1.0], index=0)

def round_value(val):
    try:
        return round(float(val)/round_increment)*round_increment
    except:
        return 0.0

# Upload CSV or Excel files (one per week)
uploaded_files = st.file_uploader(
    "Upload CSV or Excel files (one per week, up to 5 files for Weeks 1-5)",
    type=['csv', 'xlsx', 'xls'],
    accept_multiple_files=True
)

num_weeks = 5  # always show 5 weeks

if uploaded_files:
    jobs = {}  # dictionary to store job data

    # Read each file as one week
    for idx, file in enumerate(uploaded_files):
        week_num = idx + 1
        week_name = f"Week {week_num}"

        try:
            if file.name.endswith('csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except:
            st.error(f"Cannot read file: {file.name}")
            continue

        # Expecting columns: Job Number, Regular, Overtime
        for _, row in df.iterrows():
            try:
                job_number = str(row['Job Number'])
                straight = round_value(row['Regular'])
                overtime = round_value(row['Overtime'])
            except:
                continue

            if job_number not in jobs:
                jobs[job_number] = {}

            jobs[job_number][week_name] = (overtime, straight)

    # Display each job
    for job, weeks in jobs.items():
        st.subheader(f"Job {job}")
        display_rows = []

        # Build 5-week table
        for w in range(1, num_weeks+1):
            week_name = f"Week {w}"
            if week_name in weeks:
                display_rows.append(list(weeks[week_name]))
            else:
                display_rows.append([0.00, 0.00])  # Only TWO columns!

        # Create DataFrame for exact formatting
        df_display = pd.DataFrame(display_rows, columns=["OVERTIME", "STRAIGHT"])
        df_display.index = [f"Week {i}" for i in range(1, num_weeks+1)]

        st.dataframe(df_display.style.format("{:.2f}"))

        # One-click copy button
        table_str = "\n".join([f"{r[0]:.2f}\t{r[1]:.2f}" for r in display_rows])
        html_code = f"""
        <button onclick="
            const text = `{table_str}`;
            navigator.clipboard.writeText(text);
            alert('Copied!');
        ">📋 Copy Job {job}</button>
        """
        components.html(html_code, height=50)
