#include "include/greedy.hpp"
#include <iostream>

void Greedy::setParametros(const json &params) {
    capacidade = params.value("capacidade", 0);
    estrategia = params.value("estrategia", "densidade"); // Padrão é densidade
    
    itens_gulosos.clear();
    
    auto json_itens = params["itens"];
    int id = 0;
    for (auto& [nome_item, atributos] : json_itens.items()) {
        ItemGuloso novo_item;
        novo_item.id_original = id++;
        novo_item.dados.nome = nome_item;
        novo_item.dados.peso = atributos["peso"];
        novo_item.dados.valor = atributos["valor"];
        
        // Calcula a densidade protegendo contra divisão por zero
        if (novo_item.dados.peso > 0) {
            novo_item.densidade = (double)novo_item.dados.valor / novo_item.dados.peso;
        } else {
            novo_item.densidade = 0.0;
        }
        
        itens_gulosos.push_back(novo_item);
    }
}

void Greedy::solve() {
    // Ordena o vetor de acordo com a estratégia
    if (estrategia == "valor") {
        // Maior valor primeiro. Se empatar, menor peso.
        std::sort(itens_gulosos.begin(), itens_gulosos.end(), [](const ItemGuloso& a, const ItemGuloso& b) {
            if (a.dados.valor == b.dados.valor) return a.dados.peso < b.dados.peso;
            return a.dados.valor > b.dados.valor;
        });
    } 
    else if (estrategia == "peso") {
        // Menor peso primeiro. Se empatar, maior valor.
        std::sort(itens_gulosos.begin(), itens_gulosos.end(), [](const ItemGuloso& a, const ItemGuloso& b) {
            if (a.dados.peso == b.dados.peso) return a.dados.valor > b.dados.valor;
            return a.dados.peso < b.dados.peso;
        });
    } 
    else { 
        // Densidade (Padrão) - Maior densidade primeiro
        std::sort(itens_gulosos.begin(), itens_gulosos.end(), [](const ItemGuloso& a, const ItemGuloso& b) {
            if (a.densidade == b.densidade) return a.dados.valor > b.dados.valor;
            return a.densidade > b.densidade;
        });
    }

    // Preenche a mochila
    melhor_solucao.assign(itens_gulosos.size(), 0);
    melhor_valor = 0;
    tempo_final = 0;

    for (const auto& item : itens_gulosos) {
        if (tempo_final + item.dados.peso <= capacidade) {
            melhor_solucao[item.id_original] = 1; // Salva no índice original para manter consistência
            tempo_final += item.dados.peso;
            melhor_valor += item.dados.valor;
        }
    }
}

json Greedy::getResultados() const {
    json res;
    res["melhor_valor"] = melhor_valor;
    res["tempo_final_ils"] = tempo_final; 
    
    // O guloso não tem histórico de iterações, passamos vazio
    res["historico_ils"] = std::vector<int>(); 
    
    return res;
}