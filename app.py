import streamlit as st
import time
from search import search_company
from crawler import crawl_website
from ai_processor import analyze_company
from pdf_generator import generate_pdf

# Sidebar 
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    model_choice = st.selectbox(
        "🤖 Select AI Model",
        [
            "openrouter/free",
            "meta-llama/llama-3.3-70b:free",
            "google/gemma-3-4b-it:free",
            "poolside/laguna-xs-2.1:free",
        ],
    )
    st.info("Free models may be slow. openrouter/free is recommended.")

st.set_page_config(
    page_title="AI Company Research Assistant", page_icon="🔍", layout="wide"
)

# CSS
st.markdown(
    """
<style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        background-color: #1a237e;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #283593;
    }
     .result-box {
        background: #1e1e2e;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #7c83fd;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        color: #ffffff !important;
    }
    .result-box b {
        color: #a5b4fc !important;
    }
    .result-box a {
        color: #7c83fd !important;
    }
    .result-box ul li {
        color: #ffffff !important;
    }
    .stButton>button {
        background-color: #7c83fd;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        border: none;
        width: 100%;
    }
    .stDownloadButton>button {
        background-color: #7c83fd !important;
        color: white !important;
        border-radius: 8px !important;
        width: auto !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Header
st.markdown("## AI Company Research Assistant")
st.markdown(
    "Enter a company name or website URL to generate a full AI-powered research report."
)
st.divider()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_search" not in st.session_state:
    st.session_state.last_search = None
if "last_company" not in st.session_state:
    st.session_state.last_company = None

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input(
    "Enter company name or URL (e.g. Stripe or https://stripe.com)"
)

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        # Progress
        progress = st.progress(0)
        status = st.empty()

        try:
            # Step 1: Search
            status.markdown("**Searching for company info...**")
            progress.progress(20)
            search_data = search_company(user_input)
            time.sleep(0.5)

            # Step 2: Crawl
            status.markdown("**Crawling company website...**")
            progress.progress(40)
            crawl_data = crawl_website(search_data["website"])
            time.sleep(0.5)

            # Step 3: AI
            status.markdown("**AI analyzing data...**")
            progress.progress(65)
            ai_result = analyze_company(
                user_input, crawl_data, search_data, model_choice
            )
            time.sleep(0.5)

            # Step 4: PDF
            status.markdown("**Generating PDF report...**")
            progress.progress(85)
            safe_name = user_input.replace(" ", "_").replace("/", "_")
            pdf_path = f"{safe_name}_report.pdf"
            generate_pdf(user_input, ai_result, search_data, pdf_path)
            progress.progress(100)
            status.empty()
            progress.empty()

            # Save results
            st.session_state.last_result = ai_result
            st.session_state.last_search = search_data
            st.session_state.last_company = user_input

            # Show results
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Company Info")
                st.markdown(
                    f"""
                <div class='result-box'>
                <b>Website:</b> {search_data.get('website', 'N/A')}<br><br>
                <b>Overview:</b><br>{search_data.get('description', 'N/A')}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown("### Products / Services")
                products = ai_result.get("products", [])
                product_html = "".join([f"<li>{p}</li>" for p in products])
                st.markdown(
                    f"""
                <div class='result-box'>
                <ul style='margin:0;padding-left:20px'>{product_html}</ul>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown("### AI Pain Points")
                pain_html = "".join(
                    [
                        f"<li style='margin-bottom:6px'>{p}</li>"
                        for p in ai_result.get("pain_points", [])
                    ]
                )
                st.markdown(
                    f"""
                <div class='result-box'>
                <ul style='margin:0;padding-left:20px'>{pain_html}</ul>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown("### Competitors")
                for comp in ai_result.get("competitors", []):
                    # Guard against malformed AI output (e.g. plain strings
                    # instead of {"name":..., "website":...} dicts)
                    if isinstance(comp, dict):
                        comp_name = comp.get("name", "Unknown")
                        comp_site = comp.get("website", "N/A")
                    else:
                        comp_name = str(comp)
                        comp_site = "N/A"

                    st.markdown(
                        f"""
                    <div class='result-box' style='padding:10px 16px;margin:6px 0'>
                    <b>{comp_name}</b><br>
                    <a href='{comp_site}' target='_blank'>{comp_site}</a>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

            # Summary
            st.markdown("### Company Summary")
            st.markdown(
                f"""
            <div class='result-box'>
            {ai_result.get('summary', 'N/A')}
            </div>
            """,
                unsafe_allow_html=True,
            )

            # PDF Download
            st.markdown("### Download Report")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download PDF Report",
                    data=f,
                    file_name=pdf_path,
                    mime="application/pdf",
                )

            with st.expander("View Sources"):
                for source in search_data.get("sources", []):
                    st.markdown(f"- [{source}]({source})")

            # Assistant message
            response_msg = f"Research complete for **{user_input}**! Report generated with summary, products, pain points, and {len(ai_result.get('competitors', []))} competitors found."
            st.session_state.messages.append(
                {"role": "assistant", "content": response_msg}
            )

        except Exception as e:
            status.empty()
            progress.empty()
            st.error(f"Error: {str(e)}")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"Error processing request: {str(e)}",
                }
            )