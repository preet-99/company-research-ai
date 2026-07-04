import streamlit as st
import time
from search import search_company, search_contact_details
from crawler import crawl_website, extract_contact_info
from ai_processor import analyze_company
from pdf_generator import generate_pdf

st.set_page_config(
    page_title="AI Company Research Assistant", page_icon="🔍", layout="wide"
)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    model_choice = st.selectbox(
        "🤖 Select AI Model",
        [
            "openrouter/free",
            "meta-llama/llama-3.3-70b:free",
            "mistralai/mistral-7b-instruct:free",
            "deepseek/deepseek-chat:free",
            "google/gemma-3-4b-it:free",
            "poolside/laguna-xs-2.1:free",
        ],
    )
    st.caption("Free models may be slower. If a response looks off, try a different model.")

# CSS — consistent light theme throughout
st.markdown(
    """
<style>
    .main { background-color: #f7f7fb; }

    .stButton>button {
        background-color: #6C63FF;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 15px;
        font-weight: 500;
        border: none;
        width: 100%;
        transition: background-color 0.15s ease;
    }
    .stButton>button:hover {
        background-color: #574fdb;
    }

    .stDownloadButton>button {
        background-color: #6C63FF !important;
        color: white !important;
        border-radius: 10px !important;
        width: auto !important;
        font-weight: 500 !important;
    }

    .result-card {
        background: #ffffff;
        padding: 18px 20px;
        border-radius: 12px;
        border: 1px solid #e6e6f0;
        margin: 8px 0;
        color: #1f1f2e;
    }
    .result-card h4 {
        margin: 0 0 10px 0;
        font-size: 14px;
        color: #6C63FF;
        font-weight: 600;
    }
    .result-card a { color: #6C63FF; }
    .result-card ul { margin: 0; padding-left: 18px; }
    .result-card li { margin-bottom: 4px; }

    .comp-pill {
        display: inline-block;
        background: #f0eefe;
        color: #4b3fd6;
        border: 1px solid #d9d5fb;
        border-radius: 20px;
        padding: 6px 14px;
        margin: 4px 6px 4px 0;
        font-size: 13px;
        text-decoration: none;
    }

    .example-chip button {
        background-color: #f0eefe !important;
        color: #4b3fd6 !important;
        border: 1px solid #d9d5fb !important;
        font-weight: 500 !important;
    }
    .example-chip button:hover {
        background-color: #e2ddfc !important;
    }

    .report-divider {
        border: none;
        border-top: 1px dashed #d9d5fb;
        margin: 18px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Header
st.markdown("## 🔍 AI Company Research Assistant")
st.markdown(
    "Enter a company name or website URL to generate a full AI-powered research report."
)

# Example chips
st.markdown("<div class='example-chip'>", unsafe_allow_html=True)
chip_cols = st.columns([1, 1, 1, 5])
example_pick = None
with chip_cols[0]:
    if st.button("Try Stripe", key="ex_stripe"):
        example_pick = "Stripe"
with chip_cols[1]:
    if st.button("Try Notion", key="ex_notion"):
        example_pick = "Notion"
with chip_cols[2]:
    if st.button("Try Figma", key="ex_figma"):
        example_pick = "Figma"
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# Chat history — each entry is either a plain text turn, or a full report turn
if "messages" not in st.session_state:
    st.session_state.messages = []


def render_report(company_name, search_data, ai_result, pdf_bytes, pdf_filename):
    """Render the full result block for one company. Used both for the live
    run and when redrawing past reports from chat history, so nothing gets
    lost when a new company is researched afterwards."""

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
        <div class='result-card'>
        <h4>🏢 Company Info</h4>
        <b>Website:</b> {search_data.get('website', 'N/A')}<br>
        <b>Phone:</b> {search_data.get('phone', 'N/A')}<br>
        <b>Address:</b> {search_data.get('address', 'N/A')}<br><br>
        <b>Overview:</b><br>{search_data.get('description', 'N/A')}
        </div>
        """,
            unsafe_allow_html=True,
        )

        products = ai_result.get("products", [])
        product_html = "".join([f"<li>{p}</li>" for p in products])
        st.markdown(
            f"""
        <div class='result-card'>
        <h4>📦 Products / Services</h4>
        <ul>{product_html}</ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        pain_html = "".join(
            [f"<li>{p}</li>" for p in ai_result.get("pain_points", [])]
        )
        st.markdown(
            f"""
        <div class='result-card'>
        <h4>⚠️ AI Pain Points</h4>
        <ul>{pain_html}</ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

        comp_pills = "".join(
            [
                f"<a class='comp-pill' href='{c.get('website')}' target='_blank'>{c.get('name')}</a>"
                for c in ai_result.get("competitors", [])
            ]
        )
        st.markdown(
            f"""
        <div class='result-card'>
        <h4>🏆 Competitors</h4>
        {comp_pills if comp_pills else '<span style="color:#888">No competitors found.</span>'}
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
    <div class='result-card'>
    <h4>📝 Company Summary</h4>
    {ai_result.get('summary', 'N/A')}
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Download Report")
    st.download_button(
        label="⬇️ Download PDF Report",
        data=pdf_bytes,
        file_name=pdf_filename,
        mime="application/pdf",
        key=f"pdf_{company_name}_{pdf_filename}",
    )

    with st.expander("View Sources"):
        for source in search_data.get("sources", []):
            st.markdown(f"- [{source}]({source})")


# Replay every past turn so earlier reports stay visible
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("report"):
            r = msg["report"]
            render_report(
                r["company_name"],
                r["search_data"],
                r["ai_result"],
                r["pdf_bytes"],
                r["pdf_filename"],
            )

# Input — either typed in chat, or picked from an example chip
typed_input = st.chat_input(
    "Enter company name or URL (e.g. Stripe or https://stripe.com)"
)
user_input = typed_input or example_pick

if user_input:
    # Add + show the user's message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        progress = st.progress(0)
        status = st.empty()

        try:
            status.markdown("**🔎 Searching for company info...**")
            progress.progress(15)
            search_data = search_company(user_input)
            time.sleep(0.3)

            status.markdown("**🌐 Crawling company website...**")
            progress.progress(35)
            crawl_data = crawl_website(search_data["website"])
            time.sleep(0.3)

            status.markdown("**📇 Extracting contact details...**")
            progress.progress(50)
            contact_info = extract_contact_info(crawl_data)
            if contact_info.get("phone") == "N/A" or contact_info.get("address") == "N/A":
                fallback_contact = search_contact_details(user_input)
                if contact_info.get("phone") == "N/A":
                    contact_info["phone"] = fallback_contact.get("phone", "N/A")
                if contact_info.get("address") == "N/A":
                    contact_info["address"] = fallback_contact.get("address", "N/A")

            search_data["phone"] = contact_info.get("phone", "N/A")
            search_data["address"] = contact_info.get("address", "N/A")
            time.sleep(0.3)

            status.markdown("**🤖 AI analyzing data...**")
            progress.progress(75)
            ai_result = analyze_company(
                user_input, crawl_data, search_data, model_choice
            )
            time.sleep(0.3)

            status.markdown("**📄 Generating PDF report...**")
            progress.progress(92)
            safe_name = user_input.replace(" ", "_").replace("/", "_")
            pdf_filename = f"{safe_name}_report.pdf"
            generate_pdf(user_input, ai_result, search_data, pdf_filename)

            # Read PDF bytes now so we can keep them in memory for history
            # redisplay later — the file on disk isn't a reliable long-term
            # source across reruns.
            with open(pdf_filename, "rb") as f:
                pdf_bytes = f.read()

            progress.progress(100)
            status.empty()
            progress.empty()

            render_report(user_input, search_data, ai_result, pdf_bytes, pdf_filename)

            response_msg = (
                f"Research complete for **{user_input}**! Report generated with "
                f"summary, products, pain points, and "
                f"{len(ai_result.get('competitors', []))} competitors found."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response_msg,
                    "report": {
                        "company_name": user_input,
                        "search_data": search_data,
                        "ai_result": ai_result,
                        "pdf_bytes": pdf_bytes,
                        "pdf_filename": pdf_filename,
                    },
                }
            )

        except Exception as e:
            status.empty()
            progress.empty()
            st.error(f"Error: {str(e)}")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"Error processing request: {str(e)}",
                    "report": None,
                }
            )