import streamlit as st
import pandas as pd
import os
import pydicom
import numpy as np
from PIL import Image
import cv2

# ---------------- LOGIN_input("Password", type="password")# ---------------- LOGIN ----------------
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

# ---------------- AI SCORING ----------------
def ai_score(image_array):
    # Convert to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

    # Collimation: ratio of anatomy coverage (edges detected)
    edges = cv2.Canny(gray, 50, 150)
    coverage = np.sum(edges > 0) / edges.size
    collimation_score = min(10, max(0, 10 - (coverage * 5)))  # heuristic

    # Positioning: symmetry check (fix for shape mismatch)
    h, w = gray.shape
    mid = w // 2
    left = gray[:, :mid]
    right = np.fliplr(gray[:, mid:mid + left.shape[1]])  # match width
    symmetry_diff = np.mean(cv2.absdiff(left, right))
    positioning_score = max(0, 10 - symmetry_diff / 10)

    # Exposure: brightness histogram
    brightness = np.mean(gray)
    exposure_score = 10 - abs(brightness - 128) / 12  # ideal ~128 mid-gray
    exposure_score = max(0, min(10, exposure_score))

    # Artifacts: high variance in small patches
    variance = np.var(gray)
    artifacts_score = max(0, 10 - variance / 5000)

    return round(collimation_score, 2), round(positioning_score, 2), round(exposure_score, 2), round(artifacts_score, 2)

# ---------------- MAIN APP ----------------
def main_app():
    st.title("AI-Powered X-Ray QA Scoring Tool")

    dicom_file = st.file_uploader("Upload Image or DICOM file", type=["dcm", "jpg", "jpeg", "png"])

    if dicom_file:
        if dicom_file.name.lower().endswith(".dcm"):
            body_part, view = detect_body_part(dicom_file)
            st.success(f"Detected Body Part: {body_part}, View: {view}")
            ds = pydicom.dcmread(dicom_file)
            image_array = ds.pixel_array
            image_array = cv2.convertScaleAbs(image_array)
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGR)
        else:
            st.warning("Image uploaded (not DICOM). Please select Body Part and View manually below.")
            body_part = st.selectbox("Body Part", ["Chest", "Abdomen", "Extremity", "Spine"])
            view = st.selectbox("View", ["AP", "PA", "Lateral", "Oblique"])
            image = Image.open(dicom_file).convert("RGB")
            image_array = np.array(image)

        # Show preview
        st.image(image_array, caption="Uploaded Image", use_column_width=True)

        # AI scoring
        collimation, positioning, exposure, artifacts = ai_score(image_array)
        st.subheader("AI-Generated Scores (0-10)")
        st.write(f"Collimation: {collimation}")
        st.write(f"Positioning: {positioning}")
        st.write(f"Exposure: {exposure}")
        st.write(f"Artifacts: {artifacts}")

        # Manual override
        st.subheader("Adjust Scores if Needed")
        collimation = st.number_input("Collimation", 0, 10, value=collimation)
        positioning = st.number_input("Positioning", 0, 10, value=positioning)
        exposure = st.number_input("Exposure", 0, 10, value=exposure)
        artifacts = st.number_input("Artifacts", 0, 10, value=artifacts)

        # Weighted score
        st.sidebar.header("Adjust Scoring Weights")
        weights = {
            "Collimation": st.sidebar.slider("Collimation Weight", 0.0, 1.0, 0.3),
            "Positioning": st.sidebar.slider("Positioning Weight", 0.0, 1.0, 0.3),
            "Exposure": st.sidebar.slider("Exposure Weight", 0.0, 1.0, 0.2),
            "Artifacts": st.sidebar.slider("Artifacts Weight", 0.0, 1.0, 0.2)
        }

        total_score = (collimation * weights["Collimation"] +
                       positioning * weights["Positioning"] +
                       exposure * weights["Exposure"] +
                       artifacts * weights["Artifacts"])
        st.write(f"**Total Weighted Score:** {round(total_score, 2)}")

        # Save results
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

def login():
    st.title("QA App Login")
    username = st.text_input("Username")
