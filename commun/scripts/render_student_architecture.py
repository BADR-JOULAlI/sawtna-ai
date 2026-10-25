from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "commun/docs" / "architecture-par-etudiant.png"
W, H = 1800, 1180
BG = "#F4F7FB"
INK = "#17243A"
MUTED = "#53647B"
LINE = "#9BAAC0"
WHITE = "#FFFFFF"

FONT_DIR = Path("C:/Windows/Fonts")
REG = str(FONT_DIR / "segoeui.ttf")
BOLD = str(FONT_DIR / "segoeuib.ttf")
ITALIC = str(FONT_DIR / "segoeuii.ttf")


def font(size, bold=False, italic=False):
    path = BOLD if bold else ITALIC if italic else REG
    return ImageFont.truetype(path, size)


im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)


def text(x, y, value, size=23, color=INK, bold=False, anchor=None):
    d.text((x, y), value, font=font(size, bold), fill=color, anchor=anchor)


def centered(x, y, value, size=23, color=INK, bold=False):
    text(x, y, value, size, color, bold, "mm")


def rounded(box, fill, outline=None, radius=22, width=2):
    d.rounded_rectangle(box, radius, fill=fill, outline=outline, width=width)


def arrow(points, color=LINE, width=5, head=14, dashed=False):
    if dashed:
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            dx, dy = x2 - x1, y2 - y1
            length = (dx * dx + dy * dy) ** 0.5
            if not length:
                continue
            ux, uy = dx / length, dy / length
            step, dash = 0, 16
            while step < length - head:
                end = min(step + dash, length - head)
                d.line((x1 + ux * step, y1 + uy * step, x1 + ux * end, y1 + uy * end), fill=color, width=width)
                step += dash * 1.7
    else:
        d.line(points, fill=color, width=width, joint="curve")
    x1, y1 = points[-2]
    x2, y2 = points[-1]
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    left = (x2 - head * math.cos(angle - .48), y2 - head * math.sin(angle - .48))
    right = (x2 - head * math.cos(angle + .48), y2 - head * math.sin(angle + .48))
    d.polygon([(x2, y2), left, right], fill=color)


# Header
text(72, 48, "SAWTNA AI", 24, "#E4002B", True)
text(72, 85, "Architecture du projet par dossier étudiant", 43, INK, True)
text(72, 145, "5 responsabilités · 3 fournisseurs cloud · contrats partagés · intégration par API", 23, MUTED)

# External actors / sources
rounded((60, 205, 460, 290), WHITE, "#C9D4E2", 18)
text(85, 222, "SOURCES OFFICIELLES", 18, "#5A6B80", True)
text(85, 249, "PDF et pages institutionnelles", 21, INK)
rounded((1310, 205, 1740, 290), WHITE, "#C9D4E2", 18)
text(1335, 222, "CITOYEN", 18, "#5A6B80", True)
text(1335, 249, "Questions · références · quiz", 21, INK)

# Cards and paths
xs = [45, 395, 745, 1095, 1445]
cw, top, bottom = 305, 350, 805
centers = [x + cw // 2 for x in xs]
colors = ["#FF8A24", "#1478B8", "#35A96B", "#0078D4", "#7A45E8"]
light = ["#FFF3E8", "#EAF5FC", "#ECF8F0", "#EAF4FE", "#F3EDFF"]

# Flows behind cards
arrow([(260, 290), (260, 325), (centers[0], 325), (centers[0], top)], colors[0], 5)
arrow([(centers[0] + 153, 530), (xs[1] - 8, 530)], "#425A78", 5)
arrow([(centers[1] + 153, 570), (xs[2] - 8, 570)], colors[2], 5)
# Citizen to web
arrow([(1525, 290), (1525, 325), (centers[3], 325), (centers[3], top)], colors[3], 5)
# Frontend consumes backend: routed underneath the cards
arrow([(centers[3], bottom + 3), (centers[3], 850), (centers[1], 850), (centers[1], bottom + 3)], colors[3], 5)
# Backend sends anonymized events to analytics
arrow([(centers[1] + 20, bottom + 4), (centers[1] + 20, 890), (centers[4] - 20, 890), (centers[4] - 20, bottom + 4)], colors[4], 5)

# Connection captions
rounded((470, 493, 638, 529), BG, None, 12)
centered(554, 511, "JSON · HTTPS", 16, MUTED, True)
rounded((828, 535, 1005, 572), BG, None, 12)
centered(916, 553, "embeddings", 16, MUTED, True)
rounded((646, 828, 850, 865), BG, None, 12)
centered(748, 846, "API citoyenne", 16, colors[3], True)
rounded((885, 870, 1115, 907), BG, None, 12)
centered(1000, 888, "événements agrégés", 16, colors[4], True)

cards = [
    ("ÉTUDIANT 1", "Ayoub Chenguir", "AWS EC2 · IaaS", "Data Engineering", ["Collecte officielle", "Extraction · OCR · nettoyage", "Passages + métadonnées", "Revue puis ingestion"], "partie-1-data-engineering"),
    ("ÉTUDIANT 2", "Soulayman Jdidi", "Azure VM · IaaS", "Backend + PostgreSQL", ["API métier sécurisée", "PostgreSQL + pgvector", "Recherche et citations", "Quiz + orchestration"], "partie-2-backend"),
    ("ÉTUDIANT 3", "Badr Joulali", "Google Cloud Run · PaaS", "NLP + embeddings", ["Prétraitement multilingue", "Embeddings versionnés", "API appelée par backend", "Évaluation · latence"], "partie-3-nlp"),
    ("ÉTUDIANT 4", "Aya Sdour", "Azure Static Web Apps · PaaS", "Frontend citoyen", ["React · assistant · quiz", "Bibliothèque des sources", "Français · arabe · RTL", "Responsive · accessibilité"], "partie-4-frontend"),
    ("ÉTUDIANT 5", "Ijlal Sellak", "Google Compute Engine · IaaS", "Analytics + dashboard", ["KPI définis et calculés", "Événements dédupliqués", "Données minimisées", "Dashboard protégé"], "partie-5-analytics"),
]

for i, (role, owner, cloud, title, bullets, folder) in enumerate(cards):
    x = xs[i]
    rounded((x, top, x + cw, bottom), WHITE, "#D9E1EB", 20)
    d.rounded_rectangle((x, top, x + cw, top + 13), 7, fill=colors[i])
    text(x + 21, top + 31, role, 17, colors[i], True)
    text(x + 21, top + 61, owner, 20, MUTED, True)
    # Cloud label wraps to avoid overrun
    cloud_size = 17 if len(cloud) > 23 else 19
    text(x + 21, top + 96, cloud, cloud_size, INK, True)
    d.line((x + 20, top + 132, x + cw - 20, top + 132), fill="#E5EAF1", width=2)
    text(x + 21, top + 150, title, 21, INK, True)
    for j, bullet in enumerate(bullets):
        yy = top + 195 + j * 42
        d.ellipse((x + 22, yy + 9, x + 32, yy + 19), fill=colors[i])
        text(x + 43, yy, bullet, 17, MUTED)
    # Folder tag
    rounded((x + 16, bottom - 52, x + cw - 16, bottom - 15), light[i], None, 10)
    label = folder
    text(x + 25, bottom - 44, label[:34], 13, colors[i], True)

# GitHub / shared contracts base
rounded((260, 975, 1540, 1062), "#18283F", None, 22)
centered(900, 1004, "GITHUB · CINQ PARTIES · CONTRATS COMMUNS · CI D’INTÉGRATION", 22, WHITE, True)
centered(900, 1038, "Le code des cinq services, leurs README et les ressources communes sont versionnés ensemble.", 18, "#D5E0EF")
for cx in centers:
    arrow([(cx, 974), (cx, 930)], "#73849A", 3, 11, dashed=True)

# Status footer
rounded((60, 1090, 1740, 1150), "#FFF4DF", "#F0D7A4", 16)
centered(900, 1120, "ÉTAT : prototype et intégration vérifiés en local · les comptes et déploiements AWS / Azure / Google restent à configurer", 18, "#77551C", True)

OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT, optimize=True)
print(OUT)
