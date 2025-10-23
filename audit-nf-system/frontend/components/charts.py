import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
import pandas as pd # type: ignore
from typing import Optional

# Definindo um template de cores padrão
DEFAULT_COLORS = px.colors.qualitative.Plotly
CUSTOM_COLOR_MAP = {
    "Aprovada": "#2ca02c", # Verde
    "Rejeitada": "#d62728", # Vermelho
    "Pendente": "#ff7f0e", # Laranja
    "Em Análise": "#1f77b4", # Azul
}

def _apply_default_layout(fig):
    """Aplica um layout padrão e limpo aos gráficos Plotly."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', # Fundo transparente
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
        legend_title_text='',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(
            family="sans-serif",
            size=12,
            color="#333333"
        )
    )
    return fig

def plot_status_distribution(
    data: pd.DataFrame, 
    names_col: str, 
    values_col: str, 
    title: str = "Distribuição de Status"
) -> go.Figure:
    """
    Cria um gráfico de pizza (donut) interativo para distribuição de status.
    """
    fig = px.pie(
        data, 
        names=names_col, 
        values=values_col, 
        title=title,
        hole=0.4, # Cria o efeito "donut"
        color=names_col,
        color_discrete_map=CUSTOM_COLOR_MAP
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return _apply_default_layout(fig)

def plot_timeline(
    data: pd.DataFrame, 
    x_col: str, 
    y_col: str, 
    color_col: Optional[str] = None, 
    title: str = "Evolução Temporal"
) -> go.Figure:
    """
    Cria um gráfico de linha ou área para séries temporais.
    """
    fig = px.area(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        color_discrete_map=CUSTOM_COLOR_MAP,
        labels={x_col: "Data", y_col: "Volume"}
    )
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='Volume')
    return _apply_default_layout(fig)

def plot_top_suppliers(
    data: pd.DataFrame, 
    x_col: str, 
    y_col: str,
    orientation: str = 'h',
    title: str = "Top Fornecedores"
) -> go.Figure:
    """
    Cria um gráfico de barras (horizontal ou vertical) para rankings.
    """
    fig = px.bar(
        data.sort_values(by=x_col, ascending=True if orientation == 'h' else False),
        x=x_col,
        y=y_col,
        orientation=orientation,
        title=title,
        color=x_col,
        color_continuous_scale=px.colors.sequential.Blues,
        text=x_col
    )
    fig.update_traces(texttemplate='%{text:,.2s}', textposition='auto')
    fig.update_layout(
        xaxis_title="Valor Total (R$)" if orientation == 'h' else "",
        yaxis_title=""
    )
    return _apply_default_layout(fig)

# Você pode adicionar mais gráficos aqui, como 'plot_heatmap'
