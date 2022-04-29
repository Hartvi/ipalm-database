
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
drawing = svg2rlg(r"C:\Users\jhart\PycharmProjects\ipalm-database\tutorial\proj9.svg")
renderPDF.drawToFile(drawing, r"C:\Users\jhart\PycharmProjects\ipalm-database\tutorial\proj9.pdf")
