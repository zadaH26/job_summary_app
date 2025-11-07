import streamlit as st
import pandas as pd
import pdfplumber
import streamlit.components.v1 as components

# -------------------
# Sidebar settings
# -------------------
st.sidebar.header("Settings")
round_increment = st.sidebar.selectbox("Round hours to:", [0.25, 0.5, 1.0], index=0)

def round_hours(value, increment):
    try:
        return round(float(value) / increment) * increment
    except:
        return 0.0

# -------------------
# File uploader
# -------------------
st.title("Job Summary to Weekly Hours")

uploaded_files = st.file_uploader(
    "Upload your reports (CSV, Excel, PDF)", 
    type=['csv', 'xlsx', 'xls', 'pdf'], 
    accept_multiple_files=True
)

if uploaded_files:

    all_data = []

    for file in uploaded_files:
        filename = file.name
        week_name = filename.split('.')[0]
        try:
            if filename.endswith(('csv')):
                df = pd.read_csv(file)
            elif filename.endswith(('xlsx', 'xls')):
                df = pd.read_excel(file)
            elif filename.endswith('pdf'):
                text = ""
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                lines = text.split("\n")
                data = []
                for line in lines:
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
            st.warning(f"Could not read {filename}: {e}")
            continue

        # Ensure columns exist
        if 'STRAIGHT' not in df.columns and 'Regular' in df.columns:
            df.rename(columns={'Regular':'STRAIGHT'}, inplace=True)
        if 'OVERTIME' not in df.columns and 'Overtime' in df.columns:
            df.rename(columns={'Overtime':'OVERTIME'}, inplace=True)

        # Round values
        df['STRAIGHT'] = df['STRAIGHT'].apply(lambda x: round_hours(x, round_increment))
        df['OVERTIME'] = df['OVERTIME'].apply(lambda x: round_hours(x, round_increment))

        df['DATE'] = week_name
        all_data.append(df[['Job Number','DATE','OVERTIME','STRAIGHT']])

    if all_data:
        export_df = pd.concat(all_data, ignore_index=True)
        job_numbers = export_df['Job Number'].unique()

        for job in job_numbers:
            st.subheader(f"Job {job}")
            job_df = export_df[export_df['Job Number']==job].copy()
            job_df_display = job_df[['OVERTIME','STRAIGHT']]  # Only numbers columns
            st.dataframe(job_df_display, use_container_width=True)

            # -----------------------------
            # One-click copy button (numbers only)
            # -----------------------------
            numbers_text = ""
            for idx, row in job_df_display.iterrows():
                numbers_text += f"{row['OVERTIME']:.2f}\t{row['STRAIGHT']:.2f}\n"
            numbers_text = numbers_text.strip()

            html_code = f"""
            <input type="text" value="{numbers_text}" id="copyInput{job}" style="position:absolute; left:-1000px; top:-1000px;">
            <button onclick="
                var copyText = document.getElementById('copyInput{job}');
                copyText.select();
                copyText.setSelectionRange(0, 99999);
                navigator.clipboard.writeText(copyText.value);
                alert('Copied to clipboard!');
            ">📋 Copy Numbers</button>
            """
            components.html(html_code, height=50)

        # -----------------------------
        # Export buttons
        # -----------------------------
        st.download_button(
            label="⬇️ Download as CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name="job_summary.csv",
            mime="text/csv"
        )
        st.download_button(
            label="⬇️ Download as Excel",
            data=export_df.to_excel(index=False, engine='openpyxl'),
            file_name="job_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

