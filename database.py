from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = "clientes"

    id         = db.Column(db.Integer, primary_key=True)
    nome       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    telefone   = db.Column(db.String(20))
    empresa    = db.Column(db.String(100))
    status     = db.Column(db.String(20), default="Lead")  # Lead, Ativo, Inativo
    valor_deal = db.Column(db.Float, default=0.0)
    criado_em  = db.Column(db.DateTime, default=datetime.utcnow)

    interacoes = db.relationship("Interacao", backref="cliente", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":         self.id,
            "nome":       self.nome,
            "email":      self.email,
            "telefone":   self.telefone,
            "empresa":    self.empresa,
            "status":     self.status,
            "valor_deal": self.valor_deal,
            "criado_em":  self.criado_em.strftime("%d/%m/%Y %H:%M"),
        }


class Interacao(db.Model):
    __tablename__ = "interacoes"

    id         = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    tipo       = db.Column(db.String(50))   # Ligação, E-mail, Reunião, WhatsApp
    nota       = db.Column(db.Text)
    data       = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":    self.id,
            "tipo":  self.tipo,
            "nota":  self.nota,
            "data":  self.data.strftime("%d/%m/%Y %H:%M"),
        }
