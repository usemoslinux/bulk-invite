# Sistema de invitaciones en masa

Este proyecto contiene dos scripts (`bulk-invite.py` y `bulk-invite-no-name.py`) diseñados para generar invitaciones en formato PDF y enviarlas por correo electrónico. Los scripts permiten personalizar las invitaciones y asociarlas a un ID único para facilitar el control de asistencia. 

**Nota: Estos scripts deben utilizarse en una red que NO use un proxy.**

## 1. Descargar el proyecto desde GitHub

```bash
git clone https://github.com/usemoslinux/bulk-invite.git
cd bulk-invite
```

## 2. Crear un entorno virtual

Crear y activar un entorno virtual para instalar las dependencias:

```bash
python -m venv venv
source venv/bin/activate
```

## 3. Instalar paquetes necesarios

```bash
pip install PyYAML reportlab tqdm pillow
```

## 4. El listado de invitados

El listado de invitados debe estar en el archivo `guests.csv`, un archivo separado por comas. Cada campo de texto, además, debe estar empezar y terminar con comillas (").

Los 3 primeros campos (guest_id, guest_name, email) son obligatorios. Se pueden agregar otros campos adicionales, según sea necesario.

El campo email puede incluir varias direcciones, pero deben estar separadas por comas (,) no por punto y coma (;).

Cada correo está asociado a un ID único para facilitar el control de asistencia al evento. Este sistema evita la necesidad de usar un QR y no requiere un servidor para registrar las asistencias.

## 5. Utilización

Para invitaciones nominadas:

```bash
python bulk-invite.py
```

Para invitaciones genéricas:

```bash
python bulk-invite-no-name.py
```

### 5.1. ¿Cuándo usar cada script?

#### a) bulk-invite.py

Uso: para invitaciones nominadas.

Características:
- Lee el campo guest_name en `guests.csv` y lo incluye en la invitación.
- Utiliza `templates/invite.txt` como texto de la invitación. Este archivo debe contener 4 secciones separadas por "---":
    - Texto principal
    - Footer izquierdo
    - Footer derecho
    - Mini footer centrado con el número de ID
- Los placeholders en el texto de la invitación pueden usar los nombres de los campos de `guests.csv` precedidos por el signo pesos ($).
- Utiliza `templates/email.html` para enviar el correo con la invitación.
- Usa un fondo definido en `assets_bg` (`config.yaml`), que debería incluir el logo oficial y nada más. - El texto de la invitación se superpone a este fondo.
- El color del texto está definido en `invite_text_color` en `config.yaml`.

#### b) bulk-invite-no-name.py

Uso: para invitaciones genéricas dirigidas a un público amplio (por ejemplo, toda la comunidad residente).

Características:
- Ignora el campo guest_name en `guests.csv`.
- Utiliza `templates/invite-no-name.txt` para el mini footer centrado, que debe incluir siempre el número de ID.
- Los placeholders en el texto del footer pueden usar los nombres de los campos de `guests.csv` precedidos por el signo pesos ($).
- Utiliza `templates/email-no-name.html` para enviar el correo con la invitación.
- Usa un fondo definido en `assets_bg_no_name` (`config.yaml`), que debería incluir el logo oficial y el texto de la invitación. Solo se agrega el mini footer con el ID.
- El color del texto está definido en `invite_text_color` en `config.yaml`.

## 6. Notas adicionales

Se sugiere revisar y personalizar los archivos de configuración (`config.yaml`) y las plantillas (`templates/`) antes de ejecutar los scripts. Se proveen ejemplos en inglés y español, donde se deberán reemplazar los espacios entre corchetes con la información correspondiente. Los marcadores que comienzan con el signo pesos se utilizan como marcadores de posición para colocar los campos correspondientes del archivo `guests.csv`.

Los tipos de letra soportados por reportlab para construir los tarjetones son: __'Courier', 'Courier-Bold', 'Courier-BoldOblique', 'Courier-Oblique', 'Helvetica', 'Helvetica-Bold', 'Helvetica-BoldOblique', 'Helvetica-Oblique', 'Symbol', 'Times-Bold', 'Times-BoldItalic', 'Times-Italic', 'Times-Roman', 'ZapfDingbats'__. Este cambio debe realizarse directo en el archivo .py correspondiente.

Los PDFs generados se guardan en la carpeta `output/invites`.

Antes de enviar los correos, los scripts pedirán confirmación para proceder con el envío. Se sugiere fuertemente su revisión previo al envío.