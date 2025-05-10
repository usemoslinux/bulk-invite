#!/usr/bin/env python3
import csv
import os
import time
import yaml
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from tqdm import tqdm
import smtplib
from email.message import EmailMessage
from email.utils   import formataddr


def load_config(path="config.yaml"):
    """Load SMTP and file-path settings from YAML."""
    with open(path) as f:
        return yaml.safe_load(f)


def load_invite_template(path="templates/invite.txt"):
    # Expect four sections: main text, left footer, right footer, center footer
    content = open(path, encoding='utf-8').read()
    parts = content.split("\n---\n")
    if len(parts) != 4:
        raise ValueError("invite template (templates/invite.txt) must have four sections separated by '---'.")
    return parts[0], parts[1], parts[2], parts[3]


def load_email_template(path="templates/email.html"):
    """Read HTML email template."""
    return open(path, encoding='utf-8').read()

def generate_pdf(guest, main_text, left_footer, right_footer, center_footer, text_color, bg_path, output_path):
    """Render a PDF invite using ReportLab with a static background image."""
    # Setup canvas with background image
    bg = ImageReader(bg_path)
    width, height = bg.getSize()
    c = canvas.Canvas(output_path, pagesize=(width, height))
    c.drawImage(bg, 0, 0, width=width, height=height)

    # Prepare main and footer texts replacing placeholders
    placeholders = {key: guest.get(key, '') for key in guest}
    def fill(text):
        for key, val in placeholders.items():
            text = text.replace(f"${key}", val)
        return text

    # Convert hex text_color string to ReportLab Color object
    rl_text_color = HexColor(text_color)

    # Render main text with HTML support using Platypus Paragraph
    text_html = fill(main_text)
    styles = getSampleStyleSheet()
    font_name = 'Times-Roman'
    font_size_main = 48
    line_spacing_main = font_size_main * 1.5
    style = ParagraphStyle(
        'Invite', parent=styles['Normal'],
        fontName=font_name, fontSize=font_size_main,
        leading=line_spacing_main, alignment=TA_CENTER,
        textColor=rl_text_color
    )
    story = [Paragraph(text_html, style)]
    header_height = 450
    footer_content_height = 350
    frame_width = width * 0.8
    frame_height = height - header_height - footer_content_height
    frame_x = (width - frame_width) / 2
    frame_y = footer_content_height
    Frame(frame_x, frame_y, frame_width, frame_height, showBoundary=0).addFromList(story, c)

    # Render HTML footers with HTML support using Platypus Paragraph
    left_html = fill(left_footer)
    right_html = fill(right_footer)
    footer_frame_height = 150
    footer_y_platypus = 130
    font_size_footer = font_size_main / 1.5
    line_spacing_footer = line_spacing_main / 1.5

    footer_style_left = ParagraphStyle(
        'FooterLeft', parent=styles['Normal'],
        fontName='Helvetica', fontSize=font_size_footer,
        leading=line_spacing_footer, alignment=TA_LEFT,
        textColor=rl_text_color
    )
    footer_style_right = ParagraphStyle(
        'FooterRight', parent=styles['Normal'],
        fontName='Helvetica', fontSize=font_size_footer,
        leading=line_spacing_footer, alignment=TA_RIGHT,
        textColor=rl_text_color
    )
    left_frame = Frame(150, footer_y_platypus, (width / 2) - 150, footer_frame_height, showBoundary=0)
    left_frame.addFromList([Paragraph(left_html, footer_style_left)], c)
    right_frame = Frame((width / 2), footer_y_platypus, (width / 2) - 150, footer_frame_height, showBoundary=0)
    right_frame.addFromList([Paragraph(right_html, footer_style_right)], c)

    # Render centered footer (plain text)
    center_text = fill(center_footer)
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(rl_text_color)
    center_y = footer_y_platypus - 20
    c.drawCentredString(width / 2, center_y, center_text)

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

    timeout = 10

    with smtplib.SMTP_SSL(config['smtp_host'], config['smtp_port'], timeout=timeout) as smtp:
        smtp.login(config['smtp_user'], config['smtp_password'])
        smtp.send_message(msg)


def main():
    cfg = load_config()
    guests = list(csv.DictReader(open(cfg['guests_csv'], encoding='utf-8')))
    main_text, left_footer, right_footer, center_footer = load_invite_template(cfg['invite_template'])
    email_template = load_email_template(cfg['email_template'])
    
    invites_dir = 'output/invites'
    os.makedirs(invites_dir, exist_ok=True)
    subject = cfg.get('email_subject', 'invite')

    # Step 1: generate all invites
    generated = []
    for guest in tqdm(guests, desc="Generating invites"):
        guest_id = guest['guest_id']
        pdf_path = os.path.join(invites_dir, f"invite_{guest_id}.pdf")
        generate_pdf(guest, main_text, left_footer, right_footer, center_footer, cfg['invite_text_color'], cfg['assets_bg'], pdf_path)
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