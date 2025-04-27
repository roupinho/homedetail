from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Definir equipas e especialidades
workers = {
    'pedreiro': 5,
    'servente': 10,
    'electricista': 1,
    'canalizador': 1,
    'pintor': 2,
    'gesso_laminado': 2
}

# Pedreiros com múltiplas especialidades
multiskilled = 3

# Definir tempos por tarefa (em dias por unidade)
task_times = {
    'remocao_armarios_loicas': 0.5,
    'demolicoes_rocos': 1,
    'demolicao_paredes': 2,
    'canalizacoes': 0.5,
    'eletricidades': 0.5,
    'assentamento_base_duche': 0.5,
    'assentamento_sanitarios': 0.5,
    'estuque': 2,
    'pintura': 1,
    'montagem_moveis': 2,
    'barramento_paredes': 1,
    'regularizacao_pavimento': 1,
    'preparacao_paredes': 1,
    'teto_falso_montagem': 1,
    'acabamento_pintura_teto_falso': 1,
    'divisoria_gesso_laminado': 1,
    'pre_instalacao_ac': 1,
    'assentamento_soalho': 0.5,
    'assentamento_ladrilho': 1,
    'assentamento_azulejo': 1,
    'caixilharias': 1
}

# Dependências de tarefas
task_dependencies = {
    'demolicoes_rocos': ['remocao_armarios_loicas'],
    'demolicao_paredes': ['remocao_armarios_loicas'],
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

# Função para calcular duração total baseada na área
def calcular_tempo_total(area_m2, tarefas):
    unidades = area_m2 / 4
    tempo_total = {}
    for tarefa in tarefas:
        tempo = task_times.get(tarefa, 1) * unidades
        tempo_total[tarefa] = round(tempo, 1)
    return tempo_total

# Função para agendar tarefas respeitando dependências ajustadas
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
            print("\nErro: dependências não resolvidas. Verifique seleção de tarefas.")
            break
    return calendario

# Função para imprimir cronograma
def imprimir_cronograma(calendario):
    print("\nCronograma:")
    for tarefa, (inicio, fim) in calendario.items():
        print(f"{tarefa}: {inicio.strftime('%Y-%m-%d')} -> {fim.strftime('%Y-%m-%d')}")

# Função para desenhar gráfico de Gantt
def desenhar_gantt(calendario, nome_obra, morada):
    fig, ax = plt.subplots(figsize=(10, 6))

    tarefas = list(calendario.keys())
    for i, tarefa in enumerate(tarefas):
        inicio, fim = calendario[tarefa]
        duracao = (fim - inicio).days
        ax.barh(i, duracao, left=inicio, color='skyblue')

    ax.set_yticks(range(len(tarefas)))
    ax.set_yticklabels([tarefa.replace('_', ' ').capitalize() for tarefa in tarefas])
    ax.invert_yaxis()
    ax.set_xlabel('Data')
    ax.set_title(f'Cronograma da Obra: {nome_obra} - {morada}')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# === Interface simples ===
print("\n--- Sistema de Gestão de Obras ---")

nome_obra = input("Nome da obra: ")
morada = input("Morada da obra: ")
tipo_obra = input("Tipo de obra (casa de banho, cozinha, etc.): ")
area_m2 = float(input("Área da divisão (m²): "))
data_material = input("Data de chegada dos materiais (YYYY-MM-DD): ")
prazo_final = input("Prazo final para terminação (YYYY-MM-DD): ")

# Converter datas para datetime
data_material = datetime.strptime(data_material, '%Y-%m-%d')
prazo_final = datetime.strptime(prazo_final, '%Y-%m-%d')

# Seleção de tarefas
print("\nIndique as tarefas necessárias (s para sim, n para não):")
tarefas_necessarias = []
for tarefa in task_times.keys():
    resposta = input(f"{tarefa.replace('_', ' ').capitalize()}? (s/n): ").lower()
    if resposta == 's':
        tarefas_necessarias.append(tarefa)

if not tarefas_necessarias:
    print("Nenhuma tarefa selecionada. Programa encerrado.")
    exit()

# Calcular tempos
tempo_total = calcular_tempo_total(area_m2, tarefas_necessarias)

# Agendar
calendario = agendar_tarefas(tempo_total, data_material, tarefas_necessarias)

# Mostrar resultado
imprimir_cronograma(calendario)

desenhar_gantt(calendario, nome_obra, morada)

print("\n--- Fim do Planeamento ---")
