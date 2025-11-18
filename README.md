# X-Ray QA Scoring Tool

## Overview
This Streamlit app helps radiology teams perform quality assurance on X-ray exams by:
- Auto-detecting body part and view from DICOM metadata
- Allowing numeric scoring for key categories
- Providing actionable feedback
- Exporting results to Excel
- Adjustable scoring weights for flexibility
- Secure login for authorized users

## Features
✔ Login protection (`mgimaging` / `QA`)  
✔ Auto body-part detection from DICOM  
✔ Weighted scoring system  
✔ Actionable suggestions  
✔ Excel export  

## Installation
```bash
git clone https://github.com/YOUR_USERNAME/QA-App.git
cd QA-App
pip install -r requirements.txt
streamlit run streamlit_qa_app.py