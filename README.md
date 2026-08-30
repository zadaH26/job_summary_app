# Job Summary App

Job Summary App is a Python and Streamlit tool built to speed up weekly job-costing summaries and reduce manual calculation errors.

I created this project after working with job-costing workflows where job numbers, straight time, and overtime had to be copied, checked, rounded, and summarized by hand. The app automates that repetitive workflow so summaries can be prepared faster, more consistently, and with less human-error risk.

## What It Does

- Uploads CSV, Excel, or PDF job-summary files
- Extracts job numbers, straight hours, and overtime hours
- Groups results by week and job number
- Applies consistent time-rounding rules
- Displays clean weekly summaries for review
- Provides copy-ready tables and CSV export

## Why I Built It

The goal was to replace a slow manual workflow with a faster and more reliable process.

This project demonstrates:

- Python automation
- Data cleaning with Pandas
- File parsing across CSV, Excel, and PDF formats
- Job-costing and operations reporting
- Streamlit dashboard development
- Practical business problem solving

## Tech Stack

- Python
- Streamlit
- Pandas
- OpenPyXL
- PDFPlumber

## Project Structure

```text
job_summary_app.py   Main Streamlit application
requirements.txt     Python dependencies
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run job_summary_app.py
```

## Portfolio Summary

Built a Python and Streamlit job-costing automation tool that imports CSV, Excel, and PDF files, extracts job numbers and hours, applies consistent rounding, and exports weekly summaries to reduce manual calculation time and human-error risk.
