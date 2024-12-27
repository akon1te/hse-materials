#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <time.h>
#include <random>
#include <unordered_set>
#include <algorithm>
using namespace std;


class MaxCliqueProblem
{
public:
    static int GetRandom(int a, int b)
    {
        static mt19937 generator;
        uniform_int_distribution<int> uniform(a, b);
        return uniform(generator);
    }

    void ReadGraphFile(string filename)
    {
        ifstream fin(filename);
        string line;
        int vertices = 0, edges = 0;
        while (getline(fin, line)){
            if (line[0] == 'c'){
                continue;
            }

            stringstream line_input(line);
            char command;
            if (line[0] == 'p'){
                string type;
                line_input >> command >> type >> vertices >> edges;
                neighbour_sets.resize(vertices);
            }
            else {
                int start, finish;
                line_input >> command >> start >> finish;
                neighbour_sets[start - 1].insert(finish - 1);
                neighbour_sets[finish - 1].insert(start - 1);
            }
        }
    }


    int getMaximalDegreeIndex(vector<int> &vertices_degree){
        int max_degree = vertices_degree[0];
        int max_index = 0;
        for (int i = 1; i < vertices_degree.size(); ++i){
            if (vertices_degree[i] > max_degree){
                max_degree = vertices_degree[i];
                max_index = i;
            }
        }
        vertices_degree[max_index] = -1;
        for (int neighbour : neighbour_sets[max_index]){
            vertices_degree[neighbour]--;
        }
        return max_index;
    }


    vector<int> updateCandidates(vector<int> &candidates, int new_clique_vertex)
    {
        vector<int> new_candidates;
        for (auto vertex: candidates){
            auto &neighbours = neighbour_sets[new_clique_vertex];
            if (neighbours.find(vertex) != neighbours.end()){
                new_candidates.push_back(vertex);
            }
        }
        return new_candidates;
    }
    

    void findMaxClique(int iterations)
    {
        static mt19937 generator;
        vector<int> vertices_degree(neighbour_sets.size());
        for (int i = 0; i < neighbour_sets.size(); ++i){
            vertices_degree[i] = neighbour_sets[i].size();
        }
        
        vector<int> sorted_vertices;
        for (size_t i = 0; i < vertices_degree.size(); ++i){
            int min_index = getMaximalDegreeIndex(vertices_degree);
            sorted_vertices.push_back(min_index);
        }

        for (int iteration = 0; iteration < iterations; ++iteration){
            vector<int> clique;
            auto candidates = sorted_vertices;

            int initial_vertex = candidates[GetRandom(0, 5)];
            clique.push_back(initial_vertex);
            candidates = updateCandidates(candidates, initial_vertex);

            while (candidates.size() > 0){
                int candidates_size = candidates.size() - 1;
                int new_vertex = candidates[GetRandom(0, candidates_size)];
                clique.push_back(new_vertex);
                candidates = updateCandidates(candidates, new_vertex);
            }

            if (clique.size() > best_clique.size()) {
                best_clique = clique;
            }
        }
    }

    const vector<int>& GetClique()
    {
        return best_clique;
    }

    bool Check()
    {
        if (unique(best_clique.begin(), best_clique.end()) != best_clique.end()){
            cout << "Duplicated vertices in the clique\n";
            return false;
        }
        for (int i : best_clique){
            for (int j : best_clique){
                if (i != j && neighbour_sets[i].count(j) == 0){
                    cout << "Returned subgraph is not a clique\n";
                    return false;
                }
            }
        }
        return true;
    }

private:
    vector<unordered_set<int>> neighbour_sets;
    vector<int> best_clique;
};

int main()
{
    int iterations;
    cout << "Number of iterations: ";
    cin >> iterations;
    
    string folder = "data/";
    vector<string> files = {"brock200_1.clq", "brock200_2.clq", "brock200_3.clq", 
                            "brock200_4.clq", "brock400_1.clq", "brock400_2.clq", 
                            "brock400_3.clq", "brock400_4.clq", "C125.9.clq", 
                            "gen200_p0.9_44.clq", "gen200_p0.9_55.clq", "hamming8-4.clq",
                            "johnson16-2-4.clq", "johnson8-2-4.clq", "keller4.clq", 
                            "MANN_a27.clq", "MANN_a9.clq", "p_hat1000-1.clq", 
                            "p_hat1000-2.clq", "p_hat1500-1.clq", "p_hat300-3.clq",
                            "p_hat500-3.clq", "san1000.clq", "sanr200_0.9.clq", "sanr400_0.7.clq" };

    // Debug
    //vector<string> files = {"C125.9.clq"};
        
    ofstream fout("clique.csv");
    fout << "File; Clique; Time (sec)\n";
    for (string file : files)
    {
        MaxCliqueProblem problem;
        problem.ReadGraphFile(folder + file);
        clock_t start = clock();
        problem.findMaxClique(iterations);
        if (! problem.Check())
        {
            cout << "*** WARNING: incorrect clique ***\n";
        }
        fout << file << "; " << problem.GetClique().size() << "; " << double(clock() - start) / CLOCKS_PER_SEC << '\n';
        cout << file << ", result - " << problem.GetClique().size() << ", time - " << double(clock() - start) / CLOCKS_PER_SEC << '\n';
    }
    fout.close();
    return 0;
}
