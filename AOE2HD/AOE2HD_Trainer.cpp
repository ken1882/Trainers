#include <iostream>
#include <cstdio>
#include <vector>
#include <windows.h>
#include <cstring>
#include <time.h>
#include <tlhelp32.h>

using namespace std;

#define debugmode 0

// Functions
void update_proc_detection();
void update_input();
void get_base_address();
void process_modification();
void process_terminate();

// Global variables
const string Version = "1.0.0";
const string Title = "AoK HD Trainer";
const LPSTR LGameWindow = "Age of Empires II: HD Edition";
const int FPS   = 60;
const int fwait = 1000 / FPS;
const int refresh_timer = 5000;
const DWORD StaticOffset = 0x6dc5c0;
bool running, procOpened, refresh_needed, connet_needed, focused;
HWND HGameWindow, hwndThis;
DWORD procID, RESBaseAddress;
HANDLE procHandle;

/**================================================================================*
 *  > HackMemory
 * --------------------------------------------------------------------------------
 *  The target value that need to change
 *================================================================================**/
template <typename T>
struct HackMemory{
    /*-----------------------------------------------------------------------*
     *  > Public Instance Variable
     *-----------------------------------------------------------------------*/
    DWORD base_address;
    DWORD target_address;
    vector<DWORD> offsets;
    T value;
    /*-----------------------------------------------------------------------*
     *  > Object initialization
     *-----------------------------------------------------------------------*/
    HackMemory(DWORD base, initializer_list<DWORD> _offsets, T _value = -1){
        base_address = base;
        value = _value;
        for(auto offset:_offsets){
            offsets.push_back(offset);
        }
        FindMemory();
    }
    /*-----------------------------------------------------------------------*
     *  > Find the current address of target
     *-----------------------------------------------------------------------*/
    void FindMemory(){
        DWORD temp;
        target_address = base_address;
        ReadProcessMemory(procHandle, (LPCVOID) target_address, &temp,
                           sizeof(temp), NULL);

        int _size = offsets.size();
        for(int i=0;i<_size;i++){
            target_address = temp + offsets[i];
            ReadProcessMemory(procHandle, (LPCVOID)target_address, &temp,
                              sizeof(temp), NULL);
        }
    }
    /*-----------------------------------------------------------------------*
     *  > Modification implement
     *-----------------------------------------------------------------------*/
    void modify(T _value = -1){
        value = _value == -1 ? value : _value;
        if(value == -1)return ;
        if(debugmode){
            printf("Base/Target Address: %x/%x", base_address, target_address);
            cout << "; value: " << value << endl << endl;
        }
        WriteProcessMemory(procHandle,(BYTE*)target_address, &value,
                           sizeof(value), NULL);
    }
};
/*-----------------------------------------------------------------------*
 *  > Global variable initialization
 *-----------------------------------------------------------------------*/
void initialize(){
    running        = true;
    procOpened     = false;
    refresh_needed = true;
    connet_needed  = true;
    focused        = true;
    HGameWindow    = NULL;
    procID         = NULL;
    procHandle     = NULL;
}
/*-----------------------------------------------------------------------*
 *  > Print program information
 *-----------------------------------------------------------------------*/
void print_info(){
    system("CLS");
    std::cout << "Name: " << Title << '\n';
    std::cout << "Version: " << Version << '\n';
    std::cout << "*---------------------------------> Information <---------------------------------*\n";
    std::cout << "* This application can change the value of wood, food, gold, stone, current       *\n";
    std::cout << "* population and max population.                                                  *\n";
    std::cout << "*                Programmed by Compeador(https://github.com/ken1882)              *\n";
    std::cout << "*---------------------------------------------------------------------------------*\n";
    std::cout << "*                                 > User Guide  <                                 *\n";
    std::cout << "*---------------------------------------------------------------------------------*\n";
    std::cout << "* After you start/load a game in AOE2 HD, open up this window then press F1 to do *\n";
    std::cout << "* the hacks. Enter the amount of resources and population you desire.             *\n";
    std::cout << "* Then everything will goes as you expected!                                      *\n";
    std::cout << "*                                                                                 *\n";
    std::cout << "* If you think it's done, press alt+ESC to close this window.                     *\n";
    std::cout << "*---------------------------------------------------------------------------------*\n";
    cout << endl;
    cout << "Process [" << LGameWindow << "] >> ";
    cout << (procOpened ? "Ready" : "Not detected") << '\n';

    if(procOpened){
        cout << "Press F1 to hack resources\n";
    }
    refresh_needed = false;
}
/*-----------------------------------------------------------------------*
 *  > Main process
 *-----------------------------------------------------------------------*/
int main(){
    hwndThis = GetForegroundWindow();
    initialize();
    auto LastUpdateTime = clock();
    while(running){
        update_proc_detection();
        get_base_address();
        if(GetForegroundWindow() == hwndThis){
            update_input();
            if(refresh_needed || LastUpdateTime + refresh_timer < clock()){
                LastUpdateTime = clock();
                print_info();
            }
        }
        Sleep(fwait);
    }
    CloseHandle(procHandle);
    CloseHandle(HGameWindow);
    return 0;
}
/*-----------------------------------------------------------------------*
 *  > Update keyboard input
 *-----------------------------------------------------------------------*/
void update_input(){
    bool keys[0xff] = {0};
    for(int i=0;i<0xff;i++){
        keys[i] = GetAsyncKeyState(i);
    }

    if(keys[VK_MENU] && keys[VK_ESCAPE]){
        process_terminate();
    }

    if(procOpened && keys[VK_F1]){
        process_modification();
    }
}
/*-----------------------------------------------------------------------*
 *  > Detect game process
 *-----------------------------------------------------------------------*/
void update_proc_detection(){
    procOpened = false;
    HGameWindow = FindWindow(NULL, LGameWindow);
    if(!HGameWindow){connet_needed = true; return ;}

    GetWindowThreadProcessId(HGameWindow, &procID);
    if(!procID){connet_needed = true; return ;}

    procHandle = OpenProcess(PROCESS_ALL_ACCESS, false, procID);
    if(procHandle == INVALID_HANDLE_VALUE || procHandle == NULL){
        connet_needed = true; return ;
    }

    procOpened = true;
}
/*-----------------------------------------------------------------------*
 *  > Get static pointer address when process detected
 *-----------------------------------------------------------------------*/
void get_base_address(){
    if(!procOpened)return ;
    if(!connet_needed)return ;
    connet_needed = false;
    auto tempHandle = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, procID);
    tagMODULEENTRY32 tempMod;
    Module32First(tempHandle, &tempMod);
    RESBaseAddress = (DWORD)tempMod.modBaseAddr + StaticOffset;
    refresh_needed = true;
}
/*-----------------------------------------------------------------------*
 *  > Modification interface
 *-----------------------------------------------------------------------*/
void process_modification(){
    string name[] = {"Wood storage","Food storage",
                         "Gold storage", "Stone storage",
                         "Current Population", "Population Max",
                         };

    // Static pointer base address
    DWORD base_address[] = {RESBaseAddress, RESBaseAddress,
                            RESBaseAddress, RESBaseAddress,
                            RESBaseAddress, RESBaseAddress};
    // Pointer offsets
    vector<initializer_list<DWORD>> offsets(6);
    offsets[0] = {0xb08,0x134,0x3c,0x4};
    offsets[1] = {0xb08,0x18c,0x15c,0x3c, 0};
    offsets[2] = {0xb08,0x134,0x3c,0xc};
    offsets[3] = {0xb08,0x134,0x3c,8};
    offsets[4] = {0xb08,0x18c,0x15c,0x3c,0x2c};
    offsets[5] = {0xb08,0x18c,0x15c,0x3c,0x10};

    cout << "Enter expect values(-1 for no change)\n";
    for(int i=0;i<offsets.size();i++){
        float in;
        cout << name[i] << ": "; cin >> in;
        update_proc_detection();
        get_base_address();
        if(!procOpened){
            cout << "Process closed, abort\n";
            break;
        }
        HackMemory<float> resource(base_address[i], offsets[i], in);
        resource.modify();
    }
    print_info();
    cout << "Done!\n";
    system("pause");
}
/*-----------------------------------------------------------------------*
 *  > Terminate
 *-----------------------------------------------------------------------*/
void process_terminate(){
    running = false;
}
