from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from database import db, Cliente, Interacao
from email_service import enviar_email, template_boas_vindas, template_followup
from export_service import exportar_clientes_excel, exportar_clientes_csv, exportar_interacoes_excel
import dashboard
import io

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "crm-secret-key"

db.init_app(app)

with app.app_context():
    db.create_all()


# ─── Dashboard ──────────────────────────────────────────────────────
@app.route("/")
def index():
    total     = Cliente.query.count()
    leads     = Cliente.query.filter_by(status="Lead").count()
    ativos    = Cliente.query.filter_by(status="Ativo").count()
    inativos  = Cliente.query.filter_by(status="Inativo").count()
    total_deal= sum(c.valor_deal for c in Cliente.query.all())
    recentes  = Cliente.query.order_by(Cliente.criado_em.desc()).limit(5).all()
    ultimas   = Interacao.query.order_by(Interacao.data.desc()).limit(5).all()

    g_status     = dashboard.grafico_status()
    g_interacoes = dashboard.grafico_interacoes()
    g_deals      = dashboard.grafico_deals()

    return render_template("index.html",
        total=total, leads=leads, ativos=ativos, inativos=inativos,
        total_deal=total_deal, recentes=recentes, ultimas=ultimas,
        g_status=g_status, g_interacoes=g_interacoes, g_deals=g_deals
    )


# ─── Clientes ────────────────────────────────────────────────────────
@app.route("/clientes")
def clientes():
    q      = request.args.get("q", "")
    status = request.args.get("status", "")
    query  = Cliente.query
    if q:      query = query.filter(Cliente.nome.ilike(f"%{q}%") | Cliente.empresa.ilike(f"%{q}%"))
    if status: query = query.filter_by(status=status)
    lista  = query.order_by(Cliente.criado_em.desc()).all()
    return render_template("clientes.html", clientes=lista, q=q, status=status)


@app.route("/clientes/novo", methods=["GET", "POST"])
def novo_cliente():
    if request.method == "POST":
        cliente = Cliente(
            nome       = request.form["nome"],
            email      = request.form["email"],
            telefone   = request.form.get("telefone", ""),
            empresa    = request.form.get("empresa", ""),
            status     = request.form.get("status", "Lead"),
            valor_deal = float(request.form.get("valor_deal") or 0),
        )
        db.session.add(cliente)
        db.session.commit()

        # E-mail de boas-vindas automático
        enviar_email(cliente.email, "Bem-vindo! 👋", template_boas_vindas(cliente.nome))

        flash(f"Cliente '{cliente.nome}' cadastrado com sucesso! E-mail de boas-vindas enviado.", "success")
        return redirect(url_for("clientes"))
    return render_template("cliente_form.html", cliente=None)


@app.route("/clientes/<int:id>")
def detalhe_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    return render_template("cliente_detalhe.html", cliente=cliente)


@app.route("/clientes/<int:id>/editar", methods=["GET", "POST"])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == "POST":
        cliente.nome       = request.form["nome"]
        cliente.email      = request.form["email"]
        cliente.telefone   = request.form.get("telefone", "")
        cliente.empresa    = request.form.get("empresa", "")
        cliente.status     = request.form.get("status", "Lead")
        cliente.valor_deal = float(request.form.get("valor_deal") or 0)
        db.session.commit()
        flash("Cliente atualizado!", "success")
        return redirect(url_for("detalhe_cliente", id=id))
    return render_template("cliente_form.html", cliente=cliente)


@app.route("/clientes/<int:id>/deletar", methods=["POST"])
def deletar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash(f"Cliente '{cliente.nome}' removido.", "warning")
    return redirect(url_for("clientes"))


# ─── Interações ──────────────────────────────────────────────────────
@app.route("/clientes/<int:id>/interacao", methods=["GET", "POST"])
def nova_interacao(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == "POST":
        interacao = Interacao(
            cliente_id = id,
            tipo       = request.form["tipo"],
            nota       = request.form["nota"],
        )
        db.session.add(interacao)
        db.session.commit()

        # Follow-up por e-mail opcional
        if request.form.get("enviar_email"):
            enviar_email(
                cliente.email,
                f"Follow-up — {interacao.tipo}",
                template_followup(cliente.nome, interacao.nota)
            )
            flash("Interação registrada e e-mail de follow-up enviado!", "success")
        else:
            flash("Interação registrada!", "success")

        return redirect(url_for("detalhe_cliente", id=id))
    return render_template("interacao_form.html", cliente=cliente)


# ─── Exportações ─────────────────────────────────────────────────────
@app.route("/exportar/clientes/excel")
def exp_clientes_excel():
    data = exportar_clientes_excel()
    return send_file(io.BytesIO(data), download_name="clientes.xlsx",
                     as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route("/exportar/clientes/csv")
def exp_clientes_csv():
    data = exportar_clientes_csv()
    return send_file(io.BytesIO(data.encode()), download_name="clientes.csv",
                     as_attachment=True, mimetype="text/csv")

@app.route("/exportar/interacoes/excel")
def exp_interacoes_excel():
    data = exportar_interacoes_excel()
    return send_file(io.BytesIO(data), download_name="interacoes.xlsx",
                     as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if __name__ == "__main__":
    app.run(debug=True)
