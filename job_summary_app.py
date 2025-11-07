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

# App title
st.title("Job Summary to Weekly Hours")

uploaded_files = st.file_uploader(
    "Upload your reports (CSV, Excel, PDF)", 
    type=['csv', 'xlsx', 'xls', 'pdf'], 
    accept_multiple_files=True
)

if uploaded_files:

    all_data = []

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
            st.warning(f"Could not read {file.name}: {e}")
            continue

        # Keep only the relevant columns
        df = df[['Job Number', 'STRAIGHT', 'OVERTIME']]

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

            job_df = export_df[export_df['Job Number']==job]

            # Ensure exactly num_weeks rows
            display_rows = []
            for week_idx in range(1, num_weeks+1):
                week_name = f"Week {week_idx}"
                row = job_df[job_df['DATE']==week_name]
                if not row.empty:
                    ot = row['OVERTIME'].sum()
                    st_hours = row['STRAIGHT'].sum()
                else:
                    ot = 0.0
                    st_hours = 0.0
                display_rows.append({"OVERTIME": ot, "STRAIGHT": st_hours})

            job_df_display = pd.DataFrame(display_rows, columns=['OVERTIME','STRAIGHT'])

            st.dataframe(job_df_display, use_container_width=True)

            # One-click copy button (exactly two numbers per row)
            numbers_text = ""
            for _, row in job_df_display.iterrows():
                numbers_text += f"{row['OVERTIME']:.2f}    {row['STRAIGHT']:.2f}\n"
            numbers_text = numbers_text.strip()

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

        # Export buttons
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
