from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

def get_product_off(barcode: str):
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        res = requests.get(url, timeout=5)
        data = res.json()
        if data.get("status") != 1:
            return None
        product = data["product"]
        name = product.get("product_name_pt") or product.get("product_name") or ""
        name = name.strip()
        if not name:
            return None
        return name
    except Exception as e:
        print(f"Erro OFF: {e}")
    return None


def get_price_pingo_doce(product_name: str):
    try:
        import json
        query = product_name.replace(" ", "+")
        url = f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-Show?q={query}"
        
        res = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")

        products = soup.select("div.product-tile-pd")
        print(f"📦 Produtos encontrados: {len(products)}")

        for product in products:
            gtm_info = product.get("data-gtm-info")
            if not gtm_info:
                continue

            data = json.loads(gtm_info)
            items = data.get("items", [])
            if not items:
                continue

            item_name = items[0].get("item_name", "").lower()
            search_name = product_name.lower()

            print(f"🔎 A comparar: '{item_name}' com '{search_name}'")

            # Verifica match por palavras
            search_words = search_name.split()
            matched = sum(1 for word in search_words if word in item_name)
            score = matched / len(search_words)

            print(f"📊 Score: {score:.0%}")

            if score >= 0.7:
                price = data.get("value")
                if price:
                    print(f"✅ Match! Preço: {price}€")
                    return float(price)

        print("❌ Nenhum match encontrado")

    except Exception as e:
        print(f"Erro Pingo Doce: {e}")
    return None
    
def get_price_continente(product_name: str):
    try:
        query = requests.utils.quote(product_name)
        url = f"https://www.continente.pt/pesquisa/?q={query}"
        res = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")

        product_link = None
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/produto/" in href or "/products/" in href:
                product_link = href
                print(f"Link Continente encontrado: {href}")
                break

        if not product_link:
            print("Nenhum link Continente encontrado")
            return None

        if not product_link.startswith("http"):
            product_link = f"https://www.continente.pt{product_link}"

        res2 = requests.get(product_link, headers=HEADERS, timeout=8)
        soup2 = BeautifulSoup(res2.text, "html.parser")

        for selector in [
            "span.price", "span.product-price", "div.price",
            "p.price", "span[class*='price']", "div[class*='price']",
            "span[class*='valor']", "div[class*='valor']"
        ]:
            tag = soup2.select_one(selector)
            if tag:
                text = tag.get_text()
                match = re.search(r"\d+[.,]\d{2}", text)
                if match:
                    price = float(match.group().replace(",", "."))
                    print(f"Preço Continente encontrado: {price}€")
                    return price

    except Exception as e:
        print(f"Erro Continente: {e}")
    return None

def get_price_auchan(product_name: str):
    try:
        query = requests.utils.quote(product_name)
        url = f"https://www.auchan.pt/pesquisa?q={query}"
        res = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")

        product_link = None
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/produto/" in href or "/product/" in href:
                product_link = href
                print(f"Link Auchan encontrado: {href}")
                break

        if not product_link:
            return None

        if not product_link.startswith("http"):
            product_link = f"https://www.auchan.pt{product_link}"

        res2 = requests.get(product_link, headers=HEADERS, timeout=8)
        soup2 = BeautifulSoup(res2.text, "html.parser")

        for selector in [
            "span.price", "span.product-price", "div.price",
            "p.price", "span[class*='price']", "div[class*='price']"
        ]:
            tag = soup2.select_one(selector)
            if tag:
                text = tag.get_text()
                match = re.search(r"\d+[.,]\d{2}", text)
                if match:
                    return float(match.group().replace(",", "."))

    except Exception as e:
        print(f"Erro Auchan: {e}")
    return None

def get_price_intermarche(product_name: str):
    try:
        query = requests.utils.quote(product_name)
        url = f"https://www.intermarche.pt/pesquisa?q={query}"
        res = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")

        product_link = None
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/produto/" in href or "/product/" in href:
                product_link = href
                print(f"Link Intermarché encontrado: {href}")
                break

        if not product_link:
            return None

        if not product_link.startswith("http"):
            product_link = f"https://www.intermarche.pt{product_link}"

        res2 = requests.get(product_link, headers=HEADERS, timeout=8)
        soup2 = BeautifulSoup(res2.text, "html.parser")

        for selector in [
            "span.price", "span.product-price", "div.price",
            "p.price", "span[class*='price']", "div[class*='price']"
        ]:
            tag = soup2.select_one(selector)
            if tag:
                text = tag.get_text()
                match = re.search(r"\d+[.,]\d{2}", text)
                if match:
                    return float(match.group().replace(",", "."))

    except Exception as e:
        print(f"Erro Intermarché: {e}")
    return None

def get_price_mercadona(product_name: str):
    try:
        query = requests.utils.quote(product_name)
        url = f"https://tienda.mercadona.es/api/search/?query={query}&lang=pt&wh=mad1"
        res = requests.get(url, headers=HEADERS, timeout=8)
        data = res.json()
        results = data.get("results", [])
        if results:
            price = results[0].get("price_instructions", {}).get("unit_price")
            if price:
                return float(price)
    except Exception as e:
        print(f"Erro Mercadona: {e}")
    return None

@app.route("/product/<barcode>/<supermarket>")
def get_product(barcode: str, supermarket: str):
    supermarket = supermarket.replace("+", " ")

    name = get_product_off(barcode)
    if not name:
        # Devolve 404 em vez de usar o barcode como nome
        return jsonify({"error": "Produto não encontrado"}), 404

    price = None
    if supermarket == "Pingo Doce":
        price = get_price_pingo_doce(name)
    elif supermarket == "Continente":
        price = get_price_continente(name)
    elif supermarket == "Auchan":
        price = get_price_auchan(name)
    elif supermarket == "Intermarché":
        price = get_price_intermarche(name)
    elif supermarket == "Mercadona":
        price = get_price_mercadona(name)

    print(f"Resultado final: {name} | {supermarket} | {price}€")

    return jsonify({
        "barcode": barcode,
        "name": name,
        "price": price,
        "supermarket": supermarket
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)