#include <bits/stdc++.h>

const bool Debug = false;

struct Node{
    bool stat;
    int index;
    std::vector<int> adjcents;
    Node(bool s, int i){stat = s; index = i;}
    Node(Node* n){
        stat = n -> stat;
        index = n -> index;
        adjcents = n -> adjcents;
    }
};

struct Panel{
    std::vector<Node*> graph;
    int rating, last;
    std::vector<int> actions;

    Panel(std::vector<Node*> nodes){
        graph = nodes;
        rating = 0;
        last = -1;
        for(auto &n:nodes){
            if(n -> stat){rating += 1;}
        }
    }
};

std::vector<Node*> pool;
std::vector<Panel*> pool2;

struct CompareRating{
    bool operator ()(const Panel* l, const Panel* r){
        return l -> rating > r -> rating;
    }
};

void clear_pool(){
    for(auto &p:pool){delete p;}
    for(auto &p:pool2){delete p;}
    pool.clear(); pool2.clear();
}

Node* create_node(bool s, int i){
    auto re = new Node(s, i);
    pool.push_back(re);
    return re;
}

Node* create_node(Node* n){
    auto re = new Node(n);
    pool.push_back(re);
    return re;
}

Panel* create_panel(std::vector<Node*> nds){
    auto re = new Panel(nds);
    pool2.push_back(re);
    return re;
}

int main(){
    while(1){
    std::fstream fs("ans.txt", std::fstream::out | std::fstream::app);
    std::vector<Node*> graph;
    for(int i=0, in;i<10;++i){
        std::cin >> in;
        graph.push_back(create_node(in&1, i));
        fs << (in&1) << ' ';
    }
    fs << ": ";
    std::vector<std::vector<int>> adjcents;
    adjcents.push_back(std::vector<int>({1,3,4}));
    adjcents.push_back(std::vector<int>({0,2,4,5}));
    adjcents.push_back(std::vector<int>({1,5,6}));
    adjcents.push_back(std::vector<int>({0,4,7}));
    adjcents.push_back(std::vector<int>({0,1,3,5,7,8}));
    adjcents.push_back(std::vector<int>({1,2,4,6,8,9}));
    adjcents.push_back(std::vector<int>({2,5,9}));
    adjcents.push_back(std::vector<int>({3,4,8}));
    adjcents.push_back(std::vector<int>({4,5,7,9}));
    adjcents.push_back(std::vector<int>({5,6,8}));

    std::queue<Panel*> que;
    auto pan = create_panel(graph);
    que.push(pan);
    bool done = false;
    if(Debug){std::cout << "Start\n";}
    while(!que.empty() && !done){
        auto pa = que.front(); que.pop();
        bool ok = true;
        for(auto &node:pa -> graph){if(node -> stat){ok=false;break;}}
        if(ok){
            std::cout << "Sol: ";
            for(auto &i:pa -> actions){
                std::cout << i << ' ';
                fs << i << ' ';
            }
            std::cout << "----------------\n" << "Final:\n";
                for(auto &n:pa -> graph){
                    std::cout << n->stat << ' ';
                }
            std::cout << '\n'; done = true; break;
        }
        for(auto &node:pa -> graph){
            if(node -> index == pa -> last){continue;}
            std::vector<Node*> tmp_nodes;
            for(Node* p:pa -> graph){
                tmp_nodes.push_back(create_node(p));
            }

            if(Debug){
                std::cout << "----------------\n" << "Ori:\n";
                for(auto &n:pa -> graph){
                    std::cout << n->stat << ' ';
                }
                std::cout << '\n' << "Rating: " << pa -> rating << '\n';
                std::cout << "Click: " << node -> index << '\n';
            }
            tmp_nodes[node -> index] -> stat ^= 1;
            for(auto i:adjcents[node->index]){
                tmp_nodes[i] -> stat ^= 1;
            }
            auto tmpp = create_panel(tmp_nodes);
            tmpp -> actions = pa -> actions;
            tmpp -> actions.push_back(node -> index);
            tmpp -> last = node -> index;
            if(Debug){
                for(auto &n:tmp_nodes){
                    std::cout << n->stat << ' ';
                }
                std::cout << '\n' << "Actions: \n";
                for(auto &i:tmpp -> actions){
                    std::cout << i << ' ';
                }
                std::cout << '\n' << "Rating: "<< tmpp -> rating << '\n';
                getchar();
            }
            que.push(tmpp);
        }
    }
    clear_pool();
    fs.close();
    }// while(1)
}
