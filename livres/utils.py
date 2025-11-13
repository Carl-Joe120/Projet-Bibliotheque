import requests
from datetime import datetime
from django.core.files.base import ContentFile
from .models import Livre, Categorie

# ---------------------------
# Fonksyon pou Open Library
# ---------------------------
def trouver_livre_par_motCle(keyword, total=200, per_page=50):
    all_books = []
    for start in range(0, total, per_page):
        url = f"https://openlibrary.org/search.json?q={keyword}&language=fre&limit={per_page}&offset={start}"
        resp = requests.get(url)
        if resp.status_code != 200:
            continue
        data = resp.json().get('docs', [])
        all_books.extend(data)
    return all_books

def get_cover_url_ol(book):
    cover_id = book.get("cover_i")
    if cover_id:
        return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
    edition_key = book.get("cover_edition_key")
    if edition_key:
        return f"https://covers.openlibrary.org/b/olid/{edition_key}-L.jpg"
    return None

def get_isbn_ol(book):
    isbns = book.get("isbn", [])
    if isbns:
        return isbns[0]
    return None

def get_author_ol(book):
    authors = book.get("author_name", [])
    if authors:
        return ', '.join(authors)
    return None

def get_publish_date_ol(book):
    year = book.get("first_publish_year")
    if year:
        try:
            # Mete ane sèlman si pa gen dat konplè
            return datetime.strptime(str(year), "%Y").date()
        except:
            pass
    return None

# ---------------------------
# Google Books API (fallback)
# ---------------------------
GOOGLE_API_KEY = 'YOUR_GOOGLE_BOOKS_API_KEY'  # Mete kle w la

def fetch_from_google_books(title, author=None):
    query = f"{title}"
    if author:
        query += f"+inauthor:{author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    if GOOGLE_API_KEY:
        url += f"&key={GOOGLE_API_KEY}"

    try:
        resp = requests.get(url)
    except:
        return None

    if resp.status_code != 200:
        return None
    items = resp.json().get("items", [])
    if not items:
        return None

    volume = items[0]["volumeInfo"]

    isbn = None
    for iden in volume.get("industryIdentifiers", []):
        if iden["type"] in ["ISBN_13", "ISBN_10"]:
            isbn = iden["identifier"]
            break

    cover = volume.get("imageLinks", {}).get("thumbnail")
    resume = volume.get("description")
    authors = ', '.join(volume.get("authors", [])) if volume.get("authors") else None

    date_pub = None
    date_str = volume.get("publishedDate")
    if date_str:
        try:
            if len(date_str) == 4:
                date_pub = datetime.strptime(date_str, "%Y").date()
            elif len(date_str) == 7:
                date_pub = datetime.strptime(date_str, "%Y-%m").date()
            else:
                date_pub = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            date_pub = None

    lecture_url = volume.get("previewLink")

    return {
        "isbn": isbn,
        "couverture_url": cover,
        "resume": resume,
        "auteur": authors,
        "date_publication": date_pub,
        "lecture_en_ligne": lecture_url
    }

# ---------------------------
# Telechajman Imaj
# ---------------------------
def download_image(url, filename):
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            return ContentFile(resp.content, name=filename)
    except:
        return None
    return None

# ---------------------------
# Sauvegarde nan DB
# ---------------------------
def save_book_to_db(book, categorie_nom="Divers"):
    titre = book.get("title")
    isbn = get_isbn_ol(book)
    auteur = get_author_ol(book)
    couverture_url = get_cover_url_ol(book)
    date_pub = get_publish_date_ol(book)
    resume = book.get("first_sentence", "")
    lecture_url = None
    used_google = False

    if not isbn or not auteur or not couverture_url or not resume:
        gb_data = fetch_from_google_books(titre, auteur)
        if gb_data:
            used_google = True
            isbn = isbn or gb_data.get("isbn")
            auteur = auteur or gb_data.get("auteur")
            couverture_url = couverture_url or gb_data.get("couverture_url")
            resume = resume or gb_data.get("resume")
            date_pub = date_pub or gb_data.get("date_publication")
            lecture_url = gb_data.get("lecture_en_ligne")

    if not isbn or not auteur:
        return None, used_google

    if Livre.objects.filter(isbn=isbn).exists():
        return None, used_google

    categorie, _ = Categorie.objects.get_or_create(nom=categorie_nom)

    livre = Livre.objects.create(
        titre=titre,
        auteur=auteur,
        isbn=isbn,
        resume=resume or "",
        date_publication=date_pub,
        categorie=categorie,
        couverture=couverture_url,
        disponible=True,
        lecture_en_ligne=lecture_url
    )
    print(f"✔ Liv ajoute: {titre} - {isbn}")
    return livre, used_google

# ---------------------------
# Importasyon optimize
# ---------------------------
def importer_livres(keywords=None, total=200):
    if keywords is None:
        keywords = {
            "roman": "Roman",
            "jeunesse": "Jeunesse",
            "philosophie": "Philosophie",
            "science": "Science",
            "informatique": "Informatique",
            "education": "Education",
            "famille": "Famille",
            "dictionnaire": "Dictionnaire",
            "technologie": "Technologie",
            "magazines": "Magazines"
        }

    total_imported = 0
    google_used = 0
    per_keyword = max(1, total // len(keywords))

    for keyword, categorie_nom in keywords.items():
        raw_books = trouver_livre_par_motCle(keyword, total=per_keyword, per_page=50)
        print(f"🔍 {len(raw_books)} livres trouvés pour '{keyword}'")
        for raw in raw_books:
            livre, used_google = save_book_to_db(raw, categorie_nom=categorie_nom)
            if livre:
                total_imported += 1
                if used_google:
                    google_used += 1

    print(f" Total livres importés: {total_imported} (dont {google_used} complétés via Google Books)")
    return total_imported, google_used
