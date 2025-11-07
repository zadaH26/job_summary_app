import streamlit as st
import pandas as pd
import pdfplumber
import streamlit.components.v1 as components

# Sidebar settings
st.sidebar.header("Settings")
round_increment = st.sidebar.selectbox("Round hours to:", [0.25, 0.5, 1.0], index=0)
num_weeks = 3  # Always show 3 rows

def round_hours(value, increment):
    try:
        return round(float(value) / increment) * increment
    except:
        return 0.0

st.title("Job Summary to Weekly Hours")

uploaded_files = st.file_uploader(
    "Upload your reports (CSV, Excel, PDF)", 
    type=['csv', 'xlsx', 'xls', 'pdf'], 
    accept_multiple_files=True
)

if uploaded_files:

    all_jobs_data = {}

    for idx, file in enumerate(uploaded_files):
        week_num = idx + 1
        week_name = f"Week {week_num}"
        try:
            if file.name.endswith('csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('xlsx', 'xls')):
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
                            job_num = parts[0]
                            reg = float(parts[1])
                            ot = float(parts[2])
                            data.append({"Job Number": job_num, "STRAIGHT": reg, "OVERTIME": ot})
                        except:
                            continue
                df = pd.DataFrame(data)
            else:
                continue
        except Exception as e:
            st.warning(f"Could not read {file.name}: {e}")
            continue

        # Ensure columns exist
        if 'STRAIGHT' not in df.columns and 'Regular' in df.columns:
            df.rename(columns={'Regular':'STRAIGHT'}, inplace=True)
        if 'OVERTIME' not in df.columns and 'Overtime' in df.columns:
            df.rename(columns={'Overtime':'OVERTIME'}, inplace=True)

        # Round values
        df['STRAIGHT'] = df['STRAIGHT'].apply(lambda x: round_hours(x, round_increment))
        df['OVERTIME'] = df['OVERTIME'].apply(lambda x: round_hours(x, round_increment))

        # Collect data by job
        for _, row in df.iterrows():
            job = row['Job Number']
            if job not in all_jobs_data:
                all_jobs_data[job] = {}
            all_jobs_data[job][week_name] = {"OVERTIME": row['OVERTIME'], "STRAIGHT": row['STRAIGHT']}

    # Display each job
    for job, weeks_data in all_jobs_data.items():
        st.subheader(f"Job {job}")

        display_rows = []
        for week_idx in range(1, num_weeks+1):
            week_name = f"Week {week_idx}"
            if week_name in weeks_data:
                ot = weeks_data[week_name]["OVERTIME"]
                st_hours = weeks_data[week_name]["STRAIGHT"]
            else:
                ot = 0.0
                st_hours = 0.0
            display_rows.append([ot, st_hours])

        job_df_display = pd.DataFrame(display_rows, columns=['OVERTIME','STRAIGHT'])

        # Display table
        st.dataframe(job_df_display, use_container_width=True)

        # Copy button
        numbers_text = "\n".join([f"{row[0]:.2f}    {row[1]:.2f}" for row in display_rows])
        html_code = f"""
        <textarea id="copyInput{job}" style="position:absolute; left:-1000px; top:-1000px;">{numbers_text}</textarea>
        <button onclick="
            var copyText = document.getElementById('copyInput{job}');
            copyText.select();
            navigator.clipboard.writeText(copyText.value);
            alert('Copied to clipboard!');
        ">📋 Copy Numbers</button>
        """
        components.html(html_code, height=50)
