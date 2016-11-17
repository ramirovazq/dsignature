# -*- coding: utf-8 -*-
import xmltodict
import qrcode

def xml2pdf(url):
    with open(url) as fd:
        doc = xmltodict.parse(fd.read())
        emisor = doc["cfdi:Comprobante"]["cfdi:Emisor"]
        receptor = doc["cfdi:Comprobante"]["cfdi:Receptor"]
        nomina = doc["cfdi:Comprobante"]["cfdi:Complemento"]["nomina:Nomina"]
        conceptos = doc["cfdi:Comprobante"]["cfdi:Conceptos"]
        timbrado = doc["cfdi:Comprobante"]["cfdi:Complemento"]["tfd:TimbreFiscalDigital"]
        return pdf(doc, doc["cfdi:Comprobante"]["@total"], emisor, receptor, conceptos, timbrado, nomina)

def pdf(comprobante, total, emisor, receptor, conceptos, timbrado, nomina):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    from reportlab.platypus import Table, TableStyle, Spacer
    from reportlab.lib import colors
    from reportlab.platypus.flowables import Image
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from cStringIO import StringIO
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.graphics.charts.textlabels import Label
    from reportlab.graphics.shapes import Drawing
    from reportlab.lib.colors import Color
    from reportlab.lib.utils import ImageReader


    def AllPageSetup(canvas, doc):

        canvas.saveState()
        logo_marca_agua = ImageReader('http://www.inmegen.gob.mx/tema/photologue/photos/logo_20_transparente.png')
        canvas.drawImage(logo_marca_agua, 130, 250, width=350, height=380, mask='auto')

        logo_header = ImageReader('http://www.inmegen.gob.mx/tema/photologue/photos/inmegen_logo_color01.png')
        canvas.drawImage(logo_header, 30, 717, width=151, height=70, mask='auto')
#        canvas.setFillGray(gray) 
        canvas.restoreState()


    def PrimerPaginaSetup(canvas, doc):

        diferencia = 45            
        extra = 15

        logo_marca_agua = ImageReader('http://www.inmegen.gob.mx/tema/photologue/photos/logo_20_transparente.png')
        canvas.drawImage(logo_marca_agua, 130, 250, width=350, height=380, mask='auto')

        logo_header = ImageReader('http://www.inmegen.gob.mx/tema/photologue/photos/inmegen_logo_color01.png')
        canvas.drawImage(logo_header, 30, 717, width=151, height=70, mask='auto')


        canvas.saveState()
        canvas.drawString(370, 780-diferencia+extra, "Periodo de pago "+nomina["@FechaInicialPago"]+"   "+nomina["@FechaFinalPago"])

        canvas.drawString(30, 750-diferencia, emisor["@nombre"])
        canvas.drawString(30, 735-diferencia, emisor["@rfc"])
        canvas.drawString(445, 756-diferencia+extra, conceptos["cfdi:Concepto"]["@descripcion"])

        canvas.drawString(435, 725-diferencia+extra, 'Total Neto:')
        canvas.drawString(500, 725-diferencia+extra, "${:,.2f}".format(float(total)))
        canvas.line(495, 723-diferencia+extra, 580, 723-diferencia+extra)
             
        canvas.drawString(30, 703-diferencia+extra, 'Nombre del empleado:')
        canvas.drawString(160, 703-diferencia+extra, receptor["@nombre"])
        canvas.line(160, 700-diferencia+extra, 580, 700-diferencia+extra)    

        canvas.drawString(30, 680-diferencia+extra, 'R.F.C:')
        canvas.drawString(160, 680-diferencia+extra, receptor["@rfc"])
        canvas.line(160, 677-diferencia+extra, 270, 677-diferencia+extra)

        canvas.drawString(280, 680-diferencia+extra, 'C.U.R.P:')
        canvas.drawString(330, 680-diferencia+extra, nomina["@CURP"])
        canvas.line(330, 677-diferencia+extra, 580, 677-diferencia+extra)

        canvas.drawString(30, 660-diferencia+extra, "CLABE:")
        canvas.drawString(160, 660-diferencia+extra, nomina.get("@CLABE", "SIN CLABE"))
        canvas.line(160, 657-diferencia+extra, 580, 657-diferencia+extra)

        canvas.drawString(30, 640-diferencia+extra, "Denominación del puesto:")
        canvas.drawString(170, 640-diferencia+extra, nomina["@Puesto"])
        canvas.line(170, 637-diferencia+extra, 580, 637-diferencia+extra)

        canvas.drawString(30, 620-diferencia+extra, "Adscripción:")
        canvas.drawString(160, 620-diferencia+extra, nomina["@Departamento"])
        canvas.line(160, 617-diferencia+extra, 580, 617-diferencia+extra)

        canvas.drawString(30, 600-diferencia+extra, "Folio Fiscal:")
        canvas.drawString(150, 600-diferencia+extra, timbrado["@UUID"])
        canvas.line(150, 597-diferencia+extra, 390, 597-diferencia+extra)

        canvas.drawString(400, 600-diferencia+extra, "Timbrado:")
        canvas.drawString(460, 600-diferencia+extra, timbrado["@FechaTimbrado"])
        canvas.line(455, 597-diferencia+extra, 580, 597-diferencia+extra)

        if False:
            canvas.drawString(30, 580-diferencia+extra, "Tipo de Contrato:")
            canvas.drawString(160, 580-diferencia+extra, nomina["@TipoContrato"])
            canvas.line(160, 577-diferencia+extra, 390, 577-diferencia+extra)

        canvas.drawString(400, 580-diferencia+extra, u"Número de días pagados:")
        canvas.drawString(540, 580-diferencia+extra, 
            "{:,d}".format(int(float(nomina["@NumDiasPagados"]))))
        canvas.line(540, 577-diferencia+extra, 580, 577-diferencia+extra)
       

        canvas.restoreState()


    class InfoCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []
     
        def showPage(self):
            self.basic_data()
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()
            
     
        def basic_data(self):
            canvas = self
            canvas.setLineWidth(.3)
            canvas.setFont('Helvetica', 11)

            diferencia = 45            
            extra = 15

        def save(self):
            """add page info to each page (page x of y)"""
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                #self.draw_page_number(num_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)
 
    buffer_ = StringIO()
    doc = SimpleDocTemplate(buffer_, pagesize=letter)
    elements = [Spacer(0, 6.1*cm)]# esto baja o sube la tabla de percepciones y deducciones

    pg = ParagraphStyle('table_title')
    pg.alignment = TA_CENTER

    percepciones = nomina["nomina:Percepciones"]
    deducciones = nomina["nomina:Deducciones"]
    table = Table([[Paragraph("Percepciones", pg), Paragraph("Deducciones", pg)]], 
        colWidths=275, rowHeights=15)
    table.setStyle(TableStyle([
                           ('INNERGRID', (0,0), (0,0), 0.25, colors.black),
                           ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                     #      ('BACKGROUND',(0,0),(-1,2), colors.white)
                           ]))
    elements.append(table)
    
    p_text = ParagraphStyle('text')
    p_text.alignment = TA_LEFT
    p_text.fontSize = 7
    p_text.borderColor = 'black'
    p_text.borderWidth = 0
    p_text.textColor = 'black'

    p_money = ParagraphStyle('money')
    p_money.alignment = TA_RIGHT
    p_money.fontSize = 7
    p_money.borderColor = 'black'
    p_money.borderWidth = 0
    p_money.textColor = 'black'

    percepciones_data = []
    if not isinstance(percepciones["nomina:Percepcion"], list):
        percepciones["nomina:Percepcion"] = [percepciones["nomina:Percepcion"]]

    print(type(percepciones["nomina:Percepcion"]))
    for p in percepciones["nomina:Percepcion"]:
        percepciones_data.append([
            Paragraph(p["@Clave"]+"  "+p["@Concepto"], p_text),
            Paragraph("${:,.2f}".format(float(p["@ImporteGravado"])), p_money)])

    deducciones_data = []
    if not isinstance(deducciones["nomina:Deduccion"], list):
        deducciones["nomina:Deduccion"] = [deducciones["nomina:Deduccion"]]

    print(deducciones["nomina:Deduccion"])
    for p in deducciones["nomina:Deduccion"]:
        importe_exento = float(p["@ImporteExento"])
        importe_gravado = float(p["@ImporteGravado"])
        importe = importe_gravado if importe_gravado > 0 else importe_exento
        deducciones_data.append([
            Paragraph(p["@Clave"]+"  "+p["@Concepto"], p_text),
            Paragraph("${:,.2f}".format(importe), p_money)])

    if len(percepciones_data) < len(deducciones_data):
        for e in range(len(deducciones_data) - len(percepciones_data)):
            percepciones_data.append([
                Paragraph("", p_text),
                Paragraph("", p_text)])
    elif len(deducciones_data) < len(percepciones_data):
        for e in range(len(deducciones_data) - len(percepciones_data)):
            percepciones_data.append([
                Paragraph("", p_text),
                Paragraph("", p_text)])

    data = []
    total_deducciones_exento = float(deducciones["@TotalExento"])
    total_deducciones_gravado = float(deducciones["@TotalGravado"])
    total_importe_deducciones = total_deducciones_gravado\
        if total_deducciones_gravado > 0 else total_deducciones_exento 
    data.append([
        Paragraph("Total:", p_text),
        Paragraph("<b>${:,.2f}</b>".format(float(percepciones["@TotalGravado"])), p_money), 
        Paragraph("Total:", p_text),
        Paragraph("<b>${:,.2f}</b>".format(total_importe_deducciones), p_money)])

    for row1, row2 in zip(percepciones_data, deducciones_data):
        data.append(row1 + row2)

    table = Table(data, colWidths=(220, 50, 220, 50), rowHeights=15)
    table.setStyle(TableStyle([
                           ('INNERGRID', (0,0), (0,0), 0.5, colors.white),
                       #    ('BOX', (0,0), (-1,-1), 0.5, colors.white),
                        #   ('BACKGROUND',(0,0),(-1,2), colors.white)
                           ]))
    elements.append(Spacer(0, 0.5*cm))
    elements.append(table)
    
    qr_data = "?re={rfc_emisor}&rr={rfc_receptor}&tt={total}&id={folio_fiscal}".format(
        rfc_emisor=emisor["@rfc"],
        rfc_receptor=receptor["@rfc"],
        total=total,
        folio_fiscal=timbrado["@UUID"]
    )

    io = StringIO()
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=1,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    p_text_g = ParagraphStyle('text')
    p_text_g.alignment = TA_LEFT
    p_text_g.fontSize = 10
    p_text_g.borderColor = 'black'
    p_text_g.borderWidth = 0
    p_text_g.textColor = 'black'

    img = qr.make_image()
    img.save(io)

    data = [
        [Paragraph("<b>Sello digital CFDI</b>", p_text_g), Image(io)],
        [Paragraph(timbrado["@selloCFD"], p_text_g)],
        [Paragraph("<b>Sello del SAT</b>", p_text_g)],
        [Paragraph(timbrado["@selloSAT"], p_text_g)]]
    
    table = Table(data, colWidths=(400, 150), rowHeights=(20, 50, 20, 80))
    table.setStyle(TableStyle([
         #                  ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
          #                 ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                           ('SPAN',(1,0),(-1,-1)),
                          # ('BACKGROUND',(0,0),(-1,2), colors.white),
                           ('ALIGN', (1,0), (-1,-1), 'RIGHT')
                           ]))
    elements.append(Spacer(0, .5*cm))
    elements.append(table)
    
    data = [[Paragraph("<b>Metodo de pago</b>", p_text),            
            Paragraph(comprobante["cfdi:Comprobante"]["@metodoDePago"], p_text),
            Paragraph("<b>Condiciones de pago</b>", p_text),
            Paragraph(comprobante["cfdi:Comprobante"]["@formaDePago"], p_text)]]
    table = Table(data)#, colWidths=550, rowHeights=40)

    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        #('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        #('BOX', (0,0), (-1,-1), 0.25, colors.black),
    ]))

    elements.append(Spacer(0, .5*cm))
    elements.append(table)
    #lab = Label()
    #lab.setOrigin(300, 400)
    #lab.boxAnchor = 'ne'
    #lab.angle = 45
    #lab.dx = 0
    #lab.dy = -20
    #lab.fontSize = 60
    #lab.fillColor = Color(red=0, green=0, blue=0, alpha=.5)
    #lab.setText(u'Este recibo está\nen proceso de revisión')
    #d = Drawing(200, 10)
    #d.add(lab)
    #elements.append(d)
    doc.build(elements, canvasmaker=InfoCanvas, onFirstPage=PrimerPaginaSetup, onLaterPages=AllPageSetup)
    pdf = buffer_.getvalue()
    buffer_.close()
    return pdf

if __name__ == "__main__":
    xml2pdf("QNA.xml")
