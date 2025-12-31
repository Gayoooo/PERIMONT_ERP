from fpdf import FPDF
from config.settings import *
import os
from datetime import datetime

class PerimontPDF(FPDF):
    def header(self):
        if os.path.exists(COMPANY_LOGO):
            self.image(COMPANY_LOGO, 10, 8, 33)
        self.set_font("helvetica", "B", 9)
        self.set_text_color(100)
        self.set_xy(110, 8)
        info_text = f"{COMPANY_NAME}\n{COMPANY_ADDRESS}\n{COMPANY_CITY}\n{COMPANY_PHONE}"
        self.multi_cell(90, 4, info_text, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150)
        self.cell(0, 10, f"{COMPANY_NAME} - {COMPANY_STATUT} - Page {self.page_no()}", align="C")

# --- MODULE FINANCES (Filtrage Journalier / Mensuel) ---
def generer_journal_caisse_pdf(data_list, periode, titre="JOURNAL DE CAISSE"):
    pdf = PerimontPDF()
    pdf.add_page()
    pdf.set_y(35)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, f"{titre}", ln=True, align="C")
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 7, f"Période : {periode}", ln=True, align="C")
    pdf.ln(5)
    
    headers = ["Date", "Libellé de l'opération", "Type", "Montant"]
    widths = [35, 85, 30, 40]
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(30, 41, 59); pdf.set_text_color(255)
    for i in range(len(headers)): pdf.cell(widths[i], 10, headers[i], 1, 0, 'C', True)
    pdf.ln(); pdf.set_text_color(0); pdf.set_font("helvetica", "", 10)
    
    t_in, t_out = 0, 0
    for row in data_list:
        pdf.cell(widths[0], 8, str(row[0])[:10], 1)
        pdf.cell(widths[1], 8, f" {str(row[1])[:40]}", 1)
        if str(row[2]).upper() == "ENTRÉE":
            pdf.set_text_color(16, 120, 129); t_in += row[3]
        else:
            pdf.set_text_color(200, 0, 0); t_out += row[3]
        pdf.cell(widths[2], 8, str(row[2]), 1, 0, 'C')
        pdf.set_text_color(0)
        pdf.cell(widths[3], 8, f"{row[3]:,.0f}", 1, 1, 'R')

    pdf.ln(10); pdf.set_x(110); pdf.set_font("helvetica", "B", 11)
    pdf.cell(50, 8, "TOTAL ENTRÉES", 1, 0, "L")
    pdf.cell(40, 8, f"{t_in:,.0f}", 1, 1, "R")
    pdf.set_x(110)
    pdf.cell(50, 8, "TOTAL SORTIES", 1, 0, "L")
    pdf.cell(40, 8, f"{t_out:,.0f}", 1, 1, "R")
    pdf.set_x(110); pdf.set_fill_color(235, 235, 235)
    pdf.cell(50, 10, "SOLDE NET", 1, 0, "L", True)
    pdf.cell(40, 10, f"{(t_in - t_out):,.0f} FCFA", 1, 1, "R", True)

    if not os.path.exists("exports"): os.makedirs("exports")
    filename = os.path.join("exports", f"Bilan_{titre.replace(' ', '_')}_{periode}.pdf")
    pdf.output(filename)
    return filename

# --- MODULE LOGISTIQUE ---
def generer_bon_location_pdf(loc_data):
    pdf = PerimontPDF()
    pdf.add_page(); pdf.set_y(40)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "BON DE LOCATION / MISE À DISPOSITION", ln=True, align="C")
    pdf.ln(5); pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, f"Client : {loc_data.get('client', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Date : {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5); pdf.set_font("helvetica", "B", 10); pdf.set_fill_color(240, 240, 240)
    pdf.cell(120, 10, "Désignation Matériel", 1, 0, "L", True)
    pdf.cell(70, 10, "Durée", 1, 1, "C", True)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(120, 10, f" {loc_data.get('materiel', 'Engin')}", 1)
    pdf.cell(70, 10, f"{loc_data.get('duree', 0)} Jours", 1, 1, "C")
    pdf.ln(5); pdf.set_font("helvetica", "B", 12)
    pdf.cell(120, 12, "TOTAL À PAYER :", 0, 0, "R")
    pdf.cell(70, 12, f"{loc_data.get('total', 0):,.0f} FCFA", 1, 1, "C", True)
    pdf.ln(20); pdf.cell(95, 10, "Le Responsable (Signature)", 0, 0, "L"); pdf.cell(95, 10, "Le Client (Signature)", 0, 1, "R")
    
    if not os.path.exists("exports"): os.makedirs("exports")
    path = os.path.join("exports", f"Bon_Loc_{str(loc_data.get('client', 'Client')).replace(' ', '_')}.pdf")
    pdf.output(path)
    return path

# --- MODULE PAIE ---
def generer_bulletin(emp_data, mois, annee, details):
    pdf = PerimontPDF()
    pdf.add_page(); pdf.set_y(40)
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "BULLETIN DE PAIE", ln=True, align="C")
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 7, f"Période : {mois} {annee}", ln=True, align="C")
    pdf.ln(5)
    pdf.set_fill_color(240, 240, 240); pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 8, f" SALARIÉ : {emp_data['nom'].upper()}", 1, 1, "L", True)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(95, 8, f" Matricule : {emp_data['matricule']}", 1, 0)
    pdf.cell(95, 8, f" Contrat : {emp_data['type_contrat']}", 1, 1)
    pdf.ln(5); pdf.set_font("helvetica", "B", 10); pdf.set_fill_color(220, 220, 220)
    pdf.cell(100, 10, "Désignation", 1, 0, "L", True)
    pdf.cell(45, 10, "Gains", 1, 0, "C", True)
    pdf.cell(45, 10, "Retenues", 1, 1, "C", True)
    pdf.set_font("helvetica", "", 10)
    sb = details.get('salaire_base_calcule', 0)
    pdf.cell(100, 8, " Salaire de base", 1); pdf.cell(45, 8, f"{sb:,.0f}", 1, 0, "R"); pdf.cell(45, 8, "", 1, 1)
    if details.get('primes', 0) > 0:
        pdf.cell(100, 8, " Primes et Indemnités", 1); pdf.cell(45, 8, f"{details['primes']:,.0f}", 1, 0, "R"); pdf.cell(45, 8, "", 1, 1)
    if details.get('avances', 0) > 0:
        pdf.cell(100, 8, " Avances sur salaire", 1); pdf.cell(45, 8, "", 1, 0); pdf.cell(45, 8, f"{details['avances']:,.0f}", 1, 1, "R")
    if details.get('retenues', 0) > 0:
        pdf.cell(100, 8, " Autres retenues", 1); pdf.cell(45, 8, "", 1, 0); pdf.cell(45, 8, f"{details['retenues']:,.0f}", 1, 1, "R")
    net = sb + details.get('primes', 0) - (details.get('avances', 0) + details.get('retenues', 0))
    pdf.ln(5); pdf.set_font("helvetica", "B", 12); pdf.set_fill_color(230, 240, 255)
    pdf.cell(100, 12, "NET À PAYER", 1, 0, "R", True)
    pdf.cell(90, 12, f"{max(0, net):,.0f} FCFA", 1, 1, "C", True)
    pdf.ln(15); pdf.set_font("helvetica", "B", 10)
    pdf.cell(95, 10, "Signature Employeur", 0, 0, "C"); pdf.cell(95, 10, "Signature Salarié", 0, 1, "C")
    if not os.path.exists("exports"): os.makedirs("exports")
    path = os.path.join("exports", f"bulletin_{emp_data['matricule']}_{mois}.pdf")
    pdf.output(path)
    return path

def generer_recap_mensuel_pdf(data_list, mois, annee, total_general):
    pdf = PerimontPDF(orientation='L')
    pdf.add_page(); pdf.set_y(35)
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 15, f"RÉCAPITULATIF DE PAIE - {mois.upper()} {annee}", ln=True, align='C')
    pdf.ln(5); pdf.set_font("helvetica", "B", 10); pdf.set_fill_color(40, 40, 40); pdf.set_text_color(255)
    cols = [("Matricule", 35), ("Nom Complet", 85), ("S. Base", 38), ("Primes", 38), ("Retenues", 38), ("NET PAYÉ", 43)]
    for txt, w in cols: pdf.cell(w, 10, txt, 1, 0, 'C', True)
    pdf.ln(); pdf.set_text_color(0); pdf.set_font("helvetica", "", 10)
    for r in data_list:
        pdf.cell(35, 8, str(r['Matricule']), 1); pdf.cell(85, 8, f" {r['Nom']}", 1)
        pdf.cell(38, 8, f"{r['S. Base']:,.0f}", 1, 0, 'R'); pdf.cell(38, 8, f"{r['Primes']:,.0f}", 1, 0, 'R')
        pdf.cell(38, 8, f"{r['Retenues']:,.0f}", 1, 0, 'R'); pdf.cell(43, 8, f"{r['NET']:,.0f}", 1, 1, 'R')
    
    # --- CORRECTION COULEURS TOTAL GÉNÉRAL ---
    pdf.ln(5); pdf.set_font("helvetica", "B", 11)
    pdf.set_fill_color(230, 230, 230); pdf.set_text_color(0)
    pdf.set_x(180)
    pdf.cell(50, 10, "TOTAL GÉNÉRAL :", 1, 0, "R", True)
    pdf.cell(43, 10, f"{total_general:,.0f} FCFA", 1, 1, "R", True)
    
    pdf.set_text_color(0); pdf.ln(10)
    pdf.cell(140, 10, "Visa Direction", 0, 0, "L"); pdf.cell(140, 10, "Visa Comptabilité", 0, 1, "R")
    if not os.path.exists("exports"): os.makedirs("exports")
    path = os.path.join("exports", f"Recap_Paie_{mois}_{annee}.pdf")
    pdf.output(path)
    return path