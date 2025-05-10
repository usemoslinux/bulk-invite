# Bulk invitation system

This project contains two scripts (`bulk-invite.py` and `bulk-invite-no-name.py`) designed to generate invitations in PDF format and send them by email. The scripts allow you to customize the invitations and associate them with a unique ID for easy attendance control. 

**Note: these scripts must be used on a network that does NOT rely on a proxy.

## 1. Download the project from GitHub

````bash
git clone https://github.com/usemoslinux/bulk-invite.git
cd bulk-invite
````

## 2. Create a virtual environment

Create and activate a virtual environment to install the dependencies:

````bash
python -m venv venv
source venv/bin/activate
````

## 3. Install necessary packages

````bash
pip install PyYAML reportlab tqdm pillow
````

## 4. The guest list

The guest list must be filled in the `guests.csv` file, a comma separated file. Each text field must also begin and end with quotation marks (").

The first 3 fields (`guest_id`, `guest_name`, `email`) are mandatory. Additional fields can be added as needed.

The `email` field can include multiple addresses, but they must be separated by commas (,) not semicolons (;).

Each email is associated with a unique ID to facilitate event attendance control. This system avoids the need to use a QR and does not require a server to record attendance.

## 5. Use

For nominated invitations:

````bash
python bulk-invite.py
````

For generic invites:

````bash
python bulk-invite-no-name.py
````

### 5.1. When to use each script?

#### a) bulk-invite.py

Usage: for nominated invites.

Features:
- Reads the `guest_name` field in `guests.csv` and includes it in the invitation.
- Uses `templates/invite.txt` as invitation text. This file must contain 4 sections separated by "---":
    - Main text
    - Left footer
    - Right footer
    - Mini footer centered with the ID number
- The placeholders in the invitation text can use the field names from `guests.csv` preceded by the dollar sign ($).
- Use `templates/email.html` to send the email invitation.
- Use a background defined in `assets_bg` (`config.yaml`), which should include the official logo and nothing else.
- The text of the invitation is superimposed on this background.
- The text color is defined in `invite_text_color` in config.yaml.

#### b) bulk-invite-no-name.py

Use: for generic invitations addressed to a wide audience (e.g., the entire resident community).

Features:
- Ignore the `guest_name` field in `guests.csv`.
- Use `templates/invite-no-name.txt` for the centered mini footer, which should always include the ID number.
- Placeholders in the footer text can use the names of the fields in `guests.csv` preceded by the dollar sign ($).
- Use `templates/email-no-name.html` to send the email invitation.
- Use a background defined in `assets_bg_no_name` (`config.yaml`), which should include the official logo and the text of the invitation. Only the mini footer with the ID is added.
- The text color is defined in `invite_text_color` in `config.yaml`.

## 6. Additional notes

It is suggested to review and customize the configuration files (`config.yaml`) and templates (`templates/`) before running the scripts. Examples are provided in English and Spanish, where the spaces between brackets should be replaced with the corresponding information. Markers starting with the dollar sign ($) are used as placeholders for the fields in `guests.csv`.

The fonts supported by reportlab to build the cards are: __'Courier', 'Courier-Bold', 'Courier-BoldOblique', 'Courier-Oblique', 'Helvetica', 'Helvetica-Bold', 'Helvetica-BoldOblique', 'Helvetica-Oblique', 'Symbol', 'Times-Bold', 'Times-BoldItalic', 'Times-Italic', 'Times-Roman', 'ZapfDingbats'__. This change must be made directly in the corresponding .py file.

The generated PDFs are saved in the `output/invites` folder.

Before sending the emails, the scripts will ask for confirmation to proceed with the sending. It is strongly suggested to review them before sending.