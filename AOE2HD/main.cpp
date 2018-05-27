#include "main.h"

int keyboard_timer[0xff] = {0};
HWND HGameWindow, hwndThis;
bool running, procOpened, refresh_needed, connet_needed;
DWORD procID, modBaseAddress;

vector<DWORD> StaticOffset = {0x6DC5C0};
vector<DWORD> RESBaseAddress(StaticOffset.size());
const int BaseAddSize = RESBaseAddress.size();

vector<initializer_list<DWORD>> Offsets = {
    {0xb08,0x134,0x3c,0x4},         // 0 wood
    {0xb08,0x18c,0x15c,0x3c, 0},    // 1 food
    {0xb08,0x134,0x3c,0xc},         // 2 gold
    {0xb08,0x134,0x3c,8},           // 3 stone
    {0xb08,0x18c,0x15c,0x3c,0x2c},  // 4 current population
    {0xb08,0x18c,0x15c,0x3c,0x10},  // 5 max population
    {0xd5c,0x48},                   // 6 resource capacity pointer

};

const int HackDataSize = Offsets.size();
vector< HackMemory<float> > ResourcesStorage(4);
HackMemory<float> CurPopulation(0x0, Offsets[4], 0);
HackMemory<float> MaxPopulation(0x0, Offsets[5], 2000);
HackMemory<float> RssCapacityPointer(0x0, Offsets[6], 0xffff);

map<DWORD, DWORD> hotkey_id_table;

// Modify value according to id
void process_modification(int id){
    cin.clear();
    Sleep(100);
    if(id == 0){return ;}
    else if(id == 1){
        float input;
        for(int i=0;i<4;i++){
            cout << ResourcesStorage[i].message;
            cin >> input;
            ResourcesStorage[i].modify(input);
        }
    }
    else if(id == 2){
        cout << CurPopulation.message << endl;
        CurPopulation.toggle_active();
        system("pause");
    }
    else if(id == 3){
        float input;
        cout << MaxPopulation.message;
        cin >> input;
        MaxPopulation.modify(input);
    }
    else if(id == 4){
        float input;
        cout << RssCapacityPointer.message;
        cin >> input;
        RssCapacityPointer.modify(input);
    }
    refresh_needed = true;
}

// Update frozen values
void update_values(){
    if(CurPopulation.is_active()){
        CurPopulation.update();
    }
}

// Rescans
void realloc_memories(){
    auto base_addr = RESBaseAddress[0];
    for(int i=0;i<4;i++){
        ResourcesStorage[i].realloc_memory(base_addr, true);
    }
    CurPopulation.realloc_memory(base_addr, true);
    MaxPopulation.realloc_memory(base_addr, true);
    RssCapacityPointer.realloc_memory(base_addr, true);
}
/*-----------------------------------------------------------------------*
 *  > HackMemory initialization
 *-----------------------------------------------------------------------*/
void init_hack_values(){
    string msg[] = {"Wood: ", "Food: ", "Gold: ", "Stone: "};
    for(int i=0;i<4;i++){
        HackMemory<float> resources(0x0, Offsets[i], 8000);
        ResourcesStorage[i] = resources;
        ResourcesStorage[i].message = msg[i];
    }
    CurPopulation.message = "\nYour Current population will lock at 0\n";
    MaxPopulation.message = "\nPlease enter the number you desire: ";
    RssCapacityPointer.message = "\nPlease enter the number you want to change to: ";
}

/*-----------------------------------------------------------------------*
 *  > Global variable initialization
 *-----------------------------------------------------------------------*/
void initialize(){
    running        = true;
    procOpened     = false;
    refresh_needed = true;
    connet_needed  = true;
    HGameWindow    = NULL;
    procID         = NULL;
    procHandle     = NULL;

    for(int i=0;i<HotkeySize;i++){
        hotkey_id_table[ supported_hotkeys[i] ] = i;
    }

    init_hack_values();
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
            getch();
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
    cout << procID << endl;
    int time_out = 0;
    auto tempHandle = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, procID);
    tagMODULEENTRY32 tempMod;
    Module32First(tempHandle, &tempMod);
    modBaseAddress = (DWORD)tempMod.modBaseAddr;
    error_occurred = false;
    do{
        // Don't move this line!!!
        cout << "Mod base address: " << (DWORD)tempMod.modBaseAddr << endl;
        if(debugmode){
            utility::debug_pause();
        }
        if(modBaseAddress < 0x10){
            Module32Next(tempHandle, &tempMod);
            modBaseAddress = (DWORD)tempMod.modBaseAddr;
        }
    }while(modBaseAddress < 0x10 && time_out++ < 10);
    if(modBaseAddress < 0x10){error_occurred = true;}
    if(debugmode){
        printf("Base module address: %x\n", modBaseAddress);
    }

    for(int i=0;i<BaseAddSize;i++){
        RESBaseAddress[i] = modBaseAddress + StaticOffset[i];
        if(debugmode){
            printf("RESBaseAddress[%d]: %x + %x = %x\n", i, modBaseAddress, StaticOffset[i], RESBaseAddress[i]);
        }
    }
    utility::debug_pause();
    refresh_needed = true;
}
/*-----------------------------------------------------------------------*
 *  > Terminate
 *-----------------------------------------------------------------------*/
void process_terminate(){
    running = false;
}

