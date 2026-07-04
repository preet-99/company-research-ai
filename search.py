import requests
import streamlit as st


def search_company(company_name):
    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": st.secrets["SERPER_API_KEY"]},
        json={"q": f"{company_name} company info"},
    )
    data = response.json()

    organic = data.get("organic", [])
    faqs = data.get("peopleAlsoAsk", [])

    company_info = {
        "website": organic[0]["link"] if organic else "",
        "description": (
            faqs[0]["snippet"] if faqs else organic[0]["snippet"] if organic else ""
        ),
        "snippets": [r["snippet"] for r in organic[:5]],
        "sources": [r["link"] for r in organic[:5]],
    }

    return company_info


def search_competitors(company_name, industry=""):
    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": st.secrets["SERPER_API_KEY"]},
        json={"q": f"{company_name} competitors similar companies"},
    )
    data = response.json()

    organic = data.get("organic", [])

    competitors = []
    for item in organic[:5]:
        competitors.append(
            {"name": item["title"], "website": item["link"], "snippet": item["snippet"]}
        )

    return competitors


info = search_company("www.tesla.com")
print(info)
