import pandas as pd
import io
from database import Cliente, Interacao

def exportar_clientes_excel() -> bytes:
    clientes = Cliente.query.all()
    rows = []
    for c in clientes:
        rows.append({
            "ID":          c.id,
            "Nome":        c.nome,
            "E-mail":      c.email,
            "Telefone":    c.telefone,
            "Empresa":     c.empresa,
            "Status":      c.status,
            "Valor Deal":  c.valor_deal,
            "Cadastrado":  c.criado_em.strftime("%d/%m/%Y %H:%M"),
            "Interações":  len(c.interacoes),
        })

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Clientes")
        # Ajusta largura das colunas
        ws = writer.sheets["Clientes"]
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col) + 2
            ws.column_dimensions[col[0].column_letter].width = max_len

    return output.getvalue()


def exportar_clientes_csv() -> str:
    clientes = Cliente.query.all()
    rows = [c.to_dict() for c in clientes]
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def exportar_interacoes_excel() -> bytes:
    interacoes = Interacao.query.all()
    rows = []
    for i in interacoes:
        rows.append({
            "ID":          i.id,
            "Cliente":     i.cliente.nome,
            "Tipo":        i.tipo,
            "Nota":        i.nota,
            "Data":        i.data.strftime("%d/%m/%Y %H:%M"),
        })

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Interações")
    return output.getvalue()
