import requests
from django.conf import settings
from requests.exceptions import RequestException

# ================== NOVA POSHTA ==================
def get_np_info(ttn: str):
    payload = {
        "apiKey": settings.NP_API_KEY,
        "modelName": "TrackingDocument",
        "calledMethod": "getStatusDocuments",
        "methodProperties": {
            "Documents": [{"DocumentNumber": ttn}]
        }
    }

    try:
        r = requests.post("https://api.novaposhta.ua/v2.0/json/", json=payload)
        r.raise_for_status()
        
        doc = r.json()["data"][0]
        status = doc.get("Status", "")
        price = doc.get("DocumentCost", "")

        # ❗ працюємо тільки з відмовами
        if "Відмова" not in status:
            raise ValueError("Це не відмова. Заявка не обробляється.")

        # ❗ оплачено ТІЛЬКИ якщо платив отримувач
        paid = doc.get("PayerType") == "Recipient"

        return float(price) if price else 0.0, paid
        
    except RequestException as e:
        raise ValueError(f"Помилка запиту до Нової Пошти: {str(e)}")

# ================== NOTION ==================
def find_existing_page(ttn):
    url = f"https://api.notion.com/v1/databases/{settings.DATABASE_ID}/query"

    payload = {
        "filter": {
            "property": "ТТН",
            "rich_text": {"equals": ttn}
        }
    }

    try:
        r = requests.post(url, headers=settings.NOTION_HEADERS, json=payload)
        r.raise_for_status()
        
        results = r.json()["results"]
        return results[0]["id"] if results else None
        
    except RequestException as e:
        raise ValueError(f"Помилка запиту до Notion API: {str(e)}")

def append_text_block(page_id, text):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"

    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": text}
                        }
                    ]
                }
            }
        ]
    }

    try:
        r = requests.patch(url, headers=settings.NOTION_HEADERS, json=payload)
        r.raise_for_status()
    except RequestException as e:
        raise ValueError(f"Помилка додавання блоку: {str(e)}")

def create_notion_page(app_number, ttn, social, price, paid):
    short_ttn = ttn[-4:]
    title = f"Заявка №{app_number}-ТТН №{short_ttn}"
    status_value = "ОПЛАЧЕНО" if paid else "НЕ оплачено"

    data = {
        "parent": {"database_id": settings.DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": title}}]
            },
            "ТТН": {
                "rich_text": [{"text": {"content": ttn}}]
            },
            "Соц мережа": {
                "rich_text": [{"text": {"content": social}}]
            },
            "Ціна": {
                "rich_text": [{"text": {"content": str(price)}}]
            },
            "Оплата": {
                "status": {"name": status_value}
            }
        }
    }

    try:
        r = requests.post(
            "https://api.notion.com/v1/pages",
            headers=settings.NOTION_HEADERS,
            json=data
        )
        r.raise_for_status()
        return r.json()["id"]
    except RequestException as e:
        raise ValueError(f"Помилка створення сторінки: {str(e)}")