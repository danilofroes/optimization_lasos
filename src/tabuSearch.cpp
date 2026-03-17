#include "include/tabuSearch.hpp"
#include <algorithm>
#include <iostream>
#include <numeric>

void TabuSearch::setParametros(const json &params) {
    tipo_solucao_inicial = params.value("tipo_solucao_inicial", "aleatoria");
    capacidade = params.value("capacidade", 0);
    interacoes = params.value("interacoes", 100);
    tenencia_tabu = params.value("tenencia_tabu", 5);
    taxa_violacao = params.value("taxa_violacao", 20);
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

/// @brief Avalia uma solução, retornando {valor_total, peso_total, avaliacao_penalizada}
std::tuple<int, int, int> TabuSearch::avaliarSolucao(const std::vector<int>& solucao) {
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
        avaliacao = valor_total - (excesso * taxa_violacao);
    }

    return {valor_total, peso_total, avaliacao};
}

/// @brief Método para gerar uma solução inicial baseada no tipo definido
std::vector<int> TabuSearch::gerarSolucaoInicial() {
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

/// @brief Método para executar o algoritmo Tabu Search
void TabuSearch::solve() {
    historico_tabu.clear();
    
    std::vector<int> solucao_atual = gerarSolucaoInicial();
    auto [v_ini, p_ini, aval_atual] = avaliarSolucao(solucao_atual);
    
    valor_inicial = aval_atual;
    tempo_inicial = p_ini;
    
    melhor_solucao = solucao_atual;
    melhor_valor = aval_atual;
    historico_tabu.push_back(melhor_valor);

    // Lista Tabu em formato de vetor
    // tabu_list[i] guarda até qual iteração o item 'i' está bloqueado
    std::vector<int> tabu_list(itens.size(), -1);

    for (int iteracao = 0; iteracao < interacoes; ++iteracao) {
        std::vector<int> melhor_vizinho_iter;
        int melhor_aval_vizinho_iter = -99999999;
        int movimento_realizado = -1;

        // Explora toda a vizinhança
        for (size_t i = 0; i < itens.size(); ++i) {
            std::vector<int> vizinho = solucao_atual;
            vizinho[i] = 1 - vizinho[i]; // Bit flip
            
            auto [v, p, aval_v] = avaliarSolucao(vizinho);

            bool eh_tabu = (tabu_list[i] > iteracao);
            bool aspiracao = eh_tabu && (aval_v > melhor_valor);

            if (!eh_tabu || aspiracao) {
                if (aval_v > melhor_aval_vizinho_iter) {
                    melhor_aval_vizinho_iter = aval_v;
                    melhor_vizinho_iter = vizinho;
                    movimento_realizado = i;
                }
            }
        }

        // Atualiza o estado
        if (movimento_realizado != -1) {
            solucao_atual = melhor_vizinho_iter;
            aval_atual = melhor_aval_vizinho_iter;
            
            // Bloqueia o item movido pelas próximas 'tenencia_tabu' iterações
            tabu_list[movimento_realizado] = iteracao + tenencia_tabu;

            // Atualiza o recorde global
            if (aval_atual > melhor_valor) {
                melhor_solucao = solucao_atual;
                melhor_valor = aval_atual;
            }
        }

        historico_tabu.push_back(melhor_valor);
    }

    auto [vf, pf, af] = avaliarSolucao(melhor_solucao);
    tempo_final_tabu = pf;
}

json TabuSearch::getResultados() const {
    json res;
    res["valor_inicial"] = valor_inicial;
    res["tempo_inicial"] = tempo_inicial;
    res["melhor_valor"] = melhor_valor;
    res["historico_ils"] = historico_tabu;
    res["tempo_final_ils"] = tempo_final_tabu;
    
    std::vector<std::string> nomes_selecionados;
    for(size_t i = 0; i < melhor_solucao.size(); ++i) {
        if(melhor_solucao[i] == 1) {
            nomes_selecionados.push_back(itens[i].nome);
        }
    }
    res["itens_selecionados"] = nomes_selecionados;
    
    return res;
}