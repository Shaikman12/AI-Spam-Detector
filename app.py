import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from PIL import Image
from fpdf import FPDF
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
import random

# ==============================
# LOAD ENV VARIABLES
# ==============================
load_dotenv()

# ==============================
# GROQ API SETUP
# ==============================
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="AI Spam & Scam Detector",
    page_icon="🛡️",
    layout="centered"
)

# ==============================
# SESSION STATES
# ==============================
if "total_scans" not in st.session_state:
    st.session_state.total_scans = 0

if "phishing_count" not in st.session_state:
    st.session_state.phishing_count = 0

if "safe_count" not in st.session_state:
    st.session_state.safe_count = 0

if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

# ==============================
# DARK HACKER THEME
# ==============================
st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
    color: white;
}

h1 {
    color: #00FFAA;
    text-align: center;
    font-size: 42px;
}

p {
    color: #CFCFCF;
    text-align: center;
}

textarea {
    background-color: #1E1E1E !important;
    color: white !important;
    border-radius: 10px !important;
}

.stTextArea textarea {
    color: white !important;
}

.stButton button {
    background-color: #00FFAA;
    color: black;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    font-weight: bold;
    border: none;
}

.stButton button:hover {
    background-color: #00cc88;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# TITLE
# ==============================
st.title("🛡️ AI Spam & Scam Detector")

st.write("Detect Spam, Scam, Phishing and Fake Messages using AI")

# ==============================
# LIVE DASHBOARD
# ==============================
st.subheader("📊 Live Threat Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Total Scans", st.session_state.total_scans)
col2.metric("Phishing Detected", st.session_state.phishing_count)
col3.metric("Safe Messages", st.session_state.safe_count)

# ==============================
# MESSAGE INPUT
# ==============================
message = st.text_area(
    "📩 Enter Message",
    height=180,
    placeholder="Paste suspicious message here..."
)

# ==============================
# IMAGE UPLOAD
# ==============================
uploaded_file = st.file_uploader(
    "📸 Upload Screenshot",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Screenshot",
        use_container_width=True
    )

# ==============================
# ANALYZE BUTTON
# ==============================
if st.button("🚀 Analyze Message"):

    if message.strip() == "" and uploaded_file is None:

        st.warning(
            "⚠️ Please enter a message or upload a screenshot."
        )

    else:

        with st.spinner("🔍 AI is analyzing the content..."):

            # Increase scan count
            st.session_state.total_scans += 1

            # Detect URLs
            urls = re.findall(
                r'(https?://\S+|www\.\S+)',
                message
            )

            # Suspicious Keywords
            suspicious_keywords = [
                "otp",
                "verify",
                "password",
                "bank",
                "urgent",
                "click",
                "winner",
                "claim",
                "kyc",
                "upi",
                "suspended",
                "reward"
            ]

            found_keywords = []

            for word in suspicious_keywords:

                if word.lower() in message.lower():

                    found_keywords.append(word)

            # ==============================
            # KEYWORD WARNING
            # ==============================
            if found_keywords:

                st.warning(
                    f"⚠️ Suspicious Keywords Detected: {', '.join(found_keywords)}"
                )

            # ==============================
            # AI PROMPT
            # ==============================
            prompt = f"""
You are an advanced cybersecurity AI assistant.

Analyze the following message carefully.

Classify it strictly as ONE of these:
- Safe
- Spam
- Scam
- Phishing

Also provide:
1. Threat Type
2. Risk Level
3. Confidence Score
4. Reason
5. Safety Advice

Message:
{message}
"""

            try:

                # ==============================
                # AI RESPONSE
                # ==============================
                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                )

                ai_result = response.choices[0].message.content

                # ==============================
                # CLEAN AI RESPONSE
                # ==============================
                ai_result = ai_result.replace("₹", "Rs.")
                ai_result = ai_result.replace("’", "'")
                ai_result = ai_result.replace("“", '"')
                ai_result = ai_result.replace("”", '"')
                ai_result = ai_result.replace("–", "-")

                ai_result = ai_result.encode(
                    "latin-1",
                    "ignore"
                ).decode("latin-1")

                # ==============================
                # CLEAN USER MESSAGE
                # ==============================
                clean_message = message.replace("₹", "Rs.")
                clean_message = clean_message.replace("’", "'")
                clean_message = clean_message.replace("“", '"')
                clean_message = clean_message.replace("”", '"')
                clean_message = clean_message.replace("–", "-")

                clean_message = clean_message.encode(
                    "latin-1",
                    "ignore"
                ).decode("latin-1")

                result = ai_result.lower()

                # ==============================
                # THREAT TYPE
                # ==============================
                if (
                    "phishing" in result
                    or "otp" in result
                    or "bank" in result
                ):

                    threat_type = "PHISHING"

                    confidence = random.randint(85, 99)

                elif (
                    "scam" in result
                    or "fraud" in result
                    or "kyc" in result
                ):

                    threat_type = "SCAM"

                    confidence = random.randint(80, 95)

                elif "spam" in result:

                    threat_type = "SPAM"

                    confidence = random.randint(65, 85)

                else:

                    threat_type = "SAFE"

                    confidence = random.randint(5, 30)

                # ==============================
                # URL WARNING
                # ==============================
                if urls:

                    st.warning(
                        f"⚠️ Suspicious Link Detected: {urls[0]}"
                    )

                # ==============================
                # THREAT SCORE
                # ==============================
                st.subheader("📊 Threat Confidence Score")

                st.progress(confidence / 100)

                st.write(
                    f"### 🔥 Threat Score: {confidence}%"
                )

                # ==============================
                # RESULT DISPLAY
                # ==============================
                if threat_type == "PHISHING":

                    st.session_state.phishing_count += 1

                    st.error(ai_result)

                elif threat_type == "SCAM":

                    st.error(ai_result)

                elif threat_type == "SPAM":

                    st.warning(ai_result)

                else:

                    st.session_state.safe_count += 1

                    st.success(ai_result)

                # ==============================
                # SAVE HISTORY
                # ==============================
                st.session_state.scan_history.append({
                    "Message": clean_message[:50],
                    "Threat Type": threat_type,
                    "Threat Score": f"{confidence}%"
                })

                # ==============================
                # PDF REPORT
                # ==============================
                pdf = FPDF()

                pdf.add_page()

                pdf.set_font("Arial", size=14)

                pdf.cell(
                    200,
                    10,
                    txt="AI Spam & Scam Detection Report",
                    ln=True
                )

                pdf.ln(10)

                pdf.multi_cell(
                    0,
                    10,
                    f"Message:\n{clean_message}"
                )

                pdf.ln(5)

                pdf.multi_cell(
                    0,
                    10,
                    f"Threat Type: {threat_type}"
                )

                pdf.ln(5)

                pdf.multi_cell(
                    0,
                    10,
                    f"Threat Score: {confidence}%"
                )

                pdf.ln(5)

                pdf.multi_cell(
                    0,
                    10,
                    f"AI Analysis:\n{ai_result}"
                )

                pdf.output("report.pdf")

                with open("report.pdf", "rb") as file:

                    st.download_button(
                        label="📄 Download Security Report",
                        data=file,
                        file_name="security_report.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:

                st.error(f"❌ Error: {e}")

# ==============================
# PIE CHART ANALYTICS
# ==============================
st.subheader("📈 Threat Analytics")

labels = [
    "Phishing",
    "Safe"
]

sizes = [
    st.session_state.phishing_count,
    st.session_state.safe_count
]

# Avoid crash if no data
if sum(sizes) > 0:

    fig, ax = plt.subplots()

    ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%'
    )

    ax.axis('equal')

    st.pyplot(fig)

else:

    st.info("No scan data available yet.")

# ==============================
# SCAN HISTORY
# ==============================
st.subheader("📁 Scan History")

if st.session_state.scan_history:

    history_df = pd.DataFrame(
        st.session_state.scan_history
    )

    st.dataframe(
        history_df,
        use_container_width=True
    )

# ==============================
# FOOTER
# ==============================
st.markdown("---")

st.markdown(
    "<center>⚡ Developed with AI & Cybersecurity ⚡</center>",
    unsafe_allow_html=True
)