import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

customers = pd.read_csv("customers.csv")
products = pd.read_csv("products.csv")

def generate_invoice(customer_id, product_ids, quantities):
    participant = customers[customers['customer_id'] == customer_id].iloc[0]
    event = products[products['product_id'].isin(product_ids)]
    if len(event) != len(quantities):
        st.error("Mismatch between selected events and quantities")
        return None
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=30)
    pdf.cell(200, 10, txt="INVOICE", ln=True, align='C')
    pdf.image("company_logo.png", x=160, y=25, w=30)
    
    # Invoice header details
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Sangam Pvt Ltd.", ln=True)
    pdf.cell(200, 10, txt="Indore, India", ln=True)
    pdf.cell(200, 10, txt="Pincode: 452010", ln=True)
    pdf.cell(200, 10, txt="Email: vaibhav2oke@gmail.com", ln=True)
    pdf.cell(200, 10, txt="", ln=True)  # Space
    
    # Participant details
    pdf.set_font("Arial", 'B', size=20)
    pdf.cell(200, 10, txt="Participant Details:-------------", ln=True)
    pdf.cell(200, 10, txt="", ln=True)  # Space
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Participant: {participant['customer_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Address: {participant['address']}", ln=True)
    pdf.cell(200, 10, txt=f"Mobile: {participant['mobile']}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {participant['email']}", ln=True)
    pdf.cell(200, 10, txt="", ln=True)  # Space
    
    # Invoice table headers
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(60, 10, txt="Event", border=1)
    pdf.cell(60, 10, txt="Description", border=1)
    pdf.cell(20, 10, txt="Qty", border=1)
    pdf.cell(30, 10, txt="Unit Price", border=1)
    pdf.cell(30, 10, txt="Total", border=1)
    pdf.ln()

    # Invoice table rows
    total = 0
    pdf.set_font("Arial", size=12)
    for i, product in event.iterrows():
        quantity = quantities[product_ids.index(product['product_id'])]
        line_total = product['price'] * quantity
        total += line_total
        pdf.cell(60, 10, txt=product['product_name'], border=1)
        pdf.cell(60, 10, txt=product['description'], border=1)
        pdf.cell(20, 10, txt=str(quantity), border=1)
        pdf.cell(30, 10, txt=f"Rs. {product['price']}", border=1)
        pdf.cell(30, 10, txt=f"Rs. {line_total}", border=1)
        pdf.ln()
    
    # Space before total
    pdf.cell(200, 10, txt="", ln=True)
    
    # Total amount
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(170, 10, txt="Total", border=1)
    pdf.cell(30, 10, txt=f"Rs. {total}", border=1)
    
    # Add QR code image at the end of the PDF
    pdf.cell(200, 10, txt=" ", ln=True)  # Space
    pdf.image("company_logo.png", x=80, y=None, w=50)  # Adjust the position and size as needed
    
    filename = f"invoice_{customer_id}.pdf"
    pdf.output(filename)
    return filename
st.title("Your bill")
st.sidebar.header("Select Participant and Events")

participant_names = customers["customer_name"].tolist()
selected_participant = st.sidebar.selectbox("Participant", participant_names)
customer_id = customers[customers['customer_name']==selected_participant]['customer_id'].values[0]

event_names = products['product_name'].tolist()
selected_events = st.sidebar.multiselect("Events", event_names)
product_ids = products[products['product_name'].isin(selected_events)]['product_id'].tolist()

quantities = []
for event in selected_events:
    quantity = st.sidebar.number_input(f"Quantity of {event}", min_value=1, max_value=100, value=1)
    quantities.append(quantity)


if st.sidebar.button("Generate Invoice"):
    if len(product_ids) != len(quantities):
        st.error("Mismatch between selected events and quantities")
    else:
        filename = generate_invoice(customer_id, product_ids, quantities)
        if filename:
            with open(filename, 'rb') as f:
                st.download_button(
                    label="Download Invoice",
                    data=f,
                    file_name=filename,
                    mime="application/pdf",
                )
            with open(filename, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

st.write(f"Selected Participant: {selected_participant}")
st.write("Selected Events:")
for i, event in enumerate(selected_events):
    st.write(f"{event} - {quantities[i]} units")
