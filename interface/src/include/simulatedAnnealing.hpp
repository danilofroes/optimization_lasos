#pragma once

#include "metaheuristicas.hpp"
#include <vector>
#include <string>
#include <random>
#include <tuple>

#ifndef ITEM_STRUCT_DEFINED
#define ITEM_STRUCT_DEFINED
struct Item {
    std::string nome;
    int peso;
    int valor;
};
#endif

class SimulatedAnnealing : public Metaheuristicas {
private:
    std::vector<Item> itens;
    int capacidade;
    int interacoes;
    double temperatura_inicial;
    double taxa_resfriamento;
    int seed;

    std::vector<int> melhor_solucao;
    int melhor_valor;
    std::vector<int> historico_sa;
    int tempo_final_sa;

    std::mt19937 rng;

    // Métodos internos
    std::tuple<int, int, int> avaliarSolucao(const std::vector<int>& solucao);
    std::vector<int> gerarSolucaoAleatoria();

public:
    SimulatedAnnealing() = default;
    
    void solve() override;
    void setParametros(const json &params) override;
    json getResultados() const override;
    std::string getNome() const override { return "Simulated Annealing"; }
};