import streamlit as st
import requests
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="SHADOW MERCHANT", page_icon="💼", layout="wide")

# DARK MODE CSS
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ff4b4b; }
    .stTextInput input { background-color: #1e1e1e; color: white; }
    .stTextArea textarea { background-color: #1e1e1e; color: white; }
    .stButton button { background-color: #ff4b4b; color: white; border: none; }
    </style>
""", unsafe_allow_html=True)

# SIDEBAR KEYS
with st.sidebar:
    st.title("🔑 ARMORY")
    groq_key = st.text_input("GROQ API KEY", type="password")
    tavily_key = st.text_input("TAVILY API KEY", type="password")

# --- 1. THE SCOUT (Tavily Context Search) ---
def get_company_intel(url, t_key):
    # We use Tavily to "search" for the company to get a summary + latest news
    # This is often better than just scraping the homepage which might have no text.
    api_url = "https://api.tavily.com/search"
    payload = {
        "api_key": t_key,
        "query": f"What does {url} do? What is their business model?",
        "search_depth": "advanced", # Deeper search
        "include_answer": True
    }
    try:
        response = requests.post(api_url, json=payload)
        data = response.json()
        # Combine the AI generated answer with search results
        context = f"SUMMARY: {data.get('answer', '')}\n\nDETAILS:\n"
        for result in data.get('results', [])[:3]: # Top 3 results
            context += f"- {result['content']}\n"
        return context
    except Exception as e:
        return f"SCOUT FAILED: {e}"

# --- 2. THE SNIPER (Groq Email Gen) ---
def generate_cold_email(company_url, intel, my_offer, g_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {g_key}"}
    
    # SYSTEM PROMPT: THE SALES GURU
    system_prompt = """
    You are an elite Sales Development Rep (SDR). 
    Your goal is to write a COLD EMAIL that gets a reply.
    RULES:
    1. Keep it under 150 words.
    2. No "I hope this finds you well." Start with a hook about THEIR company.
    3. Connect their business (from the Intel) to MY OFFER.
    4. End with a soft Call to Action (e.g., "Worth a chat?").
    """
    
    user_prompt = f"""
    TARGET COMPANY: {company_url}
    
    INTEL ON TARGET:
    {intel}
    
    MY OFFER (What I am selling):
    {my_offer}
    
    TASK: Write 3 different subject lines and 1 killer email body.
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"SNIPER FAILED: {e}"

# --- MAIN UI ---
st.title("💼 SHADOW MERCHANT: AI SALES DRONE")
st.write("Target a company. Understand them. Pitch them.")

col1, col2 = st.columns(2)

with col1:
    target_url = st.text_input("TARGET URL (e.g., zomato.com)", placeholder="zomato.com")
    my_offer = st.text_area("MY OFFER (What do you sell?)", value="I build AI Agents that automate lead generation and save 20 hours a week.", height=150)

if st.button("GENERATE PITCH"):
    if not groq_key or not tavily_key:
        st.error("⚠️ FILL KEYS IN SIDEBAR")
    else:
        with st.status("🕵️ SHADOW AGENT DEPLOYED...", expanded=True) as status:
            
            st.write("1. Scouting Target...")
            intel = get_company_intel(target_url, tavily_key)
            st.success("Target Analyzed!")
            
            st.write("2. Drafting Strategy...")
            email = generate_cold_email(target_url, intel, my_offer, groq_key)
            st.success("Email Ready!")
            
            status.update(label="MISSION COMPLETE", state="complete")

        st.subheader("📬 GENERATED COLD EMAIL")
        st.code(email, language="markdown")
        
        with st.expander("VIEW GATHERED INTEL"):
            st.write(intel)