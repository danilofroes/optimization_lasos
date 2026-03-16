#pragma once

#include <string>
#include <vector>

// configuração da biblioteca para gerar json
#include <json.hpp>
using json = nlohmann::json;

/**
 * @brief Classe abstrata para criação de algoritmos de metaheuristicas
 */
class Metaheuristicas {
    public:
        virtual ~Metaheuristicas() = default;

        virtual void solve() = 0;

        virtual void setParametros(const json &params) = 0;

        virtual json getResultados() const = 0;

        virtual std::string getNome() const = 0;
};