#include <iostream>
#include <cstdio>
#include <vector>
#include <map>
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
void update_values();

// Global variables
const string Version = "1.0.0";
const string Title = "Kingdom Classic Trainer";
const LPSTR LGameWindow = "Kingdom";
const int FPS   = 60;
const int fwait = 1000 / FPS;
const int refresh_timer = 5000;
bool running, procOpened, refresh_needed, connet_needed, focused;

DWORD supported_hotkeys[] = {0, VK_F1, VK_F2, VK_F3, VK_F4, VK_F5, VK_F6};
const int HotkeySize = sizeof(supported_hotkeys) / sizeof(DWORD);
const int KeyCooldown = 60;
int keyboard_timer[0xff] = {0};

HWND HGameWindow, hwndThis;
DWORD procID;
HANDLE procHandle;

/**================================================================================*
 *  > HackMemory
 * --------------------------------------------------------------------------------
 *  The target value that need to change
 *================================================================================**/
template <typename T>
struct HackMemory{
    /*-----------------------------------------------------------------------*
     *  > Instance Variable
     *-----------------------------------------------------------------------*/
    T value;
    DWORD hotkey;
private:
    DWORD base_address;
    DWORD target_address;
    vector<DWORD> offsets;
    bool freeze, active;
    /*-----------------------------------------------------------------------*
     *  > Object initialization
     *-----------------------------------------------------------------------*/
public:
    HackMemory(){base_address = 0;}
    HackMemory(DWORD base, initializer_list<DWORD> _offsets, T _value = -1){
        base_address = base;
        value = _value;
        for(auto offset:_offsets){
            offsets.push_back(offset);
        }
        hotkey = 0;
        freeze = false;
        active = false;
        FindMemory();
    }
    /*-----------------------------------------------------------------------*
     * > Rescan final memory address
     *-----------------------------------------------------------------------*/
    void realloc_memory(DWORD base){
        if(base_address == base)return ;
        base_address = base;
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
     *  > Return current value
     *-----------------------------------------------------------------------*/
    T GetCurrentValue(){
        if(!base_address){return 0;}
        T target_value;
        ReadProcessMemory(procHandle, (BYTE*)target_address, &target_value,
                          sizeof(target_value), NULL);
        return target_value;
    }
    /*-----------------------------------------------------------------------*
     *  > Modification implement
     *-----------------------------------------------------------------------*/
    void modify(T _value = -1){
        value = _value == -1 ? value : _value;
        if(value == -1)return ;

        auto target_value = GetCurrentValue();
        if(target_value == value)return ;
        if(debugmode){
            printf("Base/Target Address: %x/%x\n", base_address, target_address);
            cout << "Base/Target Value: " << target_value << " / " << value << endl;
        }
        WriteProcessMemory(procHandle,(BYTE*)target_address, &value,
                           sizeof(value), NULL);
    }
    /*-----------------------------------------------------------------------*
    *  > Frame update
    *-----------------------------------------------------------------------*/
    void update(){
        if(freeze){modify();}
    }
    /*-----------------------------------------------------------------------*
    *  > Switch activity
    *-----------------------------------------------------------------------*/
    void toggle_active(){
        active ? deactivate() : activate();
        refresh_needed = true;
    }
    /*-----------------------------------------------------------------------*
    *  > Set active
    *-----------------------------------------------------------------------*/
    void activate(){
        active = freeze = true;
    }
    /*-----------------------------------------------------------------------*
    *  > Set inactive
    *-----------------------------------------------------------------------*/
    void deactivate(){
        active = freeze = false;
    }
    /*-----------------------------------------------------------------------*
    *  > Check whether this hack is active
    *-----------------------------------------------------------------------*/
    bool is_active(){
        return active;
    }
};

vector<DWORD> RESBaseAddress;
vector<DWORD> StaticOffset = {0xEA1CC8, 0xEF5574};

vector<initializer_list<DWORD>> Offsets = {
    {0x128,0x704,0x30,0x270,0x90},
    {0x128,0x704,0x30,0x4b0,0x8c},
    {0x8,0x4,0x10,0x0,0x8,0x14,0x3c},
};
const int HackDataSize = Offsets.size();

HackMemory<float> Stamina(0x0, Offsets[0], 1);
HackMemory<DWORD> Coin(0x0, Offsets[1], 20);
HackMemory<DWORD> CurrentDay(0x0, Offsets[2], 1);
map<DWORD, DWORD> hotkey_id_table;

// Modify value according to id
void process_modification(int id){
    if(id == 0){return ;}
    else if(id == 1){Stamina.toggle_active();}
    else if(id == 2){Coin.toggle_active();}
    else if(id == 3){
        cout << "\nPlease enter a day you want to chage: ";
        DWORD new_day;
        cin >> new_day;
        CurrentDay.modify(new_day);
        cout << "Done!\n";
        system("pause");
        refresh_needed = true;
    }
}

// Update frozen values
void update_values(){
    Stamina.update();
    Coin.update();
}

// Rescans
void realloc_memories(){
    Stamina.realloc_memory(RESBaseAddress[0]);
    Coin.realloc_memory(RESBaseAddress[0]);
    CurrentDay.realloc_memory(RESBaseAddress[1]);
}
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

    for(int i=0;i<HotkeySize;i++){
        hotkey_id_table[ supported_hotkeys[i] ] = i;
    }
}
/*-----------------------------------------------------------------------*
 *  > Print program information
 *-----------------------------------------------------------------------*/
void print_info(){
    system("CLS");
    std::cout << "Name: " << Title << '\n';
    std::cout << "Version: " << Version << '\n';
    std::cout << "*---------------------------------> Information <---------------------------------*\n";
    std::cout << "* This application give you unlimited stamina, coins and current day hack. Happy  *\n";
    std::cout << "* farming!                                                                        *\n";
    std::cout << "*                Programmed by Compeador(https://github.com/ken1882)              *\n";
    std::cout << "*---------------------------------------------------------------------------------*\n";
    std::cout << "*                                 > User Guide  <                                 *\n";
    std::cout << "*---------------------------------------------------------------------------------*\n";
    std::cout << "* After you start/load a game in Kingdom: Classic, open up this window then start *\n";
    std::cout << "* the hacks. F1 for infinite stamina and F2 for unlimited coins(precisely, you    *\n";
    std::cout << "* will forever have 20 coins in your bag). F3 to change current day of game.      *\n";
    std::cout << "*                                                                                 *\n";
    std::cout << "* If you think it's done, press alt+ESC to close this window.                     *\n";
    std::cout << "*---------------------------------------------------------------------------------*\n";
    cout << endl;
    cout << "Process [" << LGameWindow << "] >> ";
    cout << (procOpened ? "Ready" : "Not detected") << '\n';

    if(procOpened){
        cout << "[F1] Stamina Hack: ";
        cout << (Stamina.is_active() ? "Enabled" : "Disabled") << '\n';
        cout << "[F2] Coin Hack: ";
        cout << (Coin.is_active() ? "Enabled" : "Disabled") << '\n';
        cout << "[F3] Change current day (Now is Day ";
        cout << CurrentDay.GetCurrentValue() << ")\n";
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

        if(procOpened){
            update_values();
            realloc_memories();
        }

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
        if(keyboard_timer[i] > 0){
            keyboard_timer[i] -= 1;
        }
    }

    if(keys[VK_MENU] && keys[VK_ESCAPE]){
        process_terminate();
    }

    if(!procOpened)return ;
    for(int i=0;i<HotkeySize;i++){
        DWORD vk = supported_hotkeys[i];
        if(keys[vk] && !keyboard_timer[vk]){
            keyboard_timer[vk] = KeyCooldown;
            process_modification(hotkey_id_table[vk]);
        }
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

    int n = StaticOffset.size();
    for(int i=0;i<n;i++){
        DWORD add = (DWORD)tempMod.modBaseAddr + StaticOffset[i];
        RESBaseAddress.push_back(add);
    }
    refresh_needed = true;
}

/*-----------------------------------------------------------------------*
 *  > Terminate
 *-----------------------------------------------------------------------*/
void process_terminate(){
    running = false;
}
