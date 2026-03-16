#pragma once

#include "metaheuristicas.hpp"
#include <vector>
#include <string>
#include <algorithm>

#ifndef ITEM_STRUCT_DEFINED
#define ITEM_STRUCT_DEFINED
struct Item {
    std::string nome;
    int peso;
    int valor;
};
#endif

// Estrutura auxiliar interna para o Guloso guardar a densidade e o índice original
struct ItemGuloso {
    int id_original;
    double densidade;
    Item dados;
};

class Greedy : public Metaheuristicas {
private:
    std::vector<ItemGuloso> itens_gulosos;
    int capacidade;
    std::string estrategia; // "valor", "peso" ou "densidade"

    std::vector<int> melhor_solucao;
    int melhor_valor;
    int tempo_final;

public:
    Greedy() = default;
    
    void solve() override;
    void setParametros(const json &params) override;
    json getResultados() const override;
    
    // O nome se adapta dinamicamente para aparecer bonito no Log
    std::string getNome() const override { return "Guloso (" + estrategia + ")"; }
};