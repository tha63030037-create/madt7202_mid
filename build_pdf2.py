import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image
OUT, FIG, REPO = sys.argv[1], sys.argv[2], sys.argv[3]
ORANGE, BLUE, INK, RULE = "#E8591A", "#2E3192", "#222222", "#D5D9E6"
FS, LD = 10, 11.3
body = ParagraphStyle("b", fontName="Helvetica", fontSize=FS, leading=LD, textColor=colors.HexColor(INK))
lab = ParagraphStyle("l", parent=body, fontName="Helvetica-Bold")
bul = ParagraphStyle("bl", parent=body, leftIndent=9, bulletIndent=0, spaceAfter=0.8)
para = ParagraphStyle("p", parent=body, spaceAfter=1.2)
title = ParagraphStyle("t", parent=body, fontName="Helvetica-Bold", fontSize=13, leading=15, textColor=colors.HexColor(BLUE))
sub = ParagraphStyle("s", parent=body, textColor=colors.HexColor("#555555"))
idst = ParagraphStyle("id", parent=body, alignment=2, fontName="Helvetica-Bold")
cellb = ParagraphStyle("cb", parent=body, fontName="Helvetica-Bold")
P = lambda t, s=body: Paragraph(t, s)
B = lambda t: Paragraph(t, bul, bulletText="•")
def L(n, t): return P(f'<font color="{ORANGE}"><b>{n}</b></font>&nbsp;&nbsp;<font color="{BLUE}"><b>{t}</b></font>', lab)
def D(t): return Paragraph(t, para)
LW, CW = 3.1 * cm, 14.9 * cm
watch = Table([
 [P("Fund", cellb), P("Link strength", cellb), P("Strongest link", cellb), P("Book held by no other fund", cellb)],
 [P("<b>Tiger Global</b> (hub)"), P("2.54"), P("0.55 (Coatue)"), P("2%")],
 [P("Baupost"), P("0.63"), P("0.09"), P("17%")],
 [P("Akre"), P("0.18"), P("0.06"), P("19%")],
 [P("Icahn"), P("0.00"), P("0.00"), P("66%")]], colWidths=[3.5 * cm, 2.6 * cm, 3.1 * cm, 5.7 * cm])
watch.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor(BLUE)), ("LINEBELOW", (0, 1), (-1, -2), 0.3, colors.HexColor(RULE)), ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FFF1E8")),
  ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 0.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
fig = Image(FIG, width=18 * cm, height=18 * cm * 2.45 / 7.09)
rows = [
 [L(1, "The decision"), [D("Which four US managers' 13F filings our analysts read each quarter. Owner: portfolio manager, Thai equity fund. If all 24 were distinct, we'd just follow the four largest.")]],
 [L(2, "Why a network"), [D("A table ranks funds by size or holdings. The relational question is which funds share a stock neighbourhood and which stand alone \u2014 an overlap only a fund-to-fund graph exposes.")]],
 [L(3, "Data"), [
   D("<b>Source.</b> Secondary source, not scraped: SEC Form 13F-HR tables of 24 well-known managers filing in both quarters, via the data.sec.gov API and EDGAR archive."),
   D("<b>Permission.</b> Public filings; robots.txt allows /Archives/edgar/data (data.sec.gov has none); declared User-Agent, \u22644 requests/s (SEC limit 10); no personal data."),
   D("<b>Period, volume.</b> Quarters ended 31 Mar and 30 Jun 2026: 48 filings, 12,354 rows \u2192 7,972 fund-security records (options, ETFs, duplicates removed); 2,485 issuers in Q2."),
   D("<b>Sampling limits.</b> Long US equity only, up to 45 days late; hand-picked famous managers skew large and concentrated. One source suffices: 13F is the mandatory record.")]],
 [L(4, "Graph construction"), [
   D("<b>Node, edge.</b> Node = fund (24). Edge weight = cosine of portfolio-weight vectors, each issuer weighted by IDF = ln(24 \u00f7 funds holding it); issuer = first 6 CUSIP digits."),
   D("<b>IDF vs raw count.</b> Raw shared-stock count rewards breadth: Bridgewater\u2013Point72 share 522 issuers (rank 1 of 276) only because they hold 983 and 1,854. IDF discounts stocks many funds hold (Alphabet 14 funds): that pair falls to 0.27 (rank 7), Point72\u2013Soros 156 \u2192 0.12 (rank 2 \u2192 24), Coatue\u2013Tiger rises from 18 shared (rank 30) to 0.55 (rank 1)."),
   D("<b>Pruning, size.</b> Cosine \u2265 0.10: 24 nodes, 31 of 276 pairs. No seed entity; ETFs, options out."),
   D("<b>Robustness.</b> Cutoffs 0.05 / 0.10 / 0.15 \u2192 63 / 31 / 17 edges; Coatue\u2013Tiger\u2013Appaloosa cluster holds at all three. Q1\u2192Q2 top pair 0.57\u21920.55; dropping 9 stocks held by 8+ funds: 0.52.")]],
 [[L(5, "The picture"), Spacer(1, 2), fig], ""],
 [L(6, "Findings"), [
   B("<b>Closeness is not shared-stock count.</b> Coatue\u2013Tiger share only 18 issuers yet score 0.55 (rank 1); Bridgewater\u2013Point72 share 522 and score 0.27 (rank 7)."),
   B("<b>Tiger Global anchors one redundant cluster.</b> Strength 2.54 (top of 24); links 0.55 to Coatue, 0.43 to Bridgewater; Appaloosa\u2013Coatue 0.39. Following Coatue, Tiger and Appaloosa buys one signal."),
   B("<b>Three books stand alone.</b> Baupost, Akre, Icahn: no link above 0.09; 17%, 19%, 66% of their books are stocks no other fund owns (Tiger Global 2%).")]],
 [L(7, "Recommended action"), [watch, Spacer(1, 3),
   B("<b>Follow</b> Tiger Global (hub), Baupost, Akre, Icahn; drop Coatue, Appaloosa, Maverick."),
   B("<b>Mon 16 Nov 2026:</b> pull the four Q3 13F filings (deadline; day 45 is Sat 14 Nov), re-run the script. <b>Fri 20 Nov:</b> portfolio manager reviews new positions and hands analysts a shortlist.")]],
 [L(8, "What would change my mind"), [D("Overlap is not performance, and the picks are untested against returns. A back-test over 8 quarters (return of each fund's top-10 new positions from filing date + 45 days) would settle whether following them pays; until then I would commit analysts for Q4 only. If Q3 Coatue\u2013Tiger falls below 0.30, Coatue returns.")]],
]
t = Table(rows, colWidths=[LW, CW])
st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, -1), 0), ("LEFTPADDING", (1, 0), (1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
      ("TOPPADDING", (0, 0), (-1, -1), 3.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6), ("SPAN", (0, 4), (1, 4)), ("LEFTPADDING", (0, 4), (0, 4), 0), ("TOPPADDING", (0, 4), (-1, 4), 3), ("BOTTOMPADDING", (0, 4), (-1, 4), 0)]
for r in range(len(rows)):
    if r != 3 and r != 4: st.append(("LINEBELOW", (0, r), (-1, r), 0.4, colors.HexColor(RULE)))
st.append(("LINEBELOW", (0, 3), (-1, 3), 0.4, colors.HexColor(RULE)))
t.setStyle(TableStyle(st))
hdr = Table([[P("Which four US managers to track? 13F fund network", title), P("6810414003 Thanaree Raksaman", idst)]], colWidths=[12.4 * cm, 5.6 * cm])
hdr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
story = [hdr, Spacer(1, 1), P("MADT 7202 mid-term · 16 Oct 2026 · Code and data: " + REPO, sub), Spacer(1, 3), t]
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm, title="MADT 7202 Mid-Term - 13F fund similarity network", author="Thanaree Raksaman")
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(1.5 * cm, 1.5 * cm, 18 * cm, A4[1] - 3 * cm, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)])])
doc.build(story)
