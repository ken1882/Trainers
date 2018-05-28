#ifndef COMP_TRAINER
#define COMP_TRAINER

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

/**================================================================================*
 *  > HackMemory
 * --------------------------------------------------------------------------------
 *  The target value that need to change
 *================================================================================**/
template <typename T>
struct HackMemory{
    T value, value_frozen;
    DWORD hotkey;
    string message;
    HANDLE procHandle;
private:
    DWORD base_address;
    DWORD target_address;
    vector<DWORD> offsets;
    bool freeze, active;
public:
    HackMemory();
    HackMemory(HANDLE, DWORD, initializer_list<DWORD>, T _value = -1);
    void modify(T _value);
    void update();
    void toggle_active();
    void activate();
    void deactivate();
    bool is_active();
    void realloc_memory(HANDLE, DWORD, bool forced = false);
    T GetCurrentValue();
    void show_status(string);
private:
    void init_base();
    void FindMemory();
};

// Global variables
const string Version = "1.0.0";
const string Title = "AoK HD Trainer";
const string SplitLine = "*---------------------------------------------------------------------------------*\n";
const LPSTR LGameWindow = "Age of Empires II: HD Edition";
const int FPS   = 24;
const int fwait = 1000 / FPS;
const int refresh_timer = 5000;
const int min_refresh_timer = 1000;

const int min_valid_value = -0x0fffffff;
const int max_valid_value = INT_MAX;

const DWORD supported_hotkeys[] = {0, VK_F1, VK_F2, VK_F3, 0x31, 0x32, 0x33, 0x34, 0x35};
const int HotkeySize = sizeof(supported_hotkeys) / sizeof(DWORD);
const int KeyCooldown = 60;

extern int keyboard_timer[0xff];
extern bool running;
extern bool procOpened;
extern bool refresh_needed;
extern bool error_occurred;
extern bool connect_needed;
extern bool show_debug_info_list;
extern bool initialized;

extern HWND HGameWindow, hwndThis;
extern DWORD procID, modBaseAddress;
extern HANDLE procHandle;

extern vector< HackMemory<float> > ResourcesStorage;
extern vector< HackMemory<float> > Range;
extern HackMemory<float> CurPopulation;
extern HackMemory<float> MaxPopulation;
extern HackMemory<float> RssCapacityPointer;
extern HackMemory<float> HPPointer;

extern map<DWORD, DWORD> hotkey_id_table;

// Functions
void initialize();
void update_proc_detection();
void update_input();
void update_values();
void realloc_memories();
void process_modification();
void get_base_address();
void process_modification(int);
void process_terminate();
void print_value_info();
void print_info();

template <typename T>
bool is_numeric_legal(T);

template <typename T>
void process_numeric_modification(HackMemory<T>&,bool,string msg="");

template <typename T>
bool input_numeric(T&, bool, string message = ": ");

#endif // COMP_TRAINER
