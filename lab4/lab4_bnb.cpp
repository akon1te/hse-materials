#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <time.h>
#include <random>
#include <unordered_set>
#include <algorithm>
#include <stack>
#include <cassert>
#include <unordered_map>
#include <map>
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


class BnBSolver
{
public:
    void ReadGraphFile(string filename)
    {   
        cout << filename << endl;
        ifstream fin(filename);
        string line;
        file = filename;
        int vert = 0, edges = 0;
        while (getline(fin, line)) {
            if (line[0] == 'c') {
                continue;
            }
            if (line[0] == 'p') {
                stringstream s(line);
                char c;
                string in;
                s >> c >> in >> vert >> edges;
                neighbours.resize(vert);
            } else {
                stringstream s(line);
                char c;
                int st, fn;
                s >> c >> st >> fn;
                neighbours[st - 1].insert(fn - 1);
                neighbours[fn - 1].insert(st - 1);
            }
        }
    }

    void RunBnB()
    {
        MaxCliqueTabuSearch st;
        st.ReadGraphFile(file);
        st.RunSearch(1);
        
        best_clique = st.GetClique();
        auto c_pardalos = candidates_ordering();
        BnBRecursion(c_pardalos);
    }

    const unordered_set<int>& GetClique()
    {
        return best_clique;
    }

    bool Check()
    {
        for (int i : clique) {
            for (int j : clique) {
                if (i != j && neighbours[i].count(j) == 0) {
                    cout << "Returned subgraph is not clique\n";
                    return false;
                }
            }
        }
        return true;
    }

    void ClearClique()
    {
        best_clique.clear();
        clique.clear();
    }

private:
    vector<unordered_set<int>> neighbours;
    unordered_set<int> best_clique;
    unordered_set<int> clique;
    string file;


    vector<int> candidates_ordering() {
        vector<int> c_pardalos_ordering(neighbours.size());
        vector<int> vertices_degree(neighbours.size());
        
        for (int i = 0; i < neighbours.size(); i++) {
            vertices_degree[i] = neighbours[i].size();
        }
        
        for (int i = 0; i < neighbours.size(); i++) {
            int min_vertex = distance(vertices_degree.begin(), min_element(vertices_degree.begin(), vertices_degree.end()));

            vertices_degree[min_vertex] = INT32_MAX;
            for (int neighbour : neighbours[min_vertex]) {
                vertices_degree[neighbour]--;
            }

            c_pardalos_ordering[i] = min_vertex;
        }
        return c_pardalos_ordering;
    }

    map<int, deque<int>> greedy_coloring(const vector<int>& candidates) 
    {
        vector<int> colors(neighbours.size(), 0);
        map<int, deque<int>> color_classes;

        for (int i = candidates.size() - 1; i >= 0; i--) {
            int vertex = candidates[i];

            vector<int> neighbours_colors;
            for (int neighbour : neighbours[vertex]){
                neighbours_colors.push_back(colors[neighbour]);
            }

            int current_v_color = -1;
            sort(neighbours_colors.begin(), neighbours_colors.end());
            for (int i = 1; i < neighbours_colors.size(); ++i){
                if (abs(neighbours_colors[i] - neighbours_colors[i - 1]) > 1){
                    current_v_color = neighbours_colors[i - 1] + 1;
                    break;
                }
            }
            if (current_v_color == -1)
                current_v_color = neighbours_colors.back() + 1;
            
            colors[vertex] = current_v_color;
            color_classes[current_v_color].push_front(vertex);
        }

        return color_classes;
    }


    void BnBRecursion(vector<int> &candidates) {

        if (candidates.empty()) {
            if (clique.size() > best_clique.size()) {
                best_clique = clique;
            }
            return;
        }
        
        map<int, deque<int>> colored_candidates = greedy_coloring(candidates);
        
        unordered_set<int> used_colored_candidates;
        vector<int> filtered_candidates;

        for (int color = colored_candidates.size(); color >= 1; color--) {
            if (clique.size() + color <= best_clique.size()) 
                return; 

            for (auto vertex: colored_candidates[color]) {
                clique.insert(vertex);

                filtered_candidates.resize(0);
                used_colored_candidates.insert(vertex);

                for (auto candidate : candidates) {
                    if (!used_colored_candidates.contains(candidate)) {
                        if (neighbours[vertex].contains(candidate)) {
                            filtered_candidates.push_back(candidate);
                        }
                    }
                }

                BnBRecursion(filtered_candidates);
                clique.erase(vertex);
            }
        }
    }
};

int main()
{
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);

    string folder = "data/";
    vector<string> files = {"brock200_1.clq", "brock200_2.clq", "brock200_3.clq", "brock200_4.clq", 
                            "C125.9.clq", "gen200_p0.9_44.clq", "gen200_p0.9_55.clq",
                            "hamming8-4.clq", "johnson16-2-4.clq", "johnson8-2-4.clq", 
                            "keller4.clq", "MANN_a27.clq", "MANN_a9.clq", "p_hat1000-1.clq",
                            "p_hat1500-1.clq", "p_hat300-3.clq", "san1000.clq", "sanr200_0.9.clq"};

    ofstream fout("clique_bnb.csv");
    fout << "File; Clique; Time (sec)\n";
    for (string file : files)
    {
        BnBSolver problem;
        problem.ReadGraphFile(folder + file);
        problem.ClearClique();
        clock_t start = clock();
        problem.RunBnB();
        if (!problem.Check())
        {
            cout << "*** WARNING: incorrect clique ***\n";
        }
        fout << file << "; " << problem.GetClique().size() << "; " << double(clock() - start) / CLOCKS_PER_SEC << '\n';
        cout << file << ", result - " << problem.GetClique().size() << ", time - " << double(clock() - start) / CLOCKS_PER_SEC << '\n';
    }
    return 0;
}