from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
import random
import math
import matplotlib.pyplot as plt
import numpy as np

class KnapsackProblem(ABC):
    def __init__(self, itens: Dict[str, Dict[str, int]], capacidade: int, seed: int = 42, str_peso: str = "peso", str_valor: str = "valor"):
        random.seed(seed)

        for item in itens:
            peso = itens[item][str_peso]
            valor = itens[item][str_valor]
            densidade = valor / peso if peso > 0 else 0
            itens[item]["densidade"] = densidade

        self.itens = itens
        self.capacidade = capacidade
        self.nomes_itens = list(itens.keys())

        # self.pesos = [item[str_peso] for item in itens.values()]
        # self.valores = [item[str_valor] for item in itens.values()]
        # self.densidades = [valor / peso if peso > 0 else 0 
        #                    for valor, peso in zip(self.valores, self.pesos)]

        self.n_itens = len(self.nomes_itens)

        self.melhor_solucao = [0] * self.n_itens 
        self.melhor_valor = -float('inf')

        self.str_peso = str_peso
        self.str_valor = str_valor 

        self.resultados_gulosos = {}

    def solucao_gulosa(self, tipo_solucao: str, isDesensidade: bool = False):
        total = 0
        soma_valores = 0

        if tipo_solucao == self.str_peso or tipo_solucao == "peso":
            itens_ordenados = sorted(self.itens.items(), key=lambda x: (x[1][self.str_peso], x[1][self.str_valor]))
            nome_metodo = "Guloso (Tempo)"

        elif tipo_solucao == self.str_valor or tipo_solucao == "valor":
            itens_ordenados = sorted(self.itens.items(), key=lambda x: (x[1][self.str_valor], -x[1][self.str_peso]), reverse=True)
            nome_metodo = "Guloso (Lucro)"

        elif tipo_solucao == "densidade":
            itens_ordenados = sorted(self.itens.items(), key=lambda x: (x[1]["densidade"], x[1][self.str_valor]), reverse=True)
            nome_metodo = "Guloso (Densidade)"

        else:
            print("Tipo inválido")
            return

        while total < self.capacidade:
            for item in itens_ordenados:
                nome_item = item[0]
                peso_item = item[1][self.str_peso]
                valor_item = item[1][self.str_valor]
                densidade_item = round(item[1]["densidade"], 2) if isDesensidade else None

                if total + peso_item <= self.capacidade:
                    total += peso_item
                    soma_valores += valor_item
                    print(f'Adicionando {nome_item} ({self.str_peso}: {peso_item} | {self.str_valor}: {valor_item}', end='')
                    print(f' | densidade: {densidade_item}' if isDesensidade else '', end='')
                    print(f') | Total atual: {total}', end='\n\n')
            break

        self.resultados_gulosos[nome_metodo] = {
            "valor": soma_valores,
            "peso": total,
            "ocupacao": (total / self.capacidade) * 100
        }

        print(f'[{nome_metodo}] Valor Final: {soma_valores} | Peso Usado: {total}')

        return soma_valores, total

    def get_solucao(self, tipo_solucao: str = "aleatoria") -> List[int]:
        '''Gera uma solução inicial baseada no tipo especificado'''
        if tipo_solucao == "aleatoria":
            return [random.choice([0, 1]) for _ in range(len(self.itens))]
        
        elif tipo_solucao == "vazia":
            return [0] * len(self.nomes_itens)
        
        elif tipo_solucao == "cheia":
            return [1] * len(self.nomes_itens)
        
        elif tipo_solucao in ["peso", "valor", "densidade", self.str_peso, self.str_valor]:
            solucao = [0] * self.n_itens
            peso_atual = 0

            if tipo_solucao == self.str_peso or tipo_solucao == "peso":
                nomes_ordenados = sorted(self.itens.items(), key=lambda x: (x[1][self.str_peso], x[1][self.str_valor]))
            
            elif tipo_solucao == self.str_valor or tipo_solucao == "valor":
                nomes_ordenados = sorted(self.itens.items(), key=lambda x: (x[1][self.str_valor], -x[1][self.str_peso]), reverse=True)
            
            elif tipo_solucao == "densidade":
                nomes_ordenados = sorted(self.itens.items(), key=lambda x: (x[1]["densidade"], x[1][self.str_valor]), reverse=True)

            for nome, _ in nomes_ordenados:
                idx = self.nomes_itens.index(nome)

                peso_item = self.itens[nome][self.str_peso]

                if peso_atual + peso_item <= self.capacidade:
                    solucao[idx] = 1
                    peso_atual += peso_item

            return solucao

        else:
            raise ValueError(f"Tipo de solução '{tipo_solucao}' desconhecido")

    def desbinarizar_solucao(self, solucao: List[int]) -> List[str]:
        '''Converte a solução binária [1, 0...] para nomes de itens'''
        return [self.nomes_itens[i] for i, bit in enumerate(solucao) if bit == 1]
    
    def avaliar_solucao(self, solucao: List[int], taxa_violacao: int = 20) -> Tuple[int, int, int]:
        '''Avalia a solução retornando valor total, peso total e valor penalizado'''
        valor_total = 0
        peso_total = 0

        for i, bit in enumerate(solucao):
            if bit == 1:
                item = list(self.itens.values())[i]
                valor_total += item[self.str_valor]
                peso_total += item[self.str_peso]

        if peso_total > self.capacidade:
            excecao = peso_total - self.capacidade
            avaliacao = valor_total - (excecao * taxa_violacao)

        else:
            avaliacao = valor_total

        return valor_total, peso_total, avaliacao
    
class ILS(KnapsackProblem):
    def __init__(self, itens: Dict[str, Dict[str, int]], capacidade: int, 
                 interacoes: int = 1000, 
                 nivel_perturbacao: int = 1, 
                 taxa_violacao: int = 20,
                 limite_sem_melhora: int = 50,
                 seed: int = 42,
                 str_peso: str = "peso", 
                 str_valor: str = "valor"):
        
        super().__init__(itens, capacidade, seed, str_peso, str_valor)

        self.interacoes = interacoes
        self.nivel_perturbacao = nivel_perturbacao
        self.taxa_violacao = taxa_violacao
        self.limite_sem_melhora = limite_sem_melhora

        self.str_peso = str_peso
        self.str_valor = str_valor

        self.historico_ils = []
        self.tempo_final_ils = 0

    def perturbar_solucao(self, solucao: List[int]) -> List[int]:
        nova_solucao = solucao[:]
        
        indices_um = [i for i, x in enumerate(solucao) if x == 1]
        indices_zero = [i for i, x in enumerate(solucao) if x == 0]
        
        qnt_remover = min(len(indices_um), self.nivel_perturbacao // 2)
        qnt_adicionar = self.nivel_perturbacao - qnt_remover
        
        indices_para_inverter = []
        
        if indices_um:
            indices_para_inverter.extend(random.sample(indices_um, qnt_remover))
        
        if indices_zero:
            indices_para_inverter.extend(random.sample(indices_zero, qnt_adicionar))
            
        if not indices_para_inverter:
             indices_para_inverter = random.sample(range(self.n_itens), self.nivel_perturbacao)

        for idx in indices_para_inverter:
            nova_solucao[idx] = 1 - nova_solucao[idx]

        return nova_solucao

    def busca_local(self, solucao_inicial: List[int]) -> Tuple[List[int], int]:
        solucao_atual = solucao_inicial[:] 
        _, _, aval_atual = self.avaliar_solucao(solucao_atual, self.taxa_violacao)
        
        melhor_vizinho = None
        aval_vizinho = -float('inf')

        for i in range(self.n_itens):
            vizinho = solucao_atual[:]
            vizinho[i] = 1 - vizinho[i]
            _, _, aval = self.avaliar_solucao(vizinho, self.taxa_violacao)

            if aval > aval_vizinho:
                aval_vizinho = aval
                melhor_vizinho = vizinho[:]

        if aval_vizinho > aval_atual:
            print(f"[Busca Local] 1 passo realizado: {aval_atual} -> {aval_vizinho}", end="\n\n")
            return melhor_vizinho, aval_vizinho

        print(f"[Busca Local] Nenhuma melhora. Avaliação: {aval_atual}", end="\n\n")

        return solucao_atual, aval_atual
    
    def executar_ils(self, tipo_solucao_inicial: str = "aleatoria") -> Tuple[List[int], int]:
        print(f"--- Iniciando ILS (Capacidade: {self.capacidade}) ---")

        self.historico_ils = []

        solucao_atual = self.get_solucao(tipo_solucao_inicial)
        _, _, aval_inicial = self.avaliar_solucao(solucao_atual, self.taxa_violacao)
        print(f"Solução Inicial Gerada: {aval_inicial}", end="\n\n")

        solucao_atual, aval_atual = self.busca_local(solucao_atual)

        self.melhor_solucao = solucao_atual[:]
        self.melhor_valor = aval_atual

        self.historico_ils.append(self.melhor_valor)

        print(f"Solução Inicial (pós busca local): {aval_atual}")

        contador_sem_melhora = 0

        for i in range(self.interacoes):
            solucao_perturbada = self.perturbar_solucao(solucao_atual)
            solucao_candidata, aval_candidata = self.busca_local(solucao_perturbada)

            if aval_candidata > aval_atual:
                solucao_atual = solucao_candidata[:]
                aval_atual = aval_candidata

            if aval_candidata > self.melhor_valor:
                self.melhor_solucao = solucao_candidata[:]
                self.melhor_valor = aval_candidata
                print(f"Iteração {i}: NOVO RECORDE -> {self.melhor_valor}", end="\n\n")
                contador_sem_melhora = 0

            else:
                contador_sem_melhora += 1

            self.historico_ils.append(self.melhor_valor)

            if contador_sem_melhora >= self.limite_sem_melhora:
                print(f"\n[PARADA] O algoritmo estagnou por {self.limite_sem_melhora} iterações e parou na iteração {i}.")
                restante = self.interacoes - 1 - i
                self.historico_ils.extend([self.melhor_valor] * restante)
                break

        print(f"\nFim do ILS. Melhor valor encontrado: {self.melhor_valor}")

        _, peso_final, _ = self.avaliar_solucao(self.melhor_solucao, self.taxa_violacao)
        self.tempo_final_ils = peso_final

        return self.melhor_solucao, self.melhor_valor
    
    def plotar_convergencia(self):
        """Plota a curva de evolução do ILS após a execução"""
        if not self.historico_ils:
            print("Erro: Execute o ILS primeiro.")
            return
        
        plt.figure(figsize=(10, 5))
        plt.plot(self.historico_ils, label='Melhor Solução Global', color='#2980b9', linewidth=2)
        plt.title('Curva de Convergência (ILS)', fontsize=14)
        plt.xlabel('Iterações', fontsize=12)
        plt.ylabel('Valor da Função Objetivo (Lucro)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.show()

    def plotar_comparativo_lucro(self):
        """Compara o lucro do ILS com os gulosos salvos"""
        metodos = list(self.resultados_gulosos.keys()) + ["Metaheurística (ILS)"]
        lucros = [d['valor'] for d in self.resultados_gulosos.values()] + [self.melhor_valor]
        
        plt.figure(figsize=(10, 5))
        barras = plt.bar(metodos, lucros, color=['gray']*len(self.resultados_gulosos) + ['#27ae60'])
        
        plt.title('Comparativo de Lucro Total', fontsize=14)
        plt.ylabel('Lucro (R$)', fontsize=12)
        
        for barra in barras:
            altura = barra.get_height()
            plt.text(barra.get_x() + barra.get_width()/2., altura,
                     f'{int(altura)}', ha='center', va='bottom', fontweight='bold')
        
        plt.ylim(0, max(lucros) * 1.15)
        plt.show()

    def plotar_eficiencia_tempo(self):
        """Compara o tempo utilizado vs capacidade"""
        metodos = list(self.resultados_gulosos.keys()) + ["Metaheurística (ILS)"]
        tempos = [d['peso'] for d in self.resultados_gulosos.values()] + [self.tempo_final_ils]
        
        plt.figure(figsize=(10, 5))
        plt.bar(metodos, tempos, color='#3498db', width=0.5)
        plt.axhline(y=self.capacidade, color='red', linestyle='--', label=f'Turno ({self.capacidade} min)')
        
        plt.title('Eficiência de Ocupação do Turno', fontsize=14)
        plt.ylabel('Tempo Utilizado (min)', fontsize=12)
        plt.legend()
        
        for i, tempo in enumerate(tempos):
            pct = (tempo / self.capacidade) * 100
            plt.text(i, tempo + 5, f'{pct:.1f}%', ha='center', fontweight='bold')
            
        plt.ylim(0, max(max(tempos), self.capacidade) * 1.15)
        plt.show()
    
class TabuSearch(KnapsackProblem):
    def __init__(self, itens: Dict[str, Dict[str, int]], capacidade: int, 
                 interacoes: int = 100, 
                 tenencia_tabu: int = 5, 
                 taxa_violacao: int = 20,
                 seed: int = 42,
                 str_peso: str = "peso", 
                 str_valor: str = "valor"):
        
        super().__init__(itens, capacidade, seed, str_peso, str_valor)

        self.interacoes = interacoes
        self.tenencia_tabu = tenencia_tabu
        self.taxa_violacao = taxa_violacao
        
        self.str_peso = str_peso
        self.str_valor = str_valor

        self.historico_tabu = []
        self.tempo_final_tabu = 0

    def executar_tabu(self, tipo_solucao_inicial: str = "aleatoria") -> Tuple[List[int], int]:
        print(f"--- Iniciando Busca Tabu (Tenência: {self.tenencia_tabu}, Capacidade: {self.capacidade}) ---")

        self.historico_tabu = []
        
        solucao_atual = self.get_solucao(tipo_solucao_inicial)
        _, _, aval_atual = self.avaliar_solucao(solucao_atual, self.taxa_violacao)
        
        self.melhor_solucao = solucao_atual[:]
        self.melhor_valor = aval_atual
        
        lista_tabu = {}
        
        self.historico_tabu.append(self.melhor_valor)
        print(f"Solução Inicial: {aval_atual}")

        for iteracao in range(self.interacoes):
            melhor_vizinho_iter = None
            melhor_aval_vizinho_iter = -float('inf')
            movimento_realizado = -1

            for i in range(self.n_itens):
                vizinho = solucao_atual[:]
                vizinho[i] = 1 - vizinho[i]
                
                _, _, aval_v = self.avaliar_solucao(vizinho, self.taxa_violacao)

                eh_tabu = (i in lista_tabu) and (lista_tabu[i] > iteracao)
                
                aspiracao = eh_tabu and (aval_v > self.melhor_valor)

                if (not eh_tabu or aspiracao):
                    if aval_v > melhor_aval_vizinho_iter:
                        melhor_vizinho_iter = vizinho[:]
                        melhor_aval_vizinho_iter = aval_v
                        movimento_realizado = i

            if melhor_vizinho_iter is not None:
                solucao_atual = melhor_vizinho_iter[:]
                aval_atual = melhor_aval_vizinho_iter
                
                lista_tabu[movimento_realizado] = iteracao + self.tenencia_tabu

                if aval_atual > self.melhor_valor:
                    self.melhor_solucao = solucao_atual[:]
                    self.melhor_valor = aval_atual
                    print(f"Iteração {iteracao}: NOVO RECORDE -> {self.melhor_valor} (Movimento no item {movimento_realizado})")
            
            self.historico_tabu.append(self.melhor_valor)

        print(f"\nFim da Busca Tabu. Melhor valor encontrado: {self.melhor_valor}")

        _, peso_final, _ = self.avaliar_solucao(self.melhor_solucao, self.taxa_violacao)
        self.tempo_final_tabu = peso_final

        return self.melhor_solucao, self.melhor_valor

    def plotar_convergencia(self):
        """Plota a curva de evolução da Busca Tabu"""
        if not self.historico_tabu:
            print("Erro: Execute a Busca Tabu primeiro.")
            return
        
        plt.figure(figsize=(10, 5))
        plt.plot(self.historico_tabu, label='Melhor Solução Global', color='#8e44ad', linewidth=2)
        plt.title(f'Curva de Convergência (Busca Tabu - Tenência {self.tenencia_tabu})', fontsize=14)
        plt.xlabel('Iterações', fontsize=12)
        plt.ylabel('Valor da Função Objetivo', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.show()

    def plotar_comparativo_lucro(self):
        """Compara o lucro da Tabu com os gulosos salvos"""
        metodos = list(self.resultados_gulosos.keys()) + ["Metaheurística (Tabu)"]
        lucros = [d['valor'] for d in self.resultados_gulosos.values()] + [self.melhor_valor]
        
        plt.figure(figsize=(10, 5))
        barras = plt.bar(metodos, lucros, color=['gray']*len(self.resultados_gulosos) + ['#9b59b6'])
        
        plt.title('Comparativo de Lucro Total', fontsize=14)
        plt.ylabel('Lucro (R$)', fontsize=12)
        
        for barra in barras:
            altura = barra.get_height()
            plt.text(barra.get_x() + barra.get_width()/2., altura,
                     f'{int(altura)}', ha='center', va='bottom', fontweight='bold')
        
        plt.ylim(0, max(lucros) * 1.15)
        plt.show()

    def plotar_eficiencia_tempo(self):
        """Compara o tempo utilizado vs capacidade"""
        metodos = list(self.resultados_gulosos.keys()) + ["Metaheurística (Tabu)"]
        tempos = [d['peso'] for d in self.resultados_gulosos.values()] + [self.tempo_final_tabu]
        
        plt.figure(figsize=(10, 5))
        plt.bar(metodos, tempos, color='#3498db', width=0.5)
        plt.axhline(y=self.capacidade, color='red', linestyle='--', label=f'Turno ({self.capacidade} min)')
        
        plt.title('Eficiência de Ocupação do Turno', fontsize=14)
        plt.ylabel('Tempo Utilizado (min)', fontsize=12)
        plt.legend()
        
        for i, tempo in enumerate(tempos):
            pct = (tempo / self.capacidade) * 100
            plt.text(i, tempo + 5, f'{pct:.1f}%', ha='center', fontweight='bold')
            
        plt.ylim(0, max(max(tempos), self.capacidade) * 1.15)
        plt.show()

class SimulatedAnnealing(KnapsackProblem):
    def __init__(self, itens: Dict[str, Dict[str, int]], capacidade: int, 
                 temp_inicial: float = 1000.0,
                 temp_final: float = 1.0,
                 resfriamento: float = 0.95,
                 iteracoes_por_temp: int = 50,
                 taxa_violacao: int = 20,
                 seed: int = 42,
                 str_peso: str = "peso", 
                 str_valor: str = "valor"):
        
        super().__init__(itens, capacidade, seed, str_peso, str_valor)

        self.temp_inicial = temp_inicial
        self.temp_final = temp_final
        self.resfriamento = resfriamento
        self.iteracoes_por_temp = iteracoes_por_temp
        self.taxa_violacao = taxa_violacao
        
        self.historico_sa = []
        self.tempo_final_sa = 0

    def executar_sa(self, tipo_solucao_inicial: str = "aleatoria") -> Tuple[List[int], int]:
        print(f"--- Iniciando Simulated Annealing (T_ini: {self.temp_inicial}, Alpha: {self.resfriamento}) ---")
        
        solucao_atual = self.get_solucao(tipo_solucao_inicial)
        _, _, aval_atual = self.avaliar_solucao(solucao_atual, self.taxa_violacao)
        
        self.melhor_solucao = solucao_atual[:]
        self.melhor_valor = aval_atual
        
        self.historico_sa = [self.melhor_valor]
        
        temperatura = self.temp_inicial
        iteracao_total = 0

        while temperatura > self.temp_final:
            for _ in range(self.iteracoes_por_temp):
                idx = random.randint(0, self.n_itens - 1)
                vizinho = solucao_atual[:]
                vizinho[idx] = 1 - vizinho[idx]
                
                _, _, aval_vizinho = self.avaliar_solucao(vizinho, self.taxa_violacao)

                delta = aval_vizinho - aval_atual

                if delta > 0:
                    aceitar = True
                else:
                    probabilidade = math.exp(delta / temperatura)
                    aceitar = random.random() < probabilidade

                if aceitar:
                    solucao_atual = vizinho[:]
                    aval_atual = aval_vizinho
                    
                    if aval_atual > self.melhor_valor:
                        self.melhor_solucao = solucao_atual[:]
                        self.melhor_valor = aval_atual

                iteracao_total += 1
                self.historico_sa.append(self.melhor_valor)

            temperatura *= self.resfriamento
        
        print(f"Fim do SA. Melhor valor encontrado: {self.melhor_valor} | Temp Final: {temperatura:.2f}")

        _, peso_final, _ = self.avaliar_solucao(self.melhor_solucao, self.taxa_violacao)
        self.tempo_final_sa = peso_final

        return self.melhor_solucao, self.melhor_valor

    def plotar_convergencia(self):
        """Plota a curva de evolução do SA"""
        if not self.historico_sa:
            print("Erro: Execute o SA primeiro.")
            return
        
        plt.figure(figsize=(10, 5))
        plt.plot(self.historico_sa, label='Melhor Solução Global', color='#e67e22', linewidth=2)
        plt.title('Curva de Convergência (Simulated Annealing)', fontsize=14)
        plt.xlabel('Iterações Totais', fontsize=12)
        plt.ylabel('Valor da Função Objetivo', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.show()

class ComparadorResultados:
    def __init__(self, capacidade: int):
        self.capacidade = capacidade
        self.resultados = {}
        self.tempos_ocupacao = {}
        self.gulosos_adicionados = False

    def adicionar_gulosos(self, objeto_instancia):
        """Pega os resultados gulosos já calculados de uma das instâncias"""
        if not self.gulosos_adicionados and objeto_instancia.resultados_gulosos:
            for nome, dados in objeto_instancia.resultados_gulosos.items():
                self.resultados[nome] = dados['valor']
                self.tempos_ocupacao[nome] = dados['peso']
            self.gulosos_adicionados = True

    def adicionar_metaheuristica(self, nome: str, valor_final: int, tempo_final: int):
        """Adiciona manualmente o resultado de uma metaheurística (ILS, Tabu, SA)"""
        self.resultados[nome] = valor_final
        self.tempos_ocupacao[nome] = tempo_final

    def plotar_comparativo_geral_lucro(self):
        plt.figure(figsize=(12, 6))
        
        cores = []
        for nome in self.resultados:
            if "Guloso" in nome:
                cores.append("gray")
            elif "ILS" in nome:
                cores.append("#27ae60")
            elif "Tabu" in nome:
                cores.append("#8e44ad")
            elif "Annealing" in nome:
                cores.append("#e67e22")
            else:
                cores.append("#3498db")

        barras = plt.bar(list(self.resultados.keys()), list(self.resultados.values()), color=cores)
        
        plt.title('Comparativo GLOBAL de Lucro', fontsize=16)
        plt.ylabel('Lucro Total', fontsize=12)
        plt.xticks(rotation=15)
        
        for barra in barras:
            altura = barra.get_height()
            plt.text(barra.get_x() + barra.get_width()/2., altura,
                     f'{int(altura)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.show()

    def plotar_comparativo_geral_tempo(self):
        plt.figure(figsize=(12, 6))
        
        nomes = list(self.tempos_ocupacao.keys())
        valores = list(self.tempos_ocupacao.values())
        
        plt.bar(nomes, valores, color='#34495e', alpha=0.9)
        plt.axhline(y=self.capacidade, color='red', linestyle='--', linewidth=2, label=f'Limite ({self.capacidade})')
        
        plt.title('Comparativo GLOBAL de Ocupação', fontsize=16)
        plt.ylabel('Tempo Utilizado', fontsize=12)
        plt.xticks(rotation=15)
        plt.legend()
        
        for i, tempo in enumerate(valores):
            pct = (tempo / self.capacidade) * 100
            cor_texto = 'red' if tempo > self.capacidade else 'black'
            plt.text(i, tempo + (self.capacidade * 0.02), f'{pct:.1f}%', 
                     ha='center', fontweight='bold', color=cor_texto)
            
        plt.tight_layout()
        plt.show()