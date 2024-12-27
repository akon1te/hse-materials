#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <time.h>
#include <random>
#include <unordered_set>
#include <algorithm>
#include <cassert>
using namespace std;


class MaxCliqueTabuSearch
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
                qco.resize(vertices);
                index.resize(vertices, -1);
                non_neighbours.resize(vertices);
            } 
            else{
                int start, finish;
                line_input >> command >> start >> finish;
                neighbour_sets[start - 1].insert(finish - 1);
                neighbour_sets[finish - 1].insert(start - 1);
            }
        }
        for (int i = 0; i < vertices; ++i){
            for (int j = 0; j < vertices; ++j){
                if (neighbour_sets[i].count(j) == 0 && i != j)
                    non_neighbours[i].insert(j);
            }
        }
        tightness.resize(vertices);
    }

    void RunSearch(int iterations)
    {
        for (int iter = 0; iter < iterations; ++iter){
            ClearClique();
            for (size_t i = 0; i < neighbour_sets.size(); ++i){
                qco[i] = i;
                index[i] = i;
                tightness[i] = 0;
            }
            RunInitialHeuristic();

            c_border = q_border;
            int swaps = 0;
            while (swaps < 100){
                if (!move()){
                    if (!swap1to2()){
                        if (!swap1to1()) {
                            break;
                        } else {
                            ++swaps;
                        }   
                    } else {
                        ++swaps;
                    }
                }
            }
            if (q_border > best_clique.size()){
                best_clique.clear();
                for (int i = 0; i < q_border; ++i)
                    best_clique.insert(qco[i]);
            }
        }
    }

    const unordered_set<int>& GetClique()
    {
        return best_clique;
    }

    bool Check()
    {
        for (int i : best_clique){
            for (int j : best_clique){
                if (i != j && neighbour_sets[i].count(j) == 0){
                    cout << "Returned subgraph is not clique\n";
                    return false;
                }
            }
        }
        return true;
    }

    void ClearClique()
    {
        q_border = 0;
        c_border = neighbour_sets.size();
    }

private:
    vector<unordered_set<int>> neighbour_sets;
    vector<unordered_set<int>> non_neighbours;
    vector<int> tightness;
    unordered_set<int> best_clique;
    vector<int> qco;
    vector<int> index;
    int q_border = 0;
    int c_border = 0;

    int computeTightness(int vertex)
    {
        int tightness = 0;
        for (int i = 0; i < q_border; ++i){
            if (non_neighbours[qco[i]].count(vertex))
                ++tightness;
        }
        return tightness;
    }

    void swapVertices(int vertex, int border)
    {
        int vertex_at_border = qco[border];
        swap(qco[index[vertex]], qco[border]);
        swap(index[vertex], index[vertex_at_border]);
    }

    void insertToClique(int i)
    {
        swapVertices(i, q_border++);
        for (int j : non_neighbours[i]){
            if (tightness[j] == 0){
                swapVertices(j, --c_border);
            }
            ++tightness[j];
        }
        
    }

    void removeFromClique(int k)
    {
        swapVertices(k, --q_border);
        for (int j : non_neighbours[k]){
            if (tightness[j] == 1){
                swapVertices(j, c_border++);
            }
           --tightness[j];
        }
    }

    bool swap1to1()
    {
        for (int counter = 0; counter < q_border; ++counter){
            int vertex = qco[counter];
            for (int i : non_neighbours[vertex]){
                if (tightness[i] == 1){
                    removeFromClique(vertex);
                    insertToClique(i);
                    return true;
                }
            }
        }
        return false;
    }

    bool swap1to2()
    {
        for (int counter = 0; counter < q_border; ++counter){
            int vertex = qco[counter];
            int first_insert_v = -1, insert_counter = 0;
            
            for (int i : non_neighbours[vertex]){
                if (tightness[i] == 1 && insert_counter == 1) {
                    if (!non_neighbours[first_insert_v].contains(i)) {
                        removeFromClique(vertex);
                        insertToClique(first_insert_v);
                        insertToClique(i);
                        return true;
                    }
                }
                if (tightness[i] == 1 && insert_counter == 0) {
                    first_insert_v = i;
                    insert_counter = 1;
                }
            }
        }
        return false;
    } 

    bool move()
    {
        if (c_border == q_border)
            return false;
        int vertex = qco[q_border];
        assert(q_border < qco.size());
        insertToClique(vertex);
        return true;
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

    void RunInitialHeuristic()
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

        while (sorted_vertices.size() > 0){
            int candidates_size = sorted_vertices.size() - 1;
            int new_vertex = sorted_vertices[GetRandom(0, candidates_size)];
            insertToClique(new_vertex);
            sorted_vertices = updateCandidates(sorted_vertices, new_vertex);
        }
    }
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
    //vector<string> files = {"brock200_1.clq"};

    ofstream fout("clique_tabu.csv");
    fout << "File; Clique; Time (sec)\n";
    for (string file : files)
    {
        MaxCliqueTabuSearch problem;
        problem.ReadGraphFile(folder + file);
        clock_t start = clock();
        problem.RunSearch(iterations);
        if (!problem.Check())
        {
            cout << "*** WARNING: incorrect clique ***\n";
        }
        fout << file << "; " << problem.GetClique().size() << "; " << double(clock() - start) / CLOCKS_PER_SEC << '\n';
        cout << file << ", result - " << problem.GetClique().size() << ", time - " << double(clock() - start) / CLOCKS_PER_SEC << '\n';
    }
    fout.close();
    return 0;
}
