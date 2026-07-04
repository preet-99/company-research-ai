import requests
import streamlit as st


def search_company(query):
    """
     Search for a company by its name or website URL and return relevant company information.

    Args:
        query (str): Company name or website URL.

    Returns:
        dict: Company information obtained from the search.
    """
    try:
        if (
            query.startswith("http://")
            or query.startswith("https://")
            or query.startswith("www.")
        ):
            search_query = f"company info site:{query}"
        else:
            search_query = f"{query} company info official website"

        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": st.secrets["SERPER_API_KEY"]},
            json={"q": search_query},
        )
        data = response.json()

        organic = data.get("organic", [])
        faqs = data.get("peopleAlsoAsk", [])

        if query.startswith("http") or query.startswith("www."):
            website = query
        else:
            website = organic[0]["link"] if organic else ""

        company_info = {
            "website": website,
            "description": (
                faqs[0]["snippet"] if faqs else organic[0]["snippet"] if organic else ""
            ),
            "snippets": [r["snippet"] for r in organic[:5]],
            "sources": [r["link"] for r in organic[:5]],
        }

        return company_info
    except Exception as e:
        print(e)
        return {"website": query, "description": "", "snippets": [], "sources": []}


def search_competitors(company_name, industry=""):
    """
      Search for competitors of a given company.

    Args:
        company_name (str): Name of the company.
        industry (str): Industry of the company (optional).

    Returns:
        list: A list of competitor companies.
    """
    try:
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
                {
                    "name": item["title"],
                    "website": item["link"],
                    "snippet": item["snippet"],
                }
            )

        return competitors
    except Exception as e:
        print(e)
        return []
