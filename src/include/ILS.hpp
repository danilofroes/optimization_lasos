#pragma once

#include "metaheuristicas.hpp"

#include <vector>
#include <string>
#include <random>
#include <tuple>
#include <ctype.h>

// Estrutura auxiliar para guardar os dados de cada item
#ifndef ITEM_STRUCT_DEFINED
#define ITEM_STRUCT_DEFINED
struct Item {
    std::string nome;
    int peso;
    int valor;
};
#endif

class ILS : public Metaheuristicas {
private:
    std::vector<Item> itens;
    int capacidade;
    int interacoes;
    int nivel_perturbacao;
    int taxa_violacao;
    int limite_sem_melhora;
    int seed;

    std::string tipo_solucao_inicial;
    int valor_inicial;
    int tempo_inicial;

    std::vector<int> melhor_solucao;
    int melhor_valor;
    std::vector<int> historico_ils;
    int tempo_final_ils; // O peso da melhor solução

    std::mt19937 rng; // Gerador de números aleatórios de alta performance do C++

    // Métodos privados
    std::tuple<int, int, int> avaliarSolucao(const std::vector<int>& solucao);
    std::vector<int> gerarSolucaoInicial();
    std::vector<int> perturbarSolucao(const std::vector<int>& solucao);
    std::pair<std::vector<int>, int> buscaLocal(const std::vector<int>& solucao_inicial);

public:
    ILS() = default;
    
    // Métodos obrigatórios da classe abstrata
    void solve() override;
    void setParametros(const json &params) override;
    json getResultados() const override;
    std::string getNome() const override { return "ILS"; }
};