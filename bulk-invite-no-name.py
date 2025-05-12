#!/usr/bin/env python3
import csv
import os
import time
import yaml
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from tqdm import tqdm
import smtplib
from email.message import EmailMessage
from email.utils import formataddr


def load_config(path="config.yaml"):
    """Load SMTP and file-path settings from YAML."""
    with open(path) as f:
        return yaml.safe_load(f)


def load_invite_template(path="templates/invite-no-name.txt"):
    """Read the single-part invite template."""
    with open(path, encoding='utf-8') as f:
        return f.read()


def load_email_template(path="templates/email-no-name.html"):
    """Read HTML email template."""
    return open(path, encoding='utf-8').read()


def generate_pdf(guest, template_text, text_color, bg_path, output_path):
    """Render a PDF invite using ReportLab with a static background image and the loaded template text."""
    bg = ImageReader(bg_path)
    width, height = bg.getSize()
    c = canvas.Canvas(output_path, pagesize=(width, height))
    c.drawImage(bg, 0, 0, width=width, height=height)

    # Fill placeholders in the template text
    text = template_text
    for key, val in guest.items():
        text = text.replace(f"${key}", val)

    # Draw the text centered near the bottom of the page
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(HexColor(text_color))
    x = width / 2
    y = 50  # adjust as needed
    c.drawCentredString(x, y, text)

    c.showPage()
    c.save()


def send_email(guest, email_html, pdf_path, config, subject):
    """Send an HTML email with the invite PDF attached."""
    placeholders = {key: guest.get(key, '') for key in guest}
    html = email_html
    for key, val in placeholders.items():
        html = html.replace(f"${key}", val)

    msg = EmailMessage()
    msg['Subject'] = subject

    # build From display and address
    from_name = config['from_name']
    from_addr    = config['from_address']
    msg['From']  = formataddr((from_name, from_addr))

    msg['To'] = guest['email']
    msg.add_alternative(html, subtype='html')

    with open(pdf_path, 'rb') as f:
        msg.add_attachment(
            f.read(),
            maintype='application',
            subtype='pdf',
            filename=os.path.basename(pdf_path)
        )

    timeout = 20

    with smtplib.SMTP_SSL(config['smtp_host'], config['smtp_port'], timeout=timeout) as smtp:
        smtp.login(config['smtp_user'], config['smtp_password'])
        smtp.send_message(msg)


def main():
    cfg = load_config()
    guests = list(csv.DictReader(open(cfg['guests_csv'], encoding='utf-8')))
    center_footer = load_invite_template(cfg['invite_template_no_name'])
    email_template = load_email_template(cfg['email_template_no_name'])
    
    invites_dir = 'output/invites'
    os.makedirs(invites_dir, exist_ok=True)
    subject = cfg.get('email_subject', 'invite')

    # Step 1: generate all invites
    generated = []
    for guest in tqdm(guests, desc="Generating invites"):
        guest_id = guest['guest_id']
        pdf_path = os.path.join(invites_dir, f"invite_{guest_id}.pdf")
        generate_pdf(guest, center_footer, cfg['invite_text_color'], cfg['assets_bg_no_name'], pdf_path)
        generated.append((guest, pdf_path))

    # Step 2: prompt user to review invites
    print(f"\nAll {len(generated)} invites have been generated in '{invites_dir}'.")
    print("Please review them now. When you're ready to send, type 'yes' and hit Enter.")
    answer = input("Send all emails? [yes/no]: ").strip().lower()

    if answer in ('y', 'yes'):
        print("Sending emails...")
        for guest, pdf_path in tqdm(generated, desc="Sending invites"):
            send_email(guest, email_template, pdf_path, cfg, subject)
            time.sleep(cfg['seconds_to_wait']) # wait x seconds before sending, can be set to 0 if necessary
        print("All emails sent.")
    else:
        print("Aborted. No emails were sent.")


if __name__ == '__main__':
    main()