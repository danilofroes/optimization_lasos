#include "include/ILS.hpp"
#include <algorithm>
#include <iostream>
#include <numeric>

/// @brief Método para receber os dados do Python via JSON
void ILS::setParametros(const json &params) {
    tipo_solucao_inicial = params.value("tipo_solucao_inicial", "aleatoria");
    capacidade = params.value("capacidade", 0);
    interacoes = params.value("interacoes", 1000);
    nivel_perturbacao = params.value("nivel_perturbacao", 1);
    taxa_violacao = params.value("taxa_violacao", 20);
    limite_sem_melhora = params.value("limite_sem_melhora", 50);
    seed = params.value("seed", 42);

    rng.seed(seed); // Inicializa a semente aleatória
    itens.clear();

    // Lê o dicionário de itens do JSON ({"item1": {"peso": 10, "valor": 20}, ...})
    auto json_itens = params["itens"];
    for (auto& [nome_item, atributos] : json_itens.items()) {
        Item novo_item;
        novo_item.nome = nome_item;
        novo_item.peso = atributos["peso"];
        novo_item.valor = atributos["valor"];
        itens.push_back(novo_item);
    }
}

/// @brief Método para avaliar uma solução
std::tuple<int, int, int> ILS::avaliarSolucao(const std::vector<int>& solucao) {
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

/// @brief Método para realizar a busca local
std::pair<std::vector<int>, int> ILS::buscaLocal(const std::vector<int>& solucao_inicial) {
    std::vector<int> solucao_atual = solucao_inicial;
    auto [v_atual, p_atual, aval_atual] = avaliarSolucao(solucao_atual);

    std::vector<int> melhor_vizinho = solucao_atual;
    int aval_vizinho = -99999999;

    for (size_t i = 0; i < itens.size(); ++i) {
        std::vector<int> vizinho = solucao_atual;
        vizinho[i] = 1 - vizinho[i]; // Bit flip
        
        auto [v, p, aval] = avaliarSolucao(vizinho);
        if (aval > aval_vizinho) {
            aval_vizinho = aval;
            melhor_vizinho = vizinho;
        }
    }

    if (aval_vizinho > aval_atual) {
        return {melhor_vizinho, aval_vizinho};
    }
    return {solucao_atual, aval_atual};
}

/// @brief Método para perturbar uma solução
std::vector<int> ILS::perturbarSolucao(const std::vector<int>& solucao) {
    std::vector<int> nova_solucao = solucao;
    
    std::uniform_int_distribution<int> dist(0, itens.size() - 1);
    for(int i = 0; i < nivel_perturbacao; ++i) {
        int idx = dist(rng);
        nova_solucao[idx] = 1 - nova_solucao[idx];
    }
    return nova_solucao;
}

/// @brief Método para gerar uma solução inicial baseada no tipo definido
std::vector<int> ILS::gerarSolucaoInicial() {
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

/// @brief Método para executar o algoritmo ILS
void ILS::solve() {
    historico_ils.clear();
    
    std::vector<int> solucao_atual = gerarSolucaoInicial();
    auto [v_ini, p_ini, aval_atual] = avaliarSolucao(solucao_atual);
    
    valor_inicial = aval_atual;
    tempo_inicial = p_ini;

    auto [sol_bl, aval_bl] = buscaLocal(solucao_atual);
    solucao_atual = sol_bl;
    aval_atual = aval_bl;

    melhor_solucao = solucao_atual;
    melhor_valor = aval_atual;
    historico_ils.push_back(melhor_valor);

    int contador_sem_melhora = 0;

    for (int i = 0; i < interacoes; ++i) {
        std::vector<int> solucao_perturbada = perturbarSolucao(solucao_atual);
        auto [sol_candidata, aval_candidata] = buscaLocal(solucao_perturbada);

        if (aval_candidata > aval_atual) {
            solucao_atual = sol_candidata;
            aval_atual = aval_candidata;
        }

        if (aval_candidata > melhor_valor) {
            melhor_solucao = sol_candidata;
            melhor_valor = aval_candidata;
            contador_sem_melhora = 0;
        } else {
            contador_sem_melhora++;
        }

        historico_ils.push_back(melhor_valor);

        if (contador_sem_melhora >= limite_sem_melhora) {
            int restante = interacoes - 1 - i;
            for (int r = 0; r < restante; ++r) historico_ils.push_back(melhor_valor);
            break;
        }
    }

    auto [vf, pf, af] = avaliarSolucao(melhor_solucao);
    tempo_final_ils = pf; // Salva o peso total da melhor solução
}

/// @brief Método para retornar os dados para o Python plottar
json ILS::getResultados() const {
    json res;
    res["valor_inicial"] = valor_inicial;
    res["tempo_inicial"] = tempo_inicial;
    res["melhor_valor"] = melhor_valor;
    res["historico_ils"] = historico_ils;
    res["tempo_final_ils"] = tempo_final_ils;
    
    // Converte vetor binário de volta para os nomes dos itens
    std::vector<std::string> nomes_selecionados;
    for(size_t i = 0; i < melhor_solucao.size(); ++i) {
        if(melhor_solucao[i] == 1) {
            nomes_selecionados.push_back(itens[i].nome);
        }
    }
    res["itens_selecionados"] = nomes_selecionados;
    
    return res;
}