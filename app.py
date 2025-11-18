import streamlit as st
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="EmailFlow AI", layout="centered")

st.markdown("""
    <style>
    .stTextArea textarea {font-size: 14px;}
    .stButton button {width: 100%; border-radius: 5px; background-color: #0073e6; color: white;}
    .highlight {background-color: #ffffcc; padding: 2px 4px; border-radius: 4px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

api_key = os.getenv("GEMINI_API_KEY")

def highlight_text(text):
    """Simple function to highlight key terms in the UI display"""
    keywords = ["attached", "meeting", "update", "request", "note", "reminder", "important"]
    for word in keywords:
        text = re.sub(f"(?i)({word})", r'<span class="highlight">\1</span>', text)
    return text

with st.sidebar:
    st.header("👤 Sender Profile")
    st.caption("Configure your signature details here.")
    
    sender_name = st.text_input("Your Name", value="Your Name")
    sender_role = st.text_input("Your Role", value="Your Position")
    company_name = st.text_input("Company", value="Your Company / Organization")
    company_address = st.text_input("Company Address", value="")
    website_url = st.text_input("Website", value="")
    
    st.divider()

st.title("EmailFlow AI")
st.markdown("##### AI-Powered Email Generator")
st.divider()

col1, col2 = st.columns(2)
with col1:
    recipient_name = st.text_input("Recipient Name", placeholder="e.g. Krishna Murthi")
    recipient_role = st.text_input("Recipient Role (optional)", placeholder="e.g. AI Product Intern")

with col2:
    tone = st.selectbox("Email Tone", ["Professional", "Friendly", "Formal", "Concise"])
    context_type = st.selectbox("Context", ["General Communication", "Meeting Request", "Follow-up", "Proposal", "Other"])

context_notes = st.text_area("📝 Context / Notes (bullet points)", height=100, placeholder="- Key discussion points\n- Action items\n- Meeting availability")

uploaded_file = st.file_uploader("📎 Attach File (optional)", type=['pdf', 'docx', 'png'])

if st.button("Generate Email Draft"):
    if not api_key:
        st.error("⚠️ API Key missing. Please check your .env file.")
    elif not recipient_name or not context_notes:
        st.warning("⚠️ Please provide Recipient Name and Context Notes.")
    else:
        with st.spinner("Drafting professional response..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")
                
                attachment_context = "I have attached the requested document." if uploaded_file else ""

                prompt = f"""
You are an expert email writing assistant.

Your job is to convert the user's bullet points and context into a fully professional,
well-structured email. Follow these rules strictly:

1. Generate a clear and short subject line.
2. Start with an appropriate greeting to the recipient.
3. Write the email in short, clean paragraphs.
4. Keep the tone as specified by the user ({tone.lower()}).
5. Add optional CTA (Call to Action) if required by the context.
6. End with a polite closing and the sender's signature details provided.

Must follow this structure:

Subject: <short subject>

Dear <recipient name>,

<email body in 2–4 paragraphs>

Best regards,
<sender name>
<sender role>
<company name>
<website>

Role: You are {sender_name}, {sender_role} at {company_name}.
Task: Write a {tone.lower()} email to {recipient_name} {f"({recipient_role})" if recipient_role else ""}.

Context Type: {context_type}
Context & Notes:
{context_notes}

Attachment Info: {attachment_context}

Tone Instructions:
- Professional: Use formal language, business terminology, and respectful tone
- Friendly: Use casual language, conversational tone
- Formal: Use highly formal language, traditional business structure
- Concise: Keep it brief, focus on key points only

Instructions:
- Do not use placeholders like [Insert Date] unless necessary.
- Keep the email under 150 words.
- Follow the exact structure provided above.
"""
                
                response = model.generate_content(prompt)
                email_content = response.text
                
                st.success("✅ Draft Ready")
                
                tab1, tab2 = st.tabs(["📄 Preview (Highlighted)", "📋 Raw Text"])
                
                with tab1:
                    formatted_html = highlight_text(email_content).replace("\n", "<br>")
                    st.markdown(f"<div style='background-color:#f9f9f9; padding:15px; border-radius:5px; border:1px solid #ddd;'>{formatted_html}</div>", unsafe_allow_html=True)
                
                with tab2:
                    st.text_area("Copy Content", value=email_content, height=300)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")