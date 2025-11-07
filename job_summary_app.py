import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import pdfplumber

st.title("Job Summary - Weekly Hours Table")

# Sidebar: rounding increment
round_increment = st.sidebar.selectbox("Round to:", [0.25, 0.5, 1.0], index=0)

def round_value(val):
    try:
        return round(float(val)/round_increment)*round_increment
    except:
        return 0.0

# Upload files
uploaded_files = st.file_uploader(
    "Upload CSV, Excel, or PDF files (one per week, up to 5 files)",
    type=['csv', 'xlsx', 'xls', 'pdf'],
    accept_multiple_files=True
)

num_weeks = 5  # always show 5 weeks

if uploaded_files:
    jobs = {}

    for idx, file in enumerate(uploaded_files):
        week_num = idx + 1
        week_name = f"Week {week_num}"

        # Read file
        try:
            if file.name.endswith('csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('xlsx','xls')):
                df = pd.read_excel(file)
            elif file.name.endswith('pdf'):
                # Extract tables from PDF
                with pdfplumber.open(file) as pdf:
                    all_tables = []
                    for page in pdf.pages:
                        for table in page.extract_tables():
                            all_tables.extend(table)
                    df = pd.DataFrame(all_tables[1:], columns=all_tables[0])
            else:
                st.warning(f"Unsupported file: {file.name}")
                continue
        except Exception as e:
            st.error(f"Cannot read file {file.name}: {e}")
            continue

        # Process rows
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

        for w in range(1, num_weeks+1):
            week_name = f"Week {w}"
            if week_name in weeks:
                display_rows.append(list(weeks[week_name]))
            else:
                display_rows.append([0.00, 0.00])

        # Show table as plain text exactly like you want
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
