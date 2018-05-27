#include <iostream>
#include <cstdio>
#include <vector>
#include <map>
#include <windows.h>
#include <cstring>
#include <time.h>
#include <tlhelp32.h>
#include <conio.h>

using namespace std;

const bool debugmode = false;

namespace utility{
    void debug_pause();
}

// Functions
void update_proc_detection();
void update_input();
void get_base_address();
void process_modification();
void process_terminate();
void print_info();

// Global variables
const string Version = "1.0.0";
const string Title = "AoK HD Trainer";
const LPSTR LGameWindow = "Age of Empires II: HD Edition";
const int FPS   = 60;
const int fwait = 1000 / FPS;
const int refresh_timer = 5000;

const DWORD supported_hotkeys[] = {0, VK_F1, VK_F2, VK_F3, 0x31};
const int HotkeySize = sizeof(supported_hotkeys) / sizeof(DWORD);
const int KeyCooldown = 60;

extern int keyboard_timer[0xff];
extern bool running;
extern bool procOpened;
extern bool refresh_needed;
extern bool error_occurred;
extern HWND HGameWindow, hwndThis;
extern DWORD procID, modBaseAddress;
extern HANDLE procHandle;

/**================================================================================*
 *  > HackMemory
 * --------------------------------------------------------------------------------
 *  The target value that need to change
 *================================================================================**/
template <typename T>
struct HackMemory{
    T value;
    DWORD hotkey;
    string message;
private:
    DWORD base_address;
    DWORD target_address;
    vector<DWORD> offsets;
    bool freeze, active;
public:
    HackMemory();
    HackMemory(DWORD, initializer_list<DWORD>, T _value = -1);
    void modify(T _value);
    void update();
    void toggle_active();
    void activate();
    void deactivate();
    bool is_active();
    void realloc_memory(DWORD, bool forced = false);
    T GetCurrentValue();
private:
    void init_base();
    void FindMemory();
};

template class HackMemory<DWORD>;
template class HackMemory<float>;

extern vector< HackMemory<float> > ResourcesStorage;
extern HackMemory<float> CurPopulation;
extern HackMemory<float> MaxPopulation;
extern HackMemory<float> RssCapacityPointer;
