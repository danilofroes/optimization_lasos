#include "include/algGenetico.hpp"
#include <algorithm>
#include <numeric>
#include <iostream>

GeneticAlgorithmJSP::GeneticAlgorithmJSP() {
    jobs = {
        {"Carro", {{1, 3}, {2, 2}, {3, 2}}, 10}, // P1
        {"Boneca", {{2, 4}, {1, 1}, {3, 2}}, 8}, // P2
        {"Robô", {{3, 2}, {1, 4}, {2, 3}}, 12}   // P3
    };
}

void GeneticAlgorithmJSP::setParametros(const json &params) {
    tamanho_pop = params.value("tamanho_pop", 20);
    geracoes = params.value("geracoes", 100);
    mutacao_rate = params.value("mutacao_rate", 0.1f);
    seed = params.value("seed", 42);
    rng.seed(seed);
}

int GeneticAlgorithmJSP::calcularFitness(const std::vector<int>& cromossomo, bool save_gantt) {
    std::vector<int> jobNextTask(jobs.size(), 0);
    std::vector<int> jobReadyTime(jobs.size(), 0);
    std::vector<int> maquinaFreeTime(4, 0); // M1, M2, M3
    std::vector<int> jobFinishTime(jobs.size(), 0);

    if (save_gantt) gantt_data.clear();

    for (int jobId : cromossomo) {
        int idx = jobId - 1;
        int taskIdx = jobNextTask[idx];
        Task t = jobs[idx].route[taskIdx];

        int startTime = std::max(maquinaFreeTime[t.maquinaID], jobReadyTime[idx]);
        int endTime = startTime + t.duracao;

        maquinaFreeTime[t.maquinaID] = endTime;
        jobReadyTime[idx] = endTime;
        jobFinishTime[idx] = endTime;
        jobNextTask[idx]++;

        if (save_gantt) {
            json bloco;
            bloco["job"] = jobs[idx].name;
            bloco["machine"] = "M" + std::to_string(t.maquinaID);
            bloco["start"] = startTime;
            bloco["end"] = endTime;
            gantt_data.push_back(bloco);
        }
    }

    int atrasoTotal = 0;
    for (int i = 0; i < (int)jobs.size(); ++i) {
        atrasoTotal += std::max(0, jobFinishTime[i] - jobs[i].dueDate);
    }
    return atrasoTotal;
}

std::vector<int> GeneticAlgorithmJSP::cruzamento(const std::vector<int>& p1, const std::vector<int>& p2) {
    int size = p1.size();
    std::vector<int> child(size, -1);
    
    std::uniform_int_distribution<> dist(0, size - 1);
    int start = dist(rng);
    int end = dist(rng);
    if (start > end) std::swap(start, end);

    for (int i = start; i <= end; ++i) child[i] = p1[i];

    int corrente = (end + 1) % size;
    for (int i = 0; i < size; ++i) {
        int p2Idx = (end + 1 + i) % size;
        int item = p2[p2Idx];
        
        /// @todo a lógica atual é para um cenário onde cada job aparece 3 vezes, se mudar isso, tem que adaptar a lógica de contagem abaixo
        if (std::count(child.begin(), child.end(), item) < 3) {
            child[corrente] = item;
            corrente = (corrente + 1) % size;
        }
    }
    return child;
}

void GeneticAlgorithmJSP::mutacao(std::vector<int>& cromossomo) {
    std::uniform_int_distribution<> dist(0, cromossomo.size() - 1);
    std::swap(cromossomo[dist(rng)], cromossomo[dist(rng)]);
}

void GeneticAlgorithmJSP::solve() {
    historico_fitness.clear();

    // Cria cromossomo base
    std::vector<int> base;
    for(int i = 1; i <= 3; ++i) 
        for(int j = 0; j < 3; ++j) 
            base.push_back(i);

    // População inicial
    std::vector<std::vector<int>> populacao(tamanho_pop, base);
    for(auto& cromo : populacao) std::shuffle(cromo.begin(), cromo.end(), rng);

    for (int gen = 0; gen < geracoes; ++gen) {
        std::sort(populacao.begin(), populacao.end(), [this](const auto& a, const auto& b) {
            return calcularFitness(a) < calcularFitness(b);
        });

        historico_fitness.push_back(calcularFitness(populacao[0]));

        std::vector<std::vector<int>> nextGen;
        nextGen.push_back(populacao[0]); // Elitismo

        while (nextGen.size() < (size_t)tamanho_pop) {
            std::uniform_int_distribution<> d(0, tamanho_pop / 2);
            auto& p1 = populacao[d(rng)];
            auto& p2 = populacao[d(rng)];

            auto child = cruzamento(p1, p2);

            std::uniform_real_distribution<float> prob(0.0f, 1.0f);
            if (prob(rng) < mutacao_rate) mutacao(child);

            nextGen.push_back(child);
        }
        populacao = nextGen;
    }

    // Salva os melhores resultados e processa o Gantt da melhor solução
    melhor_cromossomo = populacao[0];
    melhor_atraso = calcularFitness(melhor_cromossomo, true);
}

json GeneticAlgorithmJSP::getResultados() const {
    json res;
    res["melhor_atraso"] = melhor_atraso;
    res["historico_fitness"] = historico_fitness;
    res["melhor_cromossomo"] = melhor_cromossomo;
    res["gantt_data"] = gantt_data;
    return res;
}