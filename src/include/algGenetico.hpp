#pragma once

#include <vector>
#include <string>
#include <random>
#include <json.hpp>

using json = nlohmann::json;

struct Task {
    int maquinaID;
    int duracao;
};

struct Job {
    std::string name;
    std::vector<Task> route;
    int dueDate;
};

class GeneticAlgorithmJSP {
private:
    int tamanho_pop;
    int geracoes;
    float mutacao_rate;
    int seed;

    std::mt19937 rng;
    std::vector<Job> jobs;

    std::vector<int> melhor_cromossomo;
    int melhor_atraso;
    std::vector<int> historico_fitness;
    json gantt_data;

    int calcularFitness(const std::vector<int>& cromossomo, bool save_gantt = false);
    std::vector<int> cruzamento(const std::vector<int>& p1, const std::vector<int>& p2);
    void mutacao(std::vector<int>& cromossomo);

public:
    GeneticAlgorithmJSP();
    
    void setParametros(const json &params);
    void solve();
    json getResultados() const;
    std::string getNome() const { return "Genetic Algorithm (JSP)"; }
};