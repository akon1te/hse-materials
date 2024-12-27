#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <random>
#include <algorithm>
#include <unordered_set>
#include <stack>
#include <time.h>
#include <chrono>
using namespace std;


class ColoringProblem
{
public:
    int GetRandom(int a, int b)
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
                colors.resize(vertices + 1);
            }
            else {
                int start, finish;
                line_input >> command >> start >> finish;
                neighbour_sets[start - 1].insert(finish - 1);
                neighbour_sets[finish - 1].insert(start - 1);
            }
        }
    }

    int getMinimalDegreeIndex(vector<int> &vertices_degree){
        int min_degree = vertices_degree[0];
        int min_index = 0;
        for (int i = 1; i < vertices_degree.size(); ++i){
            if (vertices_degree[i] < min_degree){
                min_degree = vertices_degree[i];
                min_index = i;
            }
        }
        vertices_degree[min_index] = INT32_MAX;
        for (int neighbour : neighbour_sets[min_index]){
            vertices_degree[neighbour]--;
        }
        return min_index;
    }

    int getAvailableColor(unordered_set<int> &neighbours){
        vector<int> neighbours_colors;
        for (int neighbour : neighbours){
            neighbours_colors.push_back(colors[neighbour]);
        }
        sort(neighbours_colors.begin(), neighbours_colors.end());
        for (int i = 1; i < neighbours_colors.size(); ++i){
            if (neighbours_colors[i] - neighbours_colors[i - 1] > 1){
                return neighbours_colors[i - 1] + 1;
            }
        }
        return neighbours_colors.back() + 1;
    }

    void MyGreedyGraphColoring()
    {     
        vector<int> vertices_degree(neighbour_sets.size());
        for (int i = 0; i < neighbour_sets.size(); ++i){
            vertices_degree[i] = neighbour_sets[i].size();
        }

        stack<int> sorted_neighbour_sets;
        for (size_t i = 0; i < vertices_degree.size(); ++i){
            int min_index = getMinimalDegreeIndex(vertices_degree);
            sorted_neighbour_sets.push(min_index);
        }
        
        colors.resize(neighbour_sets.size(), 1);
        
        while (!sorted_neighbour_sets.empty()) {
            int idx = sorted_neighbour_sets.top();
            colors[idx] = getAvailableColor(neighbour_sets[idx]);
            sorted_neighbour_sets.pop();
        }
    }


    bool Check()
    {
        for (size_t i = 0; i < neighbour_sets.size(); ++i) {
            if (colors[i] == 0){
                cout << "Vertex " << i + 1 << " is not colored\n";
                return false;
            }
            for (int neighbour : neighbour_sets[i]) {
                if (colors[neighbour] == colors[i]) {
                    cout << "Neighbour vertices " << i + 1 << ", " << neighbour + 1 <<  " have the same color\n";
                    return false;
                }
            }
        }
        return true;
    }

    int GetNumberOfColors()
    {
        return *max_element(colors.begin(), colors.end());
    }

    const vector<int>& GetColors()
    {
        return colors;
    }

private:
    vector<int> colors;
    int maxcolor = 1;
    vector<unordered_set<int>> neighbour_sets;
};

int main()
{
    vector<string> files = {"myciel3.col", "myciel7.col", "school1.col", "school1_nsh.col",
                           "anna.col", "miles1000.col", "miles1500.col",
                           "le450_5a.col", "le450_15b.col", "queen11_11.col"};

    string folder = "data/";
    ofstream fout("color.csv");

    fout << "Instance; Colors; Time (sec)\n";
    cout << "Instance; Colors; Time (sec)\n";
    for (string file : files)
    {
        ColoringProblem problem;
        problem.ReadGraphFile(folder + file);
        clock_t start = clock();
        problem.MyGreedyGraphColoring();

        if (!problem.Check()) {
            cout << "*** WARNING: incorrect coloring: ***\n";
        }
        fout << file << "; " << problem.GetNumberOfColors() << "; " << double(clock() - start) / CLOCKS_PER_SEC << '\n';
        cout << file << "; " << problem.GetNumberOfColors() << "; " << double(clock() - start) / CLOCKS_PER_SEC << '\n';
    }
    fout.close();
    return 0;
}