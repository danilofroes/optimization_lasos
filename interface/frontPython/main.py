import sys
import os
import numpy as np

# Importando o módulo C++
dir_atual = os.path.dirname(os.path.abspath(__file__))
caminho_build = os.path.abspath(os.path.join(dir_atual, "..", "build", "Release"))
sys.path.append(caminho_build)

try:
    import meta_engine
except ImportError as e:
    print(f"X Erro ao importar o módulo C++: {e}")
    sys.exit(1)

# Importações da Interface Gráfica (PyQt6)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QFormLayout, QLineEdit, QPushButton, 
                               QTextEdit, QLabel, QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt

import matplotlib
matplotlib.use('QtAgg') # Forçando o Matplotlib a usar o Qt correto
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# Função para gerar instâncias de produção aleatórias
def get_dict_producao(qntd_itens: int, tempo_max: int, lucro_max: int, seed: int = 42) -> dict:
    np.random.seed(seed) # Usamos a seed aqui para garantir a mesma instância sempre
    dict_producao = {}
    for i in range(1, qntd_itens + 1):
        dict_producao[f'OP_{i:03d}'] = {
            'peso': int(np.random.randint(5, tempo_max)),
            'valor': int(np.random.randint(1000, lucro_max))
        }
    return dict_producao

# Interface Gráfica Principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Otimizador com Metaheurísticas - LASOS")
        self.resize(1100, 750)

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)

        # Painel esquerdo para parâmetros e log
        painel_esquerdo = QWidget()
        layout_esq = QVBoxLayout(painel_esquerdo)
        layout_esq.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Seleção de algoritmos a executar
        grupo_algoritmos = QGroupBox("Algoritmos a Executar")
        layout_algos = QVBoxLayout()
        
        # Checkboxes Meta-heurísticas
        self.cb_ils = QCheckBox("Iterated Local Search (ILS)")
        self.cb_tabu = QCheckBox("Tabu Search (TS)")
        self.cb_sa = QCheckBox("Simulated Annealing (SA)")
        self.cb_ils.setChecked(True)
        self.cb_tabu.setChecked(True)
        self.cb_sa.setChecked(True)
        
        # Checkboxes Gulosos (Baselines)
        self.cb_guloso_valor = QCheckBox("Guloso (Por Valor)")
        self.cb_guloso_peso = QCheckBox("Guloso (Por Menor Peso)")
        self.cb_guloso_densidade = QCheckBox("Guloso (Por Densidade)")
        self.cb_guloso_densidade.setChecked(True) # Densidade costuma ser o melhor baseline por isso já fica marcado

        layout_algos.addWidget(self.cb_ils)
        layout_algos.addWidget(self.cb_tabu)
        layout_algos.addWidget(self.cb_sa)
        layout_algos.addWidget(QLabel("<i>Baselines:</i>")) # Separador visual
        layout_algos.addWidget(self.cb_guloso_valor)
        layout_algos.addWidget(self.cb_guloso_peso)
        layout_algos.addWidget(self.cb_guloso_densidade)
        
        grupo_algoritmos.setLayout(layout_algos)
        layout_esq.addWidget(grupo_algoritmos)

        # Dados gerais da instância
        grupo_instancia = QGroupBox("Parâmetros do Problema (Instância)")
        form_instancia = QFormLayout()
        self.in_qntd = QLineEdit("500")
        self.in_capacidade = QLineEdit("480")
        self.in_taxa_violacao = QLineEdit("2000")
        self.in_seed = QLineEdit("42")
        form_instancia.addRow("Qtd. de Ordens:", self.in_qntd)
        form_instancia.addRow("Capacidade (Turno):", self.in_capacidade)
        form_instancia.addRow("Multa por Violação:", self.in_taxa_violacao)
        form_instancia.addRow("Semente (Seed):", self.in_seed)
        grupo_instancia.setLayout(form_instancia)
        layout_esq.addWidget(grupo_instancia)

        # Parâmetros específicos dos algoritmos
        grupo_params = QGroupBox("Ajuste Fino das Metaheurísticas")
        form_params = QFormLayout()
        self.in_iteracoes = QLineEdit("1000")
        self.in_perturbacao = QLineEdit("5")
        self.in_tenencia = QLineEdit("10")
        self.in_limite_sem_melhora = QLineEdit("100")
        self.in_temp_inicial = QLineEdit("1000.0")
        self.in_resfriamento = QLineEdit("0.99")
        
        form_params.addRow("Iterações Totais:", self.in_iteracoes)
        form_params.addRow("ILS - Nível de Perturbação:", self.in_perturbacao)
        form_params.addRow("ILS - Limite de Estagnação:", self.in_limite_sem_melhora)
        form_params.addRow("TABU - Tenência (Memória):", self.in_tenencia)
        form_params.addRow("SA - Temp. Inicial:", self.in_temp_inicial)
        form_params.addRow("SA - Taxa Resfriamento:", self.in_resfriamento)
        grupo_params.setLayout(form_params)
        layout_esq.addWidget(grupo_params)

        # Botão para rodar os algoritmos
        self.btn_rodar = QPushButton("▶ Executar Algoritmos")
        self.btn_rodar.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 12px; font-size: 14px;")
        self.btn_rodar.clicked.connect(self.rodar_otimizacao)
        layout_esq.addWidget(self.btn_rodar)

        # Caixa de log para mostrar mensagens e resultados
        self.caixa_log = QTextEdit()
        self.caixa_log.setReadOnly(True)
        self.caixa_log.setStyleSheet("background-color: #f8f9fa; font-family: Consolas, monospace;")
        layout_esq.addWidget(self.caixa_log)

        # Painel direito para visualização gráfica
        painel_direito = QWidget()
        layout_dir = QVBoxLayout(painel_direito)

        self.figura, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas = FigureCanvas(self.figura)
        layout_dir.addWidget(self.canvas)

        layout_principal.addWidget(painel_esquerdo, 3)
        layout_principal.addWidget(painel_direito, 5)

    def log(self, mensagem):
        self.caixa_log.append(mensagem)
        QApplication.processEvents() 

    def executar_guloso(self, config_base, estrategia, label, cor):
        """Função auxiliar para rodar e plotar os gulosos sem repetir código"""
        self.log(f"\nIniciando {label}...")
        config_guloso = config_base.copy()
        config_guloso["estrategia"] = estrategia

        guloso = meta_engine.Greedy()
        guloso.setParametros(config_guloso)
        guloso.solve()

        res = guloso.getResultados()
        lucro = res.get('melhor_valor')
        self.log(f"   ↳ Lucro Máximo: R$ {lucro}")
        self.log(f"   ↳ Tempo: {res.get('tempo_final_ils')}/{config_base['capacidade']} min")
        
        # Desenha uma linha tracejada horizontal para a baseline
        self.ax.axhline(y=lucro, color=cor, linestyle='--', alpha=0.8, label=label)
        return True

    def rodar_otimizacao(self):
        self.caixa_log.clear()
        self.ax.clear()
        
        qntd = int(self.in_qntd.text())
        capacidade = int(self.in_capacidade.text())
        taxa_violacao = int(self.in_taxa_violacao.text())
        seed = int(self.in_seed.text())
        iteracoes = int(self.in_iteracoes.text())

        self.log(f"Gerando {qntd} ordens de produção (Seed: {seed})...")
        ordens_producao = get_dict_producao(qntd, tempo_max=90, lucro_max=5000, seed=seed)

        config_base = {
            "itens": ordens_producao,
            "capacidade": capacidade,
            "interacoes": iteracoes,
            "taxa_violacao": taxa_violacao,
            "seed": seed
        }

        rodou_alguma = False

        # Execução dos algoritmos gulosos (baselines)
        if self.cb_guloso_valor.isChecked():
            rodou_alguma = self.executar_guloso(config_base, "valor", "Guloso (Valor)", "green")
            
        if self.cb_guloso_peso.isChecked():
            rodou_alguma = self.executar_guloso(config_base, "peso", "Guloso (Peso)", "blue")
            
        if self.cb_guloso_densidade.isChecked():
            rodou_alguma = self.executar_guloso(config_base, "densidade", "Guloso (Densidade)", "black")

        # Execução do ILS
        if self.cb_ils.isChecked():
            self.log("\nIniciando Iterated Local Search (ILS)...")
            config_ils = config_base.copy()
            config_ils["nivel_perturbacao"] = int(self.in_perturbacao.text())
            config_ils["limite_sem_melhora"] = int(self.in_limite_sem_melhora.text())

            ils = meta_engine.ILS()
            ils.setParametros(config_ils)
            ils.solve()

            res_ils = ils.getResultados()
            self.log(f"   ↳ Lucro Máximo: R$ {res_ils.get('melhor_valor')}")
            self.log(f"   ↳ Tempo: {res_ils.get('tempo_final_ils')}/{capacidade} min")
            
            hist_ils = res_ils.get("historico_ils", [])
            self.ax.plot(hist_ils, label='ILS', color="#352f8b", linewidth=2)
            rodou_alguma = True

        # Execução do Tabu Search
        if self.cb_tabu.isChecked():
            self.log("\nIniciando Tabu Search...")
            config_tabu = config_base.copy()
            config_tabu["tenencia_tabu"] = int(self.in_tenencia.text())

            tabu = meta_engine.TabuSearch()
            tabu.setParametros(config_tabu)
            tabu.solve()

            res_tabu = tabu.getResultados()
            self.log(f"   ↳ Lucro Máximo: R$ {res_tabu.get('melhor_valor')}")
            self.log(f"   ↳ Tempo: {res_tabu.get('tempo_final_ils')}/{capacidade} min")
            
            hist_tabu = res_tabu.get("historico_ils", [])
            self.ax.plot(hist_tabu, label='Tabu Search', color="#ff0000", linewidth=2)
            rodou_alguma = True

        # Execução do Simulated Annealing
        if self.cb_sa.isChecked():
            self.log("\nIniciando Simulated Annealing (SA)...")
            config_sa = config_base.copy()
            config_sa["temperatura_inicial"] = float(self.in_temp_inicial.text())
            config_sa["taxa_resfriamento"] = float(self.in_resfriamento.text())

            sa = meta_engine.SimulatedAnnealing()
            sa.setParametros(config_sa)
            sa.solve()

            res_sa = sa.getResultados()
            self.log(f"   ↳ Lucro Máximo: R$ {res_sa.get('melhor_valor')}")
            self.log(f"   ↳ Tempo: {res_sa.get('tempo_final_ils')}/{capacidade} min")
            
            hist_sa = res_sa.get("historico_ils", [])
            self.ax.plot(hist_sa, label='SA', color="#CC720B", linewidth=2)
            rodou_alguma = True

        if rodou_alguma:
            self.log("\n✅ Execução Concluída!")
            self.ax.set_title('Comparativo de Convergência', fontsize=14, fontweight='bold')
            self.ax.set_xlabel('Iterações', fontsize=11)
            self.ax.set_ylabel('Lucro Global Encontrado (R$)', fontsize=11)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.legend(loc="lower right")
            self.canvas.draw()
        else:
            self.log("\n⚠️ Nenhum algoritmo foi selecionado para rodar.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec())