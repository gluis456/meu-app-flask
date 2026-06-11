import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Configure com suas credenciais ──────────────────────────────────
SMTP_HOST   = "smtp.gmail.com"
SMTP_PORT   = 587
EMAIL_USER  = "seuemail@gmail.com"
EMAIL_PASS  = "sua_senha_de_app"   # Use "Senha de App" do Google

def enviar_email(destinatario: str, assunto: str, corpo_html: str) -> dict:
    """
    Envia um e-mail HTML para o destinatário informado.
    Retorna {"ok": True} ou {"ok": False, "erro": mensagem}
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"]    = EMAIL_USER
        msg["To"]      = destinatario

        msg.attach(MIMEText(corpo_html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, destinatario, msg.as_string())

        return {"ok": True}

    except Exception as e:
        return {"ok": False, "erro": str(e)}


def template_boas_vindas(nome: str) -> str:
    return f"""
    <html><body style="font-family:Arial,sans-serif;padding:20px">
      <h2 style="color:#4f46e5">Olá, {nome}! 👋</h2>
      <p>Obrigado por entrar em contato. Nossa equipe retornará em breve.</p>
      <hr/>
      <small style="color:#888">CRM System — mensagem automática</small>
    </body></html>
    """

def template_followup(nome: str, nota: str) -> str:
    return f"""
    <html><body style="font-family:Arial,sans-serif;padding:20px">
      <h2 style="color:#4f46e5">Follow-up — {nome}</h2>
      <p>{nota}</p>
      <hr/>
      <small style="color:#888">CRM System — mensagem automática</small>
    </body></html>
    """
