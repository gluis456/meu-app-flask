import plotly.graph_objects as go
import plotly.express as px
import json
from database import Cliente, Interacao

def grafico_status() -> str:
    clientes = Cliente.query.all()
    contagem = {}
    for c in clientes:
        contagem[c.status] = contagem.get(c.status, 0) + 1

    cores = {"Lead": "#6366f1", "Ativo": "#22c55e", "Inativo": "#f59e0b"}
    fig = go.Figure(go.Pie(
        labels=list(contagem.keys()),
        values=list(contagem.values()),
        hole=0.4,
        marker_colors=[cores.get(s, "#94a3b8") for s in contagem.keys()]
    ))
    fig.update_layout(
        title="Clientes por Status",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        margin=dict(t=40, b=10, l=10, r=10),
        height=300,
    )
    return fig.to_json()


def grafico_interacoes() -> str:
    interacoes = Interacao.query.all()
    contagem = {}
    for i in interacoes:
        contagem[i.tipo] = contagem.get(i.tipo, 0) + 1

    fig = go.Figure(go.Bar(
        x=list(contagem.keys()),
        y=list(contagem.values()),
        marker_color="#6366f1"
    ))
    fig.update_layout(
        title="Interações por Tipo",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        margin=dict(t=40, b=10, l=10, r=10),
        height=300,
    )
    return fig.to_json()


def grafico_deals() -> str:
    clientes = Cliente.query.filter(Cliente.valor_deal > 0).all()
    fig = go.Figure(go.Bar(
        x=[c.nome for c in clientes],
        y=[c.valor_deal for c in clientes],
        marker_color="#22c55e"
    ))
    fig.update_layout(
        title="Valor de Deals por Cliente",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        margin=dict(t=40, b=10, l=10, r=10),
        height=300,
    )
    return fig.to_json()
