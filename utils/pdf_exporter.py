import sys
import os
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _trouver_police() -> tuple:
    """
    Cherche une police TTF Unicode disponible sur la machine.
    Retourne (chemin_regular, chemin_bold, chemin_italic).
    """
    # Polices système Windows — toujours présentes sur Windows 10/11
    win_fonts = r"C:\Windows\Fonts"
    candidats_win = [
        ("arial.ttf",   "arialbd.ttf",  "ariali.ttf"),
        ("calibri.ttf", "calibrib.ttf", "calibrii.ttf"),
        ("tahoma.ttf",  "tahomabd.ttf", "tahoma.ttf"),
        ("verdana.ttf", "verdanab.ttf", "verdanai.ttf"),
    ]
    if os.path.exists(win_fonts):
        for reg, bold, ital in candidats_win:
            chemin_reg = os.path.join(win_fonts, reg)
            if os.path.exists(chemin_reg):
                chemin_bold = os.path.join(win_fonts, bold)
                chemin_ital = os.path.join(win_fonts, ital)
                return (
                    chemin_reg,
                    chemin_bold if os.path.exists(chemin_bold) else chemin_reg,
                    chemin_ital if os.path.exists(chemin_ital) else chemin_reg,
                )

    # Polices système Linux/Mac
    candidats_unix = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"),
    ]
    for reg, bold, ital in candidats_unix:
        if os.path.exists(reg):
            return (
                reg,
                bold if os.path.exists(bold) else reg,
                ital if os.path.exists(ital) else reg,
            )

    # Polices bundlées fpdf2 (versions anciennes)
    try:
        import fpdf as fpdf_module
        fonts_dir = os.path.join(os.path.dirname(fpdf_module.__file__), "fonts")
        for nom in ["DejaVuSansCondensed.ttf", "DejaVuSans.ttf"]:
            chemin = os.path.join(fonts_dir, nom)
            if os.path.exists(chemin):
                return (chemin, chemin, chemin)
        # N'importe quelle TTF disponible
        if os.path.exists(fonts_dir):
            ttfs = sorted(f for f in os.listdir(fonts_dir) if f.endswith(".ttf"))
            if ttfs:
                chemin = os.path.join(fonts_dir, ttfs[0])
                return (chemin, chemin, chemin)
    except Exception:
        pass

    raise RuntimeError(
        "Aucune police TTF trouvee. Sur Windows, verifiez que C:\\Windows\\Fonts\\ existe."
    )


def generer_pdf(resultat) -> bytes:
    """
    Point d'entree principal.
    Prend un PaymentResult et retourne les bytes du PDF en memoire.
    """
    from fpdf import FPDF

    pdf = _creer_pdf()
    _ajouter_page_titre(pdf, resultat)
    pdf.add_page()
    _ajouter_resume(pdf, resultat)
    _ajouter_checklist(pdf, resultat)
    _ajouter_infos_pays(pdf, resultat)
    _ajouter_note_finale(pdf)

    return bytes(pdf.output())


def generer_nom_fichier(resultat) -> str:
    """Genere un nom de fichier unique pour le PDF."""
    op         = resultat.operation
    entreprise = (op.nom_entreprise   or "operation").replace(" ", "_")
    pays       = (op.pays_fournisseur or "inconnu").replace(" ", "_")
    date       = datetime.now().strftime("%Y%m%d_%H%M")
    return f"REasy_{entreprise}_{pays}_{date}.pdf"


def _creer_pdf():
    """Initialise le PDF avec une police Unicode detectee automatiquement."""
    from fpdf import FPDF

    chemin_reg, chemin_bold, chemin_ital = _trouver_police()

    class PDFReasy(FPDF):
        def header(self):
            if self.page_no() == 1:
                return
            self.set_font("F", "B", 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 6, "REasy AI Assistant - Resume de paiement international", align="L")
            self.set_draw_color(46, 117, 182)
            self.line(10, 17, 200, 17)
            self.ln(6)

        def footer(self):
            self.set_y(-15)
            self.set_font("F", "", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 8,
                f"Page {self.page_no()}  |  Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
                align="C"
            )

    pdf = PDFReasy()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(15, 15, 15)
    pdf.add_font("F", "",  chemin_reg,  uni=True)
    pdf.add_font("F", "B", chemin_bold, uni=True)
    pdf.add_font("F", "I", chemin_ital, uni=True)
    return pdf


def _ajouter_page_titre(pdf, resultat):
    """Page de couverture."""
    pdf.add_page()
    pdf.set_fill_color(31, 78, 121)
    pdf.rect(0, 0, 210, 55, "F")

    pdf.set_y(12)
    pdf.set_font("F", "B", 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 11, "REasy AI Assistant", align="C", ln=True)
    pdf.set_font("F", "", 13)
    pdf.cell(0, 9, "Resume de paiement international", align="C", ln=True)
    pdf.set_font("F", "I", 10)
    pdf.set_text_color(180, 210, 240)
    pdf.cell(0, 7, "Document genere automatiquement", align="C", ln=True)
    pdf.ln(14)

    op = resultat.operation
    _boite_titre(pdf, "Informations cles de l'operation")
    donnees = [
        ("Entreprise (acheteur)",  op.nom_entreprise        or "N/A"),
        ("Fournisseur",            op.nom_fournisseur       or "N/A"),
        ("Pays du fournisseur",    op.pays_fournisseur      or "N/A"),
        ("Montant",                f"{op.montant:,.2f} {op.devise}" if op.montant else "N/A"),
        ("Mode de paiement",       op.mode_paiement         or "N/A"),
        ("Type de marchandise",    op.type_marchandise      or "N/A"),
        ("Date de l'operation",    op.date_creation),
    ]
    for i, (label, valeur) in enumerate(donnees):
        _ligne_tableau(pdf, label, valeur, pair=(i % 2 == 0))

    if resultat.mode_degrade:
        pdf.ln(8)
        pdf.set_fill_color(255, 243, 205)
        pdf.set_draw_color(255, 193, 7)
        pdf.set_font("F", "I", 9)
        pdf.set_text_color(133, 100, 4)
        pdf.multi_cell(0, 6,
            "AVERTISSEMENT : Document genere en mode hors-ligne. "
            "Le resume est base sur la mise en forme automatique.",
            border=1, fill=True, align="L"
        )
        pdf.set_text_color(50, 50, 50)


def _ajouter_resume(pdf, resultat):
    """Section resume."""
    _titre_section(pdf, "1. Resume de l'operation")
    if resultat.resume.get("resume_llm"):
        texte = _nettoyer_texte(resultat.resume["resume_llm"])
        pdf.set_font("F", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, texte, align="J")
    else:
        for ligne in resultat.resume.get("resume_base", "").split("\n"):
            ligne = _nettoyer_texte(ligne.strip())
            if not ligne or set(ligne) <= {"=", "-"}:
                pdf.ln(2)
                continue
            if ligne[0].isdigit() and "." in ligne[:3]:
                pdf.set_font("F", "B", 10)
                pdf.set_text_color(46, 117, 182)
                pdf.cell(0, 7, ligne, ln=True)
                pdf.set_text_color(50, 50, 50)
            elif ligne.startswith("•"):
                parts = ligne.lstrip("•").split(":", 1)
                pdf.set_font("F", "B", 10)
                pdf.cell(75, 6, parts[0].strip() + " :")
                pdf.set_font("F", "", 10)
                pdf.cell(0, 6, parts[1].strip() if len(parts) > 1 else "", ln=True)
            else:
                pdf.set_font("F", "", 10)
                pdf.cell(0, 6, ligne, ln=True)
    pdf.ln(5)


def _ajouter_checklist(pdf, resultat):
    """Section checklist."""
    _titre_section(pdf, "2. Documents necessaires")
    obligatoires = [d for d in resultat.documents if d.get("obligatoire")]
    recommandes  = [d for d in resultat.documents if not d.get("obligatoire")]

    _sous_titre(pdf, f"Documents obligatoires ({len(obligatoires)})")
    for doc in obligatoires:
        _item_document(pdf, doc, obligatoire=True)

    if recommandes:
        pdf.ln(3)
        _sous_titre(pdf, f"Documents recommandes ({len(recommandes)})")
        for doc in recommandes:
            _item_document(pdf, doc, obligatoire=False)

    if resultat.enrichissement_checklist:
        pdf.ln(3)
        _sous_titre(pdf, "Precisions de l'assistant IA")
        pdf.set_font("F", "I", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 5, _nettoyer_texte(resultat.enrichissement_checklist[:2000]), align="J")
        pdf.set_text_color(50, 50, 50)
    pdf.ln(5)


def _ajouter_infos_pays(pdf, resultat):
    """Section infos pays."""
    from core.checklist_generator import get_infos_pays
    pays = resultat.checklist.get("pays")
    if not pays:
        return
    infos = get_infos_pays(pays)
    if not infos:
        return

    _titre_section(pdf, f"3. Informations pays fournisseur : {pays}")
    _boite_titre(pdf, "Donnees contextuelles")
    _ligne_tableau(pdf, "Delai de virement estime", infos.get("delai_virement_moyen", "N/A"), pair=False)
    _ligne_tableau(pdf, "Devise habituelle",         infos.get("devise_habituelle",    "N/A"), pair=True)

    remarque = infos.get("remarque", "")
    if remarque:
        pdf.ln(4)
        pdf.set_fill_color(235, 243, 251)
        pdf.set_draw_color(46, 117, 182)
        pdf.set_font("F", "I", 9)
        pdf.set_text_color(31, 78, 121)
        pdf.multi_cell(0, 6, _nettoyer_texte(remarque), border=1, fill=True, align="J")
        pdf.set_text_color(50, 50, 50)


def _ajouter_note_finale(pdf):
    """Note legale finale."""
    pdf.ln(10)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("F", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 5,
        "Ce document a ete genere automatiquement par REasy AI Assistant "
        "a titre informatif et pedagogique. "
        "Il ne constitue pas un conseil juridique ou financier.",
        align="C"
    )


# ============================================================
# Utilitaires de mise en page
# ============================================================

def _titre_section(pdf, texte):
    pdf.set_fill_color(31, 78, 121)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("F", "B", 11)
    pdf.cell(0, 9, f"  {texte}", fill=True, ln=True)
    pdf.set_text_color(50, 50, 50)
    pdf.ln(3)


def _sous_titre(pdf, texte):
    pdf.set_font("F", "B", 10)
    pdf.set_text_color(46, 117, 182)
    pdf.cell(0, 7, texte, ln=True)
    pdf.set_text_color(50, 50, 50)
    pdf.ln(1)


def _boite_titre(pdf, titre):
    pdf.set_fill_color(46, 117, 182)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("F", "B", 10)
    pdf.cell(0, 7, f"  {titre}", fill=True, ln=True)
    pdf.set_text_color(50, 50, 50)


def _ligne_tableau(pdf, label, valeur, pair=False):
    fill = (245, 245, 245) if pair else (255, 255, 255)
    pdf.set_fill_color(*fill)
    pdf.set_draw_color(220, 220, 220)
    pdf.set_font("F", "B", 9)
    pdf.cell(70, 7, f"  {label}", border="LRB", fill=True)
    pdf.set_font("F", "", 9)
    pdf.cell(0, 7, f"  {valeur}", border="RB", fill=True, ln=True)


def _item_document(pdf, doc, obligatoire=True):
    icone   = "[OK]" if obligatoire else "[--]"
    couleur = (0, 128, 0) if obligatoire else (100, 100, 100)
    pdf.set_text_color(*couleur)
    pdf.set_font("F", "B", 10)
    pdf.cell(12, 6, icone)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("F", "B", 10)
    pdf.cell(0, 6, _nettoyer_texte(doc["nom"]), ln=True)
    if doc.get("description"):
        pdf.set_x(27)
        pdf.set_font("F", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 5, _nettoyer_texte(doc["description"]), align="J")
        pdf.set_text_color(50, 50, 50)
    pdf.ln(1)


def _nettoyer_texte(texte):
    """Supprime le markdown et remplace les caracteres Unicode problematiques."""
    if not texte:
        return ""
    texte = re.sub(r'\*\*(.*?)\*\*', r'\1', texte)
    texte = re.sub(r'\*(.*?)\*',     r'\1', texte)
    texte = re.sub(r'#{1,6}\s*',     '',    texte)
    texte = re.sub(r'`{1,3}(.*?)`{1,3}', r'\1', texte, flags=re.DOTALL)
    remplacements = {
        '\u2014': '-',  '\u2013': '-',  '\u2019': "'", '\u2018': "'",
        '\u201c': '"',  '\u201d': '"',  '\u2026': '...', '\u2022': '-',
        '\u00a0': ' ',  '\u00ab': '<<', '\u00bb': '>>',
    }
    for char, rep in remplacements.items():
        texte = texte.replace(char, rep)
    return texte.strip()


# Alias pour compatibilite
_nettoyer_markdown = _nettoyer_texte