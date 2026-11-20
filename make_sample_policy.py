# demo ke liye chhoti si policy PDF (pip install reportlab)
from reportlab.pdfgen import canvas
lines = [
 "Meals: any meals expense above Rs 2000 per person requires prior manager approval.",
 "Travel: domestic travel above Rs 9000 needs approval from the department head.",
 "Hotel: hotel stay above Rs 8000 per night requires finance approval.",
 "Cab: cab rides above Rs 1500 need a written justification and approval.",
 "All claims above Rs 500 must have a valid receipt attached.",
]
c = canvas.Canvas("sample_policy.pdf")
y = 800
for l in lines:
    c.drawString(40, y, l); y -= 30
c.save()
