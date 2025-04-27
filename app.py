import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Definir equipas
workers = {
    'Pedreiro': 5,
    'Servente': 10,
    'Electricista': 1,
    'Canalizador': 1,
    'Pintor': 2,
    'Gesso Laminado': 2
}

# Especialidades múltiplas
multiskilled = 3

# Tempos de tarefas
task_times = {
    'Remocao Armarios Loicas': 0.5,
    'Demolicoes Rocos': 1,
    'Demolicao Paredes': 2,
    'Canalizacoes': 0.5,
    'Eletricidades': 0.5,
    'Assentamento Base Duche': 0.5,
    'Assentamento Sanitario': 0.5,
    'Estuque': 2,
    'Pintura': 1,
    'Montagem Moveis': 2,
    'Barramento Paredes': 1,
    'Regularizacao Pavimento': 1,
    'Preparacao Paredes': 1,
    'Teto Falso Montagem': 1,
    'Acabamento Pintura Teto Falso': 1,
    'Divisoria Gesso Laminado': 1,
    'Pre Instalacao AC': 1,
    'Assentamento Soalho': 0.5,
    'Assentamento Ladrilho': 1,
    'Assentamento Azulejo': 1,
    'Caixilharias': 1
}

# Dependencias
dependencies = {
    'Demolicoes Rocos': ['Remocao Armarios Loicas'],
    'Demolicao Paredes': ['Remocao Armarios Loicas'],
    'Canalizacoes': ['Demolicoes Rocos'],
    'Eletricidades': ['Demolicoes Rocos'],
    'Assentamento Base Duche': ['Canalizacoes'],
    'Estuque': ['Canalizacoes', 'Eletricidades'],
    'Pintura': ['Estuque', 'Preparacao Paredes'],
    'Montagem Moveis': ['Pintura'],
    'Assentamento Sanitario': ['Pintura'],
    'Teto Falso Montagem': ['Demolicoes Rocos'],
    'Acabamento Pintura Teto Falso': ['Teto Falso Montagem'],
    'Divisoria Gesso Laminado': ['Demolicoes Rocos'],
    'Pre Instalacao AC': ['Demolicoes Rocos'],
    'Assentamento Soalho': ['Regularizacao Pavimento'],
    'Assentamento Ladrilho': ['Regularizacao Pavimento'],
    'Assentamento Azulejo': ['Regularizacao Pavimento']
}

# Funcoes principais
def calcular_tempo(area, tarefas):
    unidades = area / 4
    return {tarefa: round(task_times.get(tarefa, 1) * unidades, 1) for tarefa in tarefas}

def agendar(tarefas, inicio):
    calendario = {}
    concluidas = set()
    dia_atual = inicio

    while len(concluidas) < len(tarefas):
        progresso = False
        for tarefa, duracao in tarefas.items():
            if tarefa in concluidas:
                continue
            deps = dependencies.get(tarefa, [])
            if all(d in concluidas for d in deps):
                calendario[tarefa] = (dia_atual, dia_atual + timedelta(days=int(duracao)))
                dia_atual += timedelta(days=int(duracao))
                concluidas.add(tarefa)
                progresso = True
        if not progresso:
            st.error("Erro de dependências.")
            break
    return calendario

def gerar_pdf(nome, morada, calendario):
    if not os.path.exists("projetos_guardados"):
        os.makedirs("projetos_guardados")
    caminho = f"projetos_guardados/{nome.replace(' ', '_')}.pdf"
    c = canvas.Canvas(caminho, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Obra: {nome}")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Morada: {morada}")
    y = height - 120
    c.drawString(50, y, "Tarefas:")
    for tarefa, (inicio, fim) in calendario.items():
        y -= 20
        c.drawString(60, y, f"{tarefa}: {inicio.strftime('%d-%m-%Y')} a {fim.strftime('%d-%m-%Y')}")
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()
    st.success(f"PDF gerado: {caminho}")

def gantt_chart(calendario):
    df = pd.DataFrame({
        'Tarefa': list(calendario.keys()),
        'Inicio': [inicio for inicio, fim in calendario.values()],
        'Fim': [fim for inicio, fim in calendario.values()]
    })
    fig = px.timeline(df, x_start="Inicio", x_end="Fim", y="Tarefa", color="Tarefa")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

# Streamlit App
st.title("Home Detail - Gestão de Obras")
st.subheader("Planeamento de Obras e Gestão de Equipa")

nome_obra = st.text_input("Nome da obra")
morada = st.text_input("Morada")
area_m2 = st.number_input("Área (m²)", min_value=1.0)
data_inicio = st.date_input("Data de Início")
prazo_final = st.date_input("Prazo Máximo de Conclusão")

st.subheader("Selecionar Tarefas")
tarefas_escolhidas = st.multiselect("Quais tarefas esta obra tem?", list(task_times.keys()))

if st.button("Gerar Cronograma"):
    if nome_obra and morada and tarefas_escolhidas:
        tempos = calcular_tempo(area_m2, tarefas_escolhidas)
        calendario = agendar(tempos, datetime.combine(data_inicio, datetime.min.time()))

        st.success("Cronograma gerado!")
        st.write("### Detalhes:")
        for tarefa, (inicio, fim) in calendario.items():
            st.write(f"**{tarefa}**: {inicio.strftime('%d-%m-%Y')} → {fim.strftime('%d-%m-%Y')}")

        gantt_chart(calendario)

        if st.button("Gerar PDF"):
            gerar_pdf(nome_obra, morada, calendario)
    else:
        st.warning("Preenche todos os campos e seleciona pelo menos uma tarefa!")
