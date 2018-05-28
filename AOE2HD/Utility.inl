#ifndef Utility
#define Utility

#include "Trainer.h"

namespace utility{
    void debug_pause();
}

template <typename T>
bool is_numeric_legal(T value){
    if(value < min_valid_value)return false;
    if(value > max_valid_value)return false;
    return true;
}

template <typename T>
bool input_numeric(T &input, bool freeze_enabled, string message){
    cin.clear();
    bool passed = false;
    while(!passed){
        cout << message;
        cin >> input;
        if(input < min_valid_value){
            cout << "Number too small, acceptable minimum is " << min_valid_value << '\n';
        }
        else if(input > max_valid_value){
            cout << "Number too large, acceptable maximum is " << max_valid_value << '\n';
        }
        else{passed = true;}
    }
    if(freeze_enabled){
        cout << "Freeze/Unfreeze value?(y/n): ";
        while(true){
            char ch = getch();
            if(ch == 'y'){
                cout << "\n\n";
                return true;
            }
            else if(ch == 'n'){
                cout << "\n\n";
                return false;
            }
        }
    }
    return false;
}

template <typename T>
void process_numeric_modification(HackMemory<T>& target, bool freeze_enabled, string input_msg){
    T input;
    string msg = (input_msg == "" ? target.message : input_msg);
    bool fz = input_numeric(input, freeze_enabled, msg);
    target.modify(input);
    if(fz)target.toggle_active();
}

#endif // Utility
