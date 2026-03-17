#pragma once

#include "metaheuristicas.hpp"
#include <vector>
#include <string>
#include <random>
#include <tuple>

// Se já foi definido em outro arquivo, não define novamente
#ifndef ITEM_STRUCT_DEFINED
#define ITEM_STRUCT_DEFINED
struct Item {
    std::string nome;
    int peso;
    int valor;
};
#endif

class TabuSearch : public Metaheuristicas {
private:
    std::vector<Item> itens;
    int capacidade;
    int interacoes;
    int tenencia_tabu;
    int taxa_violacao;
    int seed;

    std::string tipo_solucao_inicial;
    int valor_inicial;
    int tempo_inicial;

    std::vector<int> melhor_solucao;
    int melhor_valor;
    std::vector<int> historico_tabu;
    int tempo_final_tabu;

    std::mt19937 rng;

    // Métodos privados
    std::tuple<int, int, int> avaliarSolucao(const std::vector<int>& solucao);
    std::vector<int> gerarSolucaoInicial();

public:
    TabuSearch() = default;
    
    void solve() override;
    void setParametros(const json &params) override;
    json getResultados() const override;
    std::string getNome() const override { return "Tabu Search"; }
};