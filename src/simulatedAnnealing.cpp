#include "include/simulatedAnnealing.hpp"
#include <algorithm>
#include <iostream>
#include <numeric>
#include <cmath>

void SimulatedAnnealing::setParametros(const json &params) {
    tipo_solucao_inicial = params.value("tipo_solucao_inicial", "aleatoria");
    capacidade = params.value("capacidade", 0);
    interacoes = params.value("interacoes", 1000);
    temperatura_inicial = params.value("temperatura_inicial", 1000.0);
    taxa_resfriamento = params.value("taxa_resfriamento", 0.99);
    seed = params.value("seed", 42);

    rng.seed(seed);
    itens.clear();

    auto json_itens = params["itens"];
    for (auto& [nome_item, atributos] : json_itens.items()) {
        Item novo_item;
        novo_item.nome = nome_item;
        novo_item.peso = atributos["peso"];
        novo_item.valor = atributos["valor"];
        itens.push_back(novo_item);
    }
}

std::tuple<int, int, int> SimulatedAnnealing::avaliarSolucao(const std::vector<int>& solucao) {
    int valor_total = 0;
    int peso_total = 0;

    for (size_t i = 0; i < solucao.size(); ++i) {
        if (solucao[i] == 1) {
            valor_total += itens[i].valor;
            peso_total += itens[i].peso;
        }
    }

    int avaliacao = valor_total;
    if (peso_total > capacidade) {
        int excesso = peso_total - capacidade;
        avaliacao = valor_total - (excesso * 999999);
    }

    return {valor_total, peso_total, avaliacao};
}

/// @brief Método para gerar uma solução inicial baseada no tipo definido
std::vector<int> SimulatedAnnealing::gerarSolucaoInicial() {
    std::vector<int> solucao(itens.size(), 0);

    if (tipo_solucao_inicial == "vazia") return solucao;

    if (tipo_solucao_inicial == "cheia") {
        solucao.assign(itens.size(), 1);
        return solucao;
    }

    std::vector<int> indices(itens.size());
    std::iota(indices.begin(), indices.end(), 0);

    if (tipo_solucao_inicial == "aleatoria") {
        std::shuffle(indices.begin(), indices.end(), rng);
    } 
    
    else if (tipo_solucao_inicial == "valor") {
        std::sort(indices.begin(), indices.end(), [&](int a, int b) {
            if (itens[a].valor == itens[b].valor) return itens[a].peso < itens[b].peso;

            return itens[a].valor > itens[b].valor;
        });
    } 
    
    else if (tipo_solucao_inicial == "peso") {
        std::sort(indices.begin(), indices.end(), [&](int a, int b) {
            if (itens[a].peso == itens[b].peso) return itens[a].valor > itens[b].valor;

            return itens[a].peso < itens[b].peso;
        });
    } 
    
    else if (tipo_solucao_inicial == "densidade") {
        std::sort(indices.begin(), indices.end(), [&](int a, int b) {
            double denA = itens[a].peso > 0 ? (double)itens[a].valor / itens[a].peso : 0.0;
            double denB = itens[b].peso > 0 ? (double)itens[b].valor / itens[b].peso : 0.0;

            if (denA == denB) return itens[a].valor > itens[b].valor;

            return denA > denB;
        });
    }

    // Preenche a mochila respeitando a capacidade
    int peso_atual = 0;

    for(int idx : indices) {
        if(peso_atual + itens[idx].peso <= capacidade) {
            solucao[idx] = 1;
            peso_atual += itens[idx].peso;
        }
    }

    return solucao;
}

void SimulatedAnnealing::solve() {
    historico_sa.clear();
    
    std::vector<int> solucao_atual = gerarSolucaoInicial();
    auto [v_ini, p_ini, aval_atual] = avaliarSolucao(solucao_atual);
    
    valor_inicial = aval_atual;
    tempo_inicial = p_ini;
    
    melhor_solucao = solucao_atual;
    melhor_valor = aval_atual;
    historico_sa.push_back(melhor_valor);

    double temperatura = temperatura_inicial;
    std::uniform_real_distribution<double> dist_prob(0.0, 1.0);
    std::uniform_int_distribution<int> dist_idx(0, itens.size() - 1);

    for (int iteracao = 0; iteracao < interacoes; ++iteracao) {
        // Pega um vizinho aleatório invertendo apenas 1 bit
        int idx = dist_idx(rng);
        std::vector<int> vizinho = solucao_atual;
        vizinho[idx] = 1 - vizinho[idx];
        
        auto [v, p, aval_v] = avaliarSolucao(vizinho);
        int delta = aval_v - aval_atual;

        if (delta > 0) {
            solucao_atual = vizinho;
            aval_atual = aval_v;
            
            if (aval_atual > melhor_valor) {
                melhor_solucao = solucao_atual;
                melhor_valor = aval_atual;
            }
        } else {
            // Aceita solução pior com base na temperatura atual
            double prob = std::exp(delta / temperatura);
            if (dist_prob(rng) < prob) {
                solucao_atual = vizinho;
                aval_atual = aval_v;
            }
        }

        historico_sa.push_back(melhor_valor);
        temperatura *= taxa_resfriamento; // Resfria
    }

    auto [vf, pf, af] = avaliarSolucao(melhor_solucao);
    tempo_final_sa = pf;
}

json SimulatedAnnealing::getResultados() const {
    json res;
    res["valor_inicial"] = valor_inicial;
    res["tempo_inicial"] = tempo_inicial;
    res["melhor_valor"] = melhor_valor;
    // Mantendo a chave "historico_ils" para compatibilidade com o Python
    res["historico_ils"] = historico_sa; 
    res["tempo_final_ils"] = tempo_final_sa;
    
    std::vector<std::string> nomes_selecionados;
    for(size_t i = 0; i < melhor_solucao.size(); ++i) {
        if(melhor_solucao[i] == 1) {
            nomes_selecionados.push_back(itens[i].nome);
        }
    }
    res["itens_selecionados"] = nomes_selecionados;
    
    return res;
}