import streamlit as stimport stream os
import pydicom

# ---------------- LOGIN ----------------
def login():
    st.title("QA App Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "mgimaging" and password == "QA":
            st.session_state["logged_in"] = True
        else:
            st.error("Invalid credentials")

# ---------------- AUTO-DETECT BODY PART ----------------
def detect_body_part(dicom_file):
    try:
        ds = pydicom.dcmread(dicom_file)
        body_part = getattr(ds, "BodyPartExamined", "Unknown")
        view = getattr(ds, "ViewPosition", "Unknown")
        return body_part, view
    except Exception:
        return "Unknown", "Unknown"

# ---------------- MAIN APP ----------------
def main_app():
    st.title("X-Ray QA Scoring Tool")

    # Upload DICOM or image file
    dicom_file = st.file_uploader("Upload Image or DICOM file", type=["dcm", "jpg", "jpeg", "png"])

    if dicom_file:
        if dicom_file.name.lower().endswith(".dcm"):
            # Process DICOM file
            body_part, view = detect_body_part(dicom_file)
            st.success(f"Detected Body Part: {body_part}, View: {view}")
        else:
            # Handle non-DICOM image gracefully
            st.warning("Image uploaded (not DICOM). Please select Body Part and View manually below.")
            body_part = st.selectbox("Body Part", ["Chest", "Abdomen", "Extremity", "Spine"])
            view = st.selectbox("View", ["AP", "PA", "Lateral", "Oblique"])
    else:
        # No file uploaded yet
        body_part = st.selectbox("Body Part", ["Chest", "Abdomen", "Extremity", "Spine"])
        view = st.selectbox("View", ["AP", "PA", "Lateral", "Oblique"])

    # Adjustable weights
    st.sidebar.header("Adjust Scoring Weights")
    weights = {
        "Collimation": st.sidebar.slider("Collimation Weight", 0.0, 1.0, 0.3),
        "Positioning": st.sidebar.slider("Positioning Weight", 0.0, 1.0, 0.3),
        "Exposure": st.sidebar.slider("Exposure Weight", 0.0, 1.0, 0.2),
        "Artifacts": st.sidebar.slider("Artifacts Weight", 0.0, 1.0, 0.2)
    }

    # Numeric scoring
    st.subheader("Enter Scores (0-10)")
    collimation = st.number_input("Collimation", 0, 10)
    positioning = st.number_input("Positioning", 0, 10)
    exposure = st.number_input("Exposure", 0, 10)
    artifacts = st.number_input("Artifacts", 0, 10)

    # Calculate weighted score
    total_score = (collimation * weights["Collimation"] +
                   positioning * weights["Positioning"] +
                   exposure * weights["Exposure"] +
                   artifacts * weights["Artifacts"])

    st.write(f"**Total Weighted Score:** {round(total_score, 2)}")

    # Actionable feedback
    feedback = []
    if collimation < 8: feedback.append("Improve collimation to reduce unnecessary exposure.")
    if positioning < 8: feedback.append("Check patient positioning for accuracy.")
    if exposure < 8: feedback.append("Adjust exposure settings for optimal image quality.")
    if artifacts < 8: feedback.append("Remove artifacts before imaging.")

    st.write("### Suggested Fixes:")
    for f in feedback:
        st.write(f"- {f}")

    # Save to Excel
    if st.button("Save Result"):
        data = {
            "Body Part": body_part,
            "View": view,
            "Collimation": collimation,
            "Positioning": positioning,
            "Exposure": exposure,
            "Artifacts": artifacts,
            "Total Score": round(total_score, 2)
        }
        df = pd.DataFrame([data])
        file_name = "qa_results.xlsx"
        if os.path.exists(file_name):
            existing = pd.read_excel(file_name)
            df = pd.concat([existing, df], ignore_index=True)
        df.to_excel(file_name, index=False)
        st.success(f"Saved to {file_name}")

# ---------------- RUN APP ----------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login()
import pandas as pd
