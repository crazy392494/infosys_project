try:
    from fpdf import FPDF
    print("FPDF imported successfully")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt="Hello World", ln=1, align="C")
    out = pdf.output(dest='S')
    print(f"PDF generated with size: {len(out)} bytes")
except ImportError:
    print("FPDF module not found")
except Exception as e:
    print(f"Error: {e}")
