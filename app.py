import streamlit as st
from PIL import Image
import io
import base64
from datetime import datetime
import uuid

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor

# Arabic shaping imports
import arabic_reshaper
from bidi.algorithm import get_display

# Font registration for Arabic
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

##############################################
# 1) REGISTER AN ARABIC-FRIENDLY TTF FONT    #
##############################################
# Make sure "Amiri-Regular.ttf" is in a "fonts" folder
pdfmetrics.registerFont(TTFont("Amiri", "fonts/Amiri-Regular.ttf"))

###########################
# 2) LANGUAGE DICTIONARIES
###########################
LANGUAGES = {
    "en": {
        "document_type_label": "Document Type",
        "invoice": "Invoice",
        "quote": "Quote",
        "number": "Number",
        "date": "Date",
        "due_date": "Due Date",
        "from": "From",
        "to": "To",
        "tax_id": "Tax ID",
        "mobile": "Mobile",
        "email": "Email",
        "details": "Details",
        "description": "Description",
        "quantity": "Quantity",
        "unit_price": "Unit Price",
        "vat_rate": "VAT (%)",
        "vat_amount": "VAT Amount",
        "total": "Total",
        "subtotal": "Subtotal",
        "total_vat": "Total VAT",
        "payment_terms": "Payment Terms",
        "delivery_terms": "Delivery Terms",
        "accept_checks": "Accept Checks?",
        "services_products": "Services / Products",
        "add": "Add",
        "remove": "Remove",
        "download": "Download",
        "supplier_info": "Supplier Information (From)",
        "customer_info": "Customer Information (To)",
        "document_info": "Document Information",
        "additional_info": "Additional Information"
    },
    "fr": {
        "document_type_label": "Type de Document",
        "invoice": "Facture",
        "quote": "Devis",
        "number": "Numéro",
        "date": "Date",
        "due_date": "Date d’échéance",
        "from": "De",
        "to": "A",
        "tax_id": "Identifiant Fiscal",
        "mobile": "Mobile",
        "email": "Email",
        "details": "Détails",
        "description": "Description",
        "quantity": "Quantité",
        "unit_price": "Prix Unitaire",
        "vat_rate": "TVA (%)",
        "vat_amount": "Montant TVA",
        "total": "Total",
        "subtotal": "Sous Total",
        "total_vat": "TVA",
        "payment_terms": "Conditions de Paiement",
        "delivery_terms": "Conditions de Livraison",
        "accept_checks": "Accepter les chèques ?",
        "services_products": "Services / Produits",
        "add": "Ajouter",
        "remove": "Supprimer",
        "download": "Télécharger",
        "supplier_info": "Informations Fournisseur (De)",
        "customer_info": "Informations Client (A)",
        "document_info": "Informations du Document",
        "additional_info": "Informations Supplémentaires"
    },
    "ar": {
        "document_type_label": "نوع المستند",
        "invoice": "فاتورة",
        "quote": "عرض سعر",
        "number": "الرقم",
        "date": "التاريخ",
        "due_date": "تاريخ الاستحقاق",
        "from": "من",
        "to": "إلى",
        "tax_id": "الرقم الضريبي",
        "mobile": "رقم الجوال",
        "email": "البريد الإلكتروني",
        "details": "التفاصيل",
        "description": "الوصف",
        "quantity": "الكمية",
        "unit_price": "سعر الوحدة",
        "vat_rate": "نسبة الضريبة",
        "vat_amount": "مبلغ الضريبة",
        "total": "الإجمالي",
        "subtotal": "الإجمالي الفرعي",
        "total_vat": "مجموع الضريبة",
        "payment_terms": "شروط الدفع",
        "delivery_terms": "شروط التسليم",
        "accept_checks": "قبول الشيكات؟",
        "services_products": "الخدمات / المنتجات",
        "add": "إضافة",
        "remove": "إزالة",
        "download": "تحميل",
        "supplier_info": "معلومات المورد (من)",
        "customer_info": "معلومات العميل (إلى)",
        "document_info": "معلومات المستند",
        "additional_info": "معلومات إضافية"
    }
}

# Map each language to the possible doc-type labels
DOC_TYPE_OPTIONS = {
    "en": [LANGUAGES["en"]["invoice"], LANGUAGES["en"]["quote"]],
    "fr": [LANGUAGES["fr"]["invoice"], LANGUAGES["fr"]["quote"]],
    "ar": [LANGUAGES["ar"]["invoice"], LANGUAGES["ar"]["quote"]]
}

###################################################
# 3) ARABIC SHAPING / RTL HELPER FOR ARABIC TEXT  #
###################################################
def reshape_if_arabic(text, lang):
    """
    If the language is Arabic, we reshape & reorder text (RTL).
    Otherwise, return text as-is.
    """
    if lang == "ar" and text.strip():
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    else:
        return text

###############################
# 4) PDF GENERATION FUNCTION  #
###############################
def create_modern_invoice_pdf(data, items, lang_dict, primary_color, lang_choice):
    """
    Generates a PDF (invoice or quote) in memory and returns the BytesIO object.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=15*mm,
                            leftMargin=15*mm,
                            topMargin=15*mm,
                            bottomMargin=15*mm)
    
    story = []
    styles = getSampleStyleSheet()
    
    # If Arabic, we use the "Amiri" font
    # Otherwise, default "Helvetica"
    font_name = "Amiri" if lang_choice == "ar" else "Helvetica"

    # Custom Title style
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontName=font_name,
        fontSize=24,
        textColor=HexColor(primary_color),
        spaceAfter=30
    ))
    
    # SubHeading style
    styles.add(ParagraphStyle(
        name='SubHeading',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=14,
        textColor=HexColor(primary_color),
        spaceAfter=10
    ))

    # Normal style
    styles.add(ParagraphStyle(
        name='NormalArabic',
        parent=styles['Normal'],
        fontName=font_name
    ))
    
    # Reshape doc title if Arabic
    doc_title = reshape_if_arabic(data["doc_type"], lang_choice)
    number_label = reshape_if_arabic(lang_dict["number"], lang_choice)
    date_label = reshape_if_arabic(lang_dict["date"], lang_choice)
    due_date_label = reshape_if_arabic(lang_dict["due_date"], lang_choice)

    # Combine date + time
    date_str = data['invoice_date'].strftime("%d/%m/%Y") if data['invoice_date'] else ""
    date_time_str = f"{date_str} {datetime.now().strftime('%H:%M')}"

    due_date_str = data['invoice_due_date'].strftime("%d/%m/%Y") if data['invoice_due_date'] else ""
    
    # Logo if any
    if data['logo']:
        logo = RLImage(data['logo'])
        logo.drawHeight = 1*inch
        logo.drawWidth = 1*inch
    else:
        logo = Paragraph("", styles['NormalArabic'])
    
    # Header
    header_html = f"""
    <font color="{primary_color}" size="18"><b>{doc_title.upper()}</b></font><br/>
    <font color="#666666">
    {number_label}: {reshape_if_arabic(data['invoice_number'], lang_choice)}<br/>
    {date_label}: {reshape_if_arabic(date_time_str, lang_choice)}<br/>
    {due_date_label}: {reshape_if_arabic(due_date_str, lang_choice)}
    </font>
    """
    
    header_data = [[logo, Paragraph(header_html, styles['NormalArabic'])]]
    header_table = Table(header_data, colWidths=[doc.width/2.0]*2)
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 20))

    # Supplier / Customer block
    from_label = reshape_if_arabic(lang_dict["from"], lang_choice)
    to_label = reshape_if_arabic(lang_dict["to"], lang_choice)
    tax_id_label = reshape_if_arabic(lang_dict["tax_id"], lang_choice)
    mobile_label = reshape_if_arabic(lang_dict["mobile"], lang_choice)
    email_label = reshape_if_arabic(lang_dict["email"], lang_choice)

    supplier_html = f"""
    <font color="{primary_color}"><b>{from_label}:</b></font><br/>
    {reshape_if_arabic(data['supplier_name'], lang_choice)}<br/>
    {reshape_if_arabic(data['supplier_address'], lang_choice)}<br/>
    {tax_id_label}: {reshape_if_arabic(data['supplier_tax_id'], lang_choice)}<br/>
    {mobile_label}: {reshape_if_arabic(data['supplier_mobile'], lang_choice)}<br/>
    {email_label}: {reshape_if_arabic(data['supplier_email'], lang_choice)}
    """

    customer_html = f"""
    <font color="{primary_color}"><b>{to_label}:</b></font><br/>
    {reshape_if_arabic(data['customer_name'], lang_choice)}<br/>
    {reshape_if_arabic(data['customer_address'], lang_choice)}
    """

    details_data = [
        [
            Paragraph(supplier_html, styles['NormalArabic']),
            Paragraph(customer_html, styles['NormalArabic'])
        ]
    ]
    
    details_table = Table(details_data, colWidths=[doc.width/2.0]*2)
    details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 20))

    # "Details" subheading
    details_label = reshape_if_arabic(lang_dict["details"], lang_choice)
    story.append(Paragraph(details_label, styles['SubHeading']))

    # Table header row
    hdr_description = reshape_if_arabic(lang_dict["description"], lang_choice)
    hdr_quantity = reshape_if_arabic(lang_dict["quantity"], lang_choice)
    hdr_unit_price = reshape_if_arabic(lang_dict["unit_price"], lang_choice)
    hdr_vat_rate = reshape_if_arabic(lang_dict["vat_rate"], lang_choice)
    hdr_vat_amount = reshape_if_arabic(lang_dict["vat_amount"], lang_choice)
    hdr_total = reshape_if_arabic(lang_dict["total"], lang_choice)

    items_data = [[
        hdr_description, hdr_quantity, hdr_unit_price, hdr_vat_rate, hdr_vat_amount, hdr_total
    ]]

    # Calculate totals
    total_without_vat = 0.0
    total_vat = 0.0

    for item in items:
        # Reshape each piece if Arabic
        desc = reshape_if_arabic(item['description'], lang_choice)
        
        subtotal = item['quantity'] * item['unit_price']
        vat_amount = subtotal * (item['vat_rate'] / 100)
        line_total = subtotal + vat_amount

        total_without_vat += subtotal
        total_vat += vat_amount

        row_data = [
            desc,
            str(item['quantity']),
            f"{item['unit_price']:.2f}",
            f"{item['vat_rate']}%",
            f"{vat_amount:.2f}",
            f"{line_total:.2f}"
        ]
        # If Arabic, we might reshape each piece for consistency, but numeric data is typically unaffected.
        # However, you might want to reshape percentages or something else if needed.
        items_data.append(row_data)

    grand_total = total_without_vat + total_vat
    # Subtotal, total VAT, grand total rows
    lbl_subtotal = reshape_if_arabic(lang_dict["subtotal"], lang_choice)
    lbl_total_vat = reshape_if_arabic(lang_dict["total_vat"], lang_choice)
    lbl_total = reshape_if_arabic(lang_dict["total"], lang_choice)

    items_data.extend([
        ['', '', '', '', lbl_subtotal + ":", f"{total_without_vat:.2f}"],
        ['', '', '', '', lbl_total_vat + ":", f"{total_vat:.2f}"],
        ['', '', '', '', lbl_total + ":", f"{grand_total:.2f}"]
    ])

    items_table = Table(items_data, repeatRows=1)
    items_table.setStyle(TableStyle([
        # Header style
        ('BACKGROUND', (0, 0), (-1, 0), HexColor(primary_color)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Grid lines
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -2), 0.5, HexColor('#CCCCCC')),

        # Totals lines
        ('FONTNAME', (-2, -3), (-1, -1), font_name),
        ('LINEABOVE', (-2, -3), (-1, -3), 1, HexColor(primary_color)),
    ]))
    story.append(items_table)

    # Payment Terms
    if data['payment_terms']:
        story.append(Spacer(1, 20))
        label_pt = reshape_if_arabic(lang_dict["payment_terms"], lang_choice)
        story.append(Paragraph(f"<b>{label_pt}</b>:", styles['SubHeading']))
        shaped_pt = reshape_if_arabic(data['payment_terms'], lang_choice)
        story.append(Paragraph(shaped_pt, styles['NormalArabic']))

    # Delivery Terms
    if data['delivery_terms']:
        story.append(Spacer(1, 10))
        label_dt = reshape_if_arabic(lang_dict["delivery_terms"], lang_choice)
        story.append(Paragraph(f"<b>{label_dt}</b>:", styles['SubHeading']))
        shaped_dt = reshape_if_arabic(data['delivery_terms'], lang_choice)
        story.append(Paragraph(shaped_dt, styles['NormalArabic']))

    # Accept checks
    if data['accept_checks']:
        story.append(Spacer(1, 10))
        label_ac = reshape_if_arabic(lang_dict["accept_checks"], lang_choice)
        story.append(Paragraph(f"<b>{label_ac}</b> {reshape_if_arabic('Yes', lang_choice)}", styles['NormalArabic']))
    
    # Build
    doc.build(story)
    buffer.seek(0)
    return buffer

################################
# 5) PDF DISPLAY (IFRAME) HELPER
################################
def get_pdf_iframe(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    return pdf_display

################################
# 6) STREAMLIT APP ENTRY POINT
################################
def main():
    st.set_page_config(layout="wide")
    
    # 6.1 Language
    lang_choice = st.selectbox("Select Language / Choisir la langue / اختر اللغة", ["en", "fr", "ar"])
    lang_dict = LANGUAGES[lang_choice]
    
    # 6.2 Color
    primary_color = st.color_picker("Pick a primary color", "#1a237e")
    
    # 6.3 Document type (Invoice / Quote, Facture / Devis, etc.)
    doc_type = st.selectbox(lang_dict["document_type_label"], DOC_TYPE_OPTIONS[lang_choice])
    
    # Supplier defaults
    default_supplier_name = "Neuratech Solutions"
    default_supplier_address = "30 rue 6667"
    default_supplier_tax_id = "122344"
    default_supplier_mobile = ""
    default_supplier_email = ""

    # Layout: left for form, right for PDF
    col_form, col_pdf = st.columns([1, 1])
    
    with col_form:
        st.title(doc_type)

        # Supplier Info
        st.subheader(lang_dict["supplier_info"])
        supplier_name = st.text_input(lang_dict["from"], value=default_supplier_name)
        supplier_address = st.text_area(lang_dict["from"] + " - Adresse", value=default_supplier_address)
        supplier_tax_id = st.text_input(lang_dict["tax_id"], value=default_supplier_tax_id)
        supplier_mobile = st.text_input(lang_dict["mobile"], value=default_supplier_mobile)
        supplier_email = st.text_input(lang_dict["email"], value=default_supplier_email)
        logo_file = st.file_uploader("Logo", type=["png","jpg","jpeg"])

        # Customer Info
        st.subheader(lang_dict["customer_info"])
        customer_name = st.text_input(lang_dict["to"])
        customer_address = st.text_area(lang_dict["to"] + " - Adresse")

        # Document Info
        st.subheader(lang_dict["document_info"])
        invoice_number = st.text_input(lang_dict["number"], value=str(uuid.uuid4())[:8])
        invoice_date = st.date_input(lang_dict["date"])
        invoice_due_date = st.date_input(lang_dict["due_date"], value=None)

        # Items
        if "items" not in st.session_state:
            st.session_state["items"] = []

        st.subheader(lang_dict["services_products"])
        with st.form("add_item_form"):
            description = st.text_input(lang_dict["description"])
            quantity = st.number_input(lang_dict["quantity"], min_value=1, value=1)
            unit_price = st.number_input(lang_dict["unit_price"], min_value=0.0, value=0.0)
            vat_rate = st.number_input(lang_dict["vat_rate"], min_value=0.0, value=19.0)
            add_item_btn = st.form_submit_button(lang_dict["add"])
            if add_item_btn:
                new_item = {
                    "description": description,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "vat_rate": vat_rate
                }
                st.session_state["items"].append(new_item)

        if len(st.session_state["items"]) > 0:
            st.write(lang_dict["services_products"] + ":")
            for idx, item in enumerate(st.session_state["items"]):
                item_line = (
                    f"{lang_dict['description']}: {item['description']} | "
                    f"{lang_dict['quantity']}: {item['quantity']} | "
                    f"{lang_dict['unit_price']}: {item['unit_price']} | "
                    f"{lang_dict['vat_rate']}: {item['vat_rate']}%"
                )
                st.write(f"- {idx+1}) {item_line}")
                if st.button(f"{lang_dict['remove']} {idx+1}", key=f"remove_{idx}"):
                    st.session_state["items"].pop(idx)

        # Additional Info
        st.subheader(lang_dict["additional_info"])
        payment_terms = st.text_area(lang_dict["payment_terms"])
        delivery_terms = st.text_area(lang_dict["delivery_terms"])
        accept_checks = st.checkbox(lang_dict["accept_checks"])

    # Right column: Real-time PDF preview
    with col_pdf:
        st.subheader("Preview / Aperçu / معاينة")

        # Prepare the data dict
        data = {
            "doc_type": doc_type,
            "supplier_name": supplier_name,
            "supplier_address": supplier_address,
            "supplier_tax_id": supplier_tax_id,
            "supplier_mobile": supplier_mobile,
            "supplier_email": supplier_email,
            "logo": logo_file,
            "customer_name": customer_name,
            "customer_address": customer_address,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "invoice_due_date": invoice_due_date,
            "payment_terms": payment_terms,
            "delivery_terms": delivery_terms,
            "accept_checks": accept_checks
        }

        # Generate PDF
        pdf_bytes = create_modern_invoice_pdf(data, st.session_state["items"], lang_dict, primary_color, lang_choice)
        # Show PDF in iframe
        pdf_display = get_pdf_iframe(pdf_bytes.read())
        st.markdown(pdf_display, unsafe_allow_html=True)

    # Download button
    st.markdown("---")
    if st.button(lang_dict["download"]):
        if len(st.session_state["items"]) == 0:
            if lang_choice == "en":
                st.error("Please add at least one item.")
            elif lang_choice == "fr":
                st.error("Veuillez ajouter au moins un article.")
            else:  # ar
                st.error("الرجاء إضافة عنصر واحد على الأقل.")
        else:
            # Re-generate for download
            pdf_bytes = create_modern_invoice_pdf(data, st.session_state["items"], lang_dict, primary_color, lang_choice)
            file_name = f"{doc_type}_{invoice_number}.pdf"
            st.download_button(
                label=lang_dict["download"],
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
