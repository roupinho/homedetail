import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# Definir tempos por tarefa (em dias por unidade)
task_times = {
    'demolicoes_rocos': 1,
    'canalizacoes': 0.5,
    'eletricidades': 0.5,
    'assentamento_base_duche': 0.5,
    'assentamento_sanitarios': 0.5,
    'estuque': 2,
    'pintura': 1,
    'montagem_moveis': 2,
    'demolicao_paredes': 2,
    'barramento_paredes': 1,
    'regularizacao_pavimento': 1,
    'preparacao_paredes': 1,
    'teto_falso_montagem': 1,
    'acabamento_pintura_teto_falso': 1,
    'divisoria_gesso_laminado': 1,
    'pre_instalacao_ac': 1,
    'assentamento_soalho': 0.5,
    'assentamento_ladrilho': 1,
    'assentamento_azulejo': 1
}

# Dependências de tarefas
task_dependencies = {
    'canalizacoes': ['demolicoes_rocos'],
    'eletricidades': ['demolicoes_rocos'],
    'assentamento_base_duche': ['canalizacoes'],
    'estuque': ['canalizacoes', 'eletricidades'],
    'pintura': ['estuque', 'preparacao_paredes'],
    'montagem_moveis': ['pintura'],
    'assentamento_sanitarios': ['pintura'],
    'teto_falso_montagem': ['demolicoes_rocos'],
    'acabamento_pintura_teto_falso': ['teto_falso_montagem'],
    'divisoria_gesso_laminado': ['demolicoes_rocos'],
    'pre_instalacao_ac': ['demolicoes_rocos'],
    'assentamento_soalho': ['regularizacao_pavimento'],
    'assentamento_ladrilho': ['regularizacao_pavimento'],
    'assentamento_azulejo': ['regularizacao_pavimento']
}

def calcular_tempo_total(area_m2, tarefas):
    unidades = area_m2 / 4
    tempo_total = {}
    for tarefa in tarefas:
        tempo = task_times.get(tarefa, 1) * unidades
        tempo_total[tarefa] = round(tempo, 1)
    return tempo_total

def agendar_tarefas(tempo_total, data_inicio, tarefas_selecionadas):
    calendario = {}
    tarefas_concluidas = set()
    dia_atual = data_inicio

    while len(tarefas_concluidas) < len(tempo_total):
        progresso = False
        for tarefa, duracao in tempo_total.items():
            if tarefa in tarefas_concluidas:
                continue
            deps = task_dependencies.get(tarefa, [])
            deps = [d for d in deps if d in tarefas_selecionadas]
            if all(d in tarefas_concluidas for d in deps):
                calendario[tarefa] = (dia_atual, dia_atual + timedelta(days=int(duracao)))
                dia_atual += timedelta(days=int(duracao))
                tarefas_concluidas.add(tarefa)
                progresso = True
        if not progresso:
            st.error("Erro: dependências não resolvidas. Verifique seleção de tarefas.")
            break
    return calendario

def desenhar_gantt(calendario):
    fig, ax = plt.subplots(figsize=(12, 6))
    tarefas = list(calendario.keys())
    for i, tarefa in enumerate(tarefas):
        inicio, fim = calendario[tarefa]
        duracao = (fim - inicio).days
        ax.barh(i, duracao, left=inicio, color='skyblue')
    ax.set_yticks(range(len(tarefas)))
    ax.set_yticklabels([tarefa.replace('_', ' ').capitalize() for tarefa in tarefas])
    ax.invert_yaxis()
    ax.set_xlabel('Data')
    ax.set_title('Cronograma da Obra')
    plt.grid(True)
    st.pyplot(fig)

# ================== STREAMLIT ===================
st.title("📋 Gestão de Obras")

with st.form("dados_obra"):
    morada = st.text_input("🏠 Morada da Obra")
    tipo_obra = st.selectbox("📦 Tipo de Obra", ["Casa de banho", "Cozinha", "Remodelação Total", "Outros"])
    area_m2 = st.number_input("📏 Área da divisão (m2)", min_value=1.0, step=1.0)
    data_material = st.date_input("📅 Data de chegada dos materiais")
    prazo_final = st.date_input("🏁 Prazo final da obra")

    st.markdown("### Selecione as tarefas necessárias:")
    tarefas_selecionadas = []
    for tarefa in task_times.keys():
        if st.checkbox(tarefa.replace('_', ' ').capitalize()):
            tarefas_selecionadas.append(tarefa)

    submitted = st.form_submit_button("📈 Gerar Cronograma")

if submitted:
    if not tarefas_selecionadas:
        st.warning("⚠️ Selecione pelo menos uma tarefa!")
    else:
        tempo_total = calcular_tempo_total(area_m2, tarefas_selecionadas)
        calendario = agendar_tarefas(tempo_total, datetime.combine(data_material, datetime.min.time()), tarefas_selecionadas)

        st.success("✅ Cronograma Gerado!")
        st.subheader("Resumo:")
        for tarefa, (inicio, fim) in calendario.items():
            st.write(f"**{tarefa.replace('_', ' ').capitalize()}**: {inicio.strftime('%Y-%m-%d')} → {fim.strftime('%Y-%m-%d')}")

        st.subheader("Gráfico de Gantt:")
        desenhar_gantt(calendario)
