#include "Trainer.h"
#include "Utility.inl"
#include "HackMemory.inl"
#include "Trainer.inl"

int keyboard_timer[0xff] = {0};
HWND HGameWindow, hwndThis;
bool running, procOpened, refresh_needed, connect_needed;
bool initialized = false;
bool show_debug_info_list = false;
DWORD procID, modBaseAddress;
HANDLE procHandle;
map<DWORD, DWORD> hotkey_id_table;

/*-----------------------------------------------------------------------*
 *  > Main process
 *-----------------------------------------------------------------------*/
int main(){
    hwndThis = GetForegroundWindow();
    initialize();
    auto LastUpdateTime = -0xffff;
    while(running){
        update_proc_detection();
        get_base_address();

        if(procOpened){
            realloc_memories();
            update_values();
        }

        if(GetForegroundWindow() == hwndThis){
            update_input();
            bool request_refresh = refresh_needed;
            request_refresh &= (LastUpdateTime + min_refresh_timer < clock());
            request_refresh |= (LastUpdateTime + refresh_timer < clock());
            if(request_refresh){
                initialized = true;
                utility::debug_pause();
                LastUpdateTime = clock();
                print_info();
                refresh_needed = false;
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

    if(keys[VK_F9]){
        keyboard_timer[VK_F9] = KeyCooldown;
        show_debug_info_list ^= true;
        cout << "Show debug info: ";
        cout << (show_debug_info_list ? "yes" : "no") << endl;
        system("CLS");
        refresh_needed = true;
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
    if(!HGameWindow){connect_needed = true; return ;}

    GetWindowThreadProcessId(HGameWindow, &procID);
    if(!procID){connect_needed = true; return ;}

    procHandle = OpenProcess(PROCESS_ALL_ACCESS, false, procID);

    if(procHandle == INVALID_HANDLE_VALUE || procHandle == NULL){
        connect_needed = true; return ;
    }

    procOpened = true;
}
/*-----------------------------------------------------------------------*
 *  > Get static pointer address when process detected
 *-----------------------------------------------------------------------*/
void get_base_address(){
    if(!procOpened)return ;
    if(!connect_needed)return ;
    connect_needed = false;
    cout << "Process ID: " << procID << endl;
    int time_out = 0;
    auto tempHandle = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, procID);
    tagMODULEENTRY32 tempMod;
    Module32First(tempHandle, &tempMod);
    modBaseAddress = (DWORD)tempMod.modBaseAddr;
    error_occurred = false;
    do{
        if(debugmode){
            cout << "Mod base address: " << (DWORD)tempMod.modBaseAddr << endl;
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
