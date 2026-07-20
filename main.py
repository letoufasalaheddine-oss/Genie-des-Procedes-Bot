import os
import requests
from bs4 import BeautifulSoup

URL = "https://faculty.univ-eloued.dz/faculty/ft/category/2"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LAST_POST_FILE = "last_post.txt"

# الكلمات المفتاحية الخاصة بقسم هندسة الطرائق والبتروكيمياء
KEYWORDS = [
    "قسم هندسة الطرائق والبتروكيمياء",
    "قسم هندسة الطرائق و البتروكيمياء",
    "هندسة الطرائق والبتروكيمياء",
    "هندسة الطرائق و البتروكيمياء",
    "قسم هندسة الطرائق",
    "هندسة الطرائق",
    "الطرائق",
    "قسم البتروكيمياء",
    "البتروكيمياء",
    "بتروكيمياء",
    "Génie des Procédés",
    "Genie des Procédés",
    "Genie des Procedes",
    "Process Engineering",
    "GP",
    "Pétrochimie",
    "Petrochimie",
    "Petrochemistry",
]

# الكلمات الدالة على أن المنشور عام ويخص جميع الطلبة
GENERAL_WORDS = [
    "طلبة كلية التكنولوجيا",
    "جميع الطلبة",
    "لفائدة جميع الطلبة",
    "لفائدة طلبة الكلية",
    "طلبة الكلية",
    "إعادة الإدماج",
    "جميع الأقسام",
    "إعلان هام",
    "إعلان مستعجل",
    "تنويه",
    "بلاغ",
    "إعلان إداري",
    "إدارة الكلية",
    "العمادة",
    "نيابة العمادة",
    "الأمانة العامة",
    "رزنامة",
    "امتحانات",
    "التسجيلات",
    "إعادة التسجيل",
    "التحويلات",
    "العطل",
    "العطل الأكاديمية",
    "المنح",
    "النقل الجامعي",
    "الإيواء",
    "التربصات",
    "مذكرة التخرج",
    "التبرئة النهائية",
]


def load_last_post():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def save_last_post(link):
    with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
        f.write(link)


def send_telegram(title, link):
    message = f"""📢 إعلان جديد

📝 {title}

🔗 {link}
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=30,
    )

    response.raise_for_status()


def is_valid_post(text):
    text = text.lower()

    for word in KEYWORDS:
        if word.lower() in text:
            return True

    for word in GENERAL_WORDS:
        if word.lower() in text:
            return True

    return False

def get_latest_post():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        )
    }

    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # البحث عن جميع المقالات
    articles = soup.find_all("article")

    if not articles:
        print("لم يتم العثور على أي إعلانات.")
        return None, None

    # المرور على الإعلانات من الأحدث إلى الأقدم
    for article in articles:

        # البحث عن عنوان الإعلان
        h2 = article.find(["h2", "h3"])

        if not h2:
            continue

        a = h2.find("a", href=True)

        if not a:
            continue

        title = a.get_text(strip=True)

        if not title:
            continue

        link = a["href"].strip()

        if not link.startswith("http"):
            link = "https://faculty.univ-eloued.dz" + link

        # النص الكامل للإعلان
        article_text = article.get_text(" ", strip=True)

        # نشر إعلانات القسم أو الإعلانات العامة
        if is_valid_post(title) or is_valid_post(article_text):
            return title, link

    return None, None


def main():
    try:
        title, link = get_latest_post()

        if not title or not link:
            print("لا يوجد إعلان جديد يخص قسم هندسة الطرائق والبتروكيمياء.")
            return

        last_post = load_last_post()

        if link == last_post:
            print("تم نشر هذا الإعلان سابقًا.")
            return

        print(f"إعلان جديد: {title}")

        send_telegram(title, link)

        save_last_post(link)

        print("تم إرسال الإعلان إلى تيليجرام بنجاح.")

    except Exception as e:
        print(f"حدث خطأ: {e}")


if __name__ == "__main__":
    main()
