"""
POC - Micro extracción Amazon
Objetivo:
- Validar que Amazon permite extraer datos
- Ver qué campos reales se pueden obtener
- Detectar fallos temprano (bloqueos, selectores, datos faltantes)

NO:
- Base de datos
- Limpieza
- IA
"""

from DrissionPage import ChromiumPage
import time
import sys
import json
from datetime import datetime



# =========================
# 1️⃣ INICIALIZAR NAVEGADOR
# =========================

print("🔹 Iniciando navegador Chromium...")
try:
    page = ChromiumPage()
    print("✅ Navegador iniciado correctamente\n")
except Exception as e:
    print("❌ Error iniciando navegador:", e)
    sys.exit(1)


# =========================
# 2️⃣ ABRIR AMAZON
# =========================

SEARCH_URL = "https://www.amazon.com/s?k=electrodomesticos"

print(f"🔹 Abriendo URL: {SEARCH_URL}")
page.get(SEARCH_URL)

print("⏳ Esperando carga inicial (5 segundos)...")
time.sleep(5)


# =========================
# 3️⃣ SCROLL PARA CARGAR PRODUCTOS
# =========================

print("🔹 Haciendo scroll para cargar resultados...")
page.scroll.down(800)
time.sleep(2)
page.scroll.down(800)
time.sleep(2)
print("✅ Scroll completado\n")


# =========================
# 4️⃣ OBTENER BLOQUES DE PRODUCTOS
# =========================

print("🔹 Buscando productos en la página...")
products = page.eles('css:div[data-component-type="s-search-result"]')

print(f"📦 Productos encontrados: {len(products)}")

if len(products) == 0:
    print("❌ ERROR: No se encontraron productos.")
    print("👉 Posibles causas:")
    print("- Amazon cambió el selector")
    print("- Bloqueo / captcha")
    sys.exit(1)

print("✅ Productos detectados correctamente\n")


# =========================
# 5️⃣ EXTRAER DATOS (POC)
# =========================

productos_data = []  # aquí guardamos todo

print("🔹 Extrayendo datos de los primeros 40 productos...\n")

for idx, product in enumerate(products[:40], start=1):
    print(f"➡️ Producto #{idx}")

    try:
        # ----- TÍTULO -----
        title_el = product.ele('css:h2 span')
        title = title_el.text if title_el else None

        if not title:
            print("⚠️  Título no encontrado")

        # ----- PRECIO -----
        price_whole = product.ele('css:span.a-price-whole')
        price_frac = product.ele('css:span.a-price-fraction')

        price = None
        if price_whole and price_frac:
            price = price_whole.text + "." + price_frac.text
        else:
            print("⚠️  Precio no encontrado")

        # ----- URL DEL PRODUCTO -----
        product_url = None

        links = product.eles('tag:a')
        for a in links:
            href = a.attr('href')
            if not href:
                continue

            if '/dp/' in href:
                if href.startswith('http'):
                    product_url = href.split('?')[0]
                else:
                    product_url = 'https://www.amazon.com' + href.split('?')[0]

                print(f"🔗 URL encontrada: {product_url}")
                break

        if not product_url:
            print("⚠️  No se encontró URL con /dp/")

        # ----- IMAGEN -----
        img_el = product.ele('css:img')
        image_url = img_el.attr('src') if img_el else None

        if not image_url:
            print("⚠️  Imagen no encontrada")

        # ----- GUARDAR RESULTADO -----
        producto_dict = {
                "titulo": title,
                "precio": price,
                "url": product_url,
                "imagen": image_url
            }

        productos_data.append(producto_dict)
        print("✅ Producto extraído correctamente\n")

    except Exception as e:
        print("❌ Error extrayendo producto:", e)
        print("⏭️  Continuando con el siguiente...\n")


# =========================
# 6️⃣ MOSTRAR RESULTADOS FINALES
# =========================

print("\n================ RESULTADOS FINALES ================\n")

for i, p in enumerate(productos_data, start=1):
    print(f"Producto {i}:")
    print("Título      :", p["titulo"])
    print("Precio      :", p["precio"])
    print("URL Producto:", p["url"])
    print("Imagen URL  :", p["imagen"])
    print("-" * 50)


print("\n✅ POC FINALIZADO")
print(f"📊 Total productos válidos: {len(productos_data)}")

# ================= GUARDAR JSON =================
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
json_filename = f"amazon_productos_{timestamp}.json"

with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(productos_data, f, ensure_ascii=False, indent=4)

print(f"\n💾 JSON guardado correctamente: {json_filename}")

# ================= GUARDAR TXT =================
txt_filename = f"amazon_productos_{timestamp}.txt"

with open(txt_filename, "w", encoding="utf-8") as f:
    for i, p in enumerate(productos_data, 1):
        f.write(f"Producto {i}\n")
        f.write(f"Título : {p['titulo']}\n")
        f.write(f"Precio : {p['precio']}\n")
        f.write(f"URL    : {p['url']}\n")
        f.write(f"Imagen : {p['imagen']}\n")
        f.write("-" * 50 + "\n")

print(f"📝 TXT guardado correctamente: {txt_filename}")



# =========================
# 7️⃣ CIERRE MANUAL
# =========================

print("\nℹ️ El navegador queda abierto para inspección manual.")
print("👉 Ciérralo cuando termines.")
