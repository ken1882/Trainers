#include "Trainer.h"
#include "Utility.inl"
#include "HackMemory.inl"

vector<DWORD> StaticOffset = {0x6DC5C0, 0x6DD670};
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
    {0xd5c,0x34},                   // 7 HP indicator
};

vector<initializer_list<DWORD>> RangeOffsets = {
    {0xc,0x154},                    // 0 Castle
};

const int HackDataSize = Offsets.size();
vector< HackMemory<float> > ResourcesStorage(4);
vector< HackMemory<float> > Range(20);
HackMemory<float> CurPopulation(procHandle, 0x0, Offsets[4]);
HackMemory<float> MaxPopulation(procHandle, 0x0, Offsets[5]);
HackMemory<float> RssCapacityPointer(procHandle, 0x0, Offsets[6]);
HackMemory<float> HPPointer(procHandle, 0x0, Offsets[7]);

// Modify value according to id
void process_modification(int id){
    cin.clear();
    cout << SplitLine;
    Sleep(100);
    float input_f = -1;
    if(id == 0){return ;}
    else if(id == 1){
        for(int i=0;i<4;i++){
            process_numeric_modification(ResourcesStorage[i], true);
        }
    }
    else if(id == 2){
        process_numeric_modification(CurPopulation, true);
    }
    else if(id == 3){
        process_numeric_modification(MaxPopulation, true);
    }
    else if(id == 4){
        cout << "Freeze this value will also change the value of any unit you selected afterward.\n";
        process_numeric_modification(RssCapacityPointer, true);
    }
    else if(id == 5){
        cout << "Freeze this value will also change the value of any unit you selected afterward.\n";
        process_numeric_modification(HPPointer, true);
    }
    else if(id == 6){
        int _id;
        for(int i=0;i<RangeOffsets.size();i++){
            printf("%02d: %s\n", i, Range[i].message.c_str());
        }
        cout << "Enter a unit id: "; cin >> _id;
        if(_id < 0 || _id >= RangeOffsets.size()){
            cout << "Invalid ID\n";
            system("pause");
        }
        else{
            string msg = "Enter a range value: ";
            process_numeric_modification(Range[_id], false, msg);
        }
    }
    refresh_needed = true;
}


int last_sum = -1;
// Update frozen values
void update_values(){
    int sum = 0;
    for(int i=0;i<4;i++){
        ResourcesStorage[i].update();
        sum += ResourcesStorage[i].GetCurrentValue();
    }

    CurPopulation.update();
    sum += CurPopulation.GetCurrentValue();

    MaxPopulation.update();
    sum += MaxPopulation.GetCurrentValue();

    RssCapacityPointer.update();
    sum += RssCapacityPointer.GetCurrentValue();

    HPPointer.update();
    sum += HPPointer.GetCurrentValue();
    if(last_sum != sum){
        refresh_needed = true;
        last_sum = sum;
    }
}

// Rescans
void realloc_memories(){
    auto forced = 1;
    auto base_addr = RESBaseAddress[0];
    for(int i=0;i<4;i++){
        ResourcesStorage[i].realloc_memory(procHandle, base_addr, forced);
    }
    CurPopulation.realloc_memory(procHandle, base_addr, forced);
    MaxPopulation.realloc_memory(procHandle, base_addr, forced);
    RssCapacityPointer.realloc_memory(procHandle, base_addr, forced);
    HPPointer.realloc_memory(procHandle, base_addr, forced);

    for(int i=0;i<RangeOffsets.size();i++){
        Range[i].realloc_memory(procHandle, RESBaseAddress[1], forced);
    }
}
/*-----------------------------------------------------------------------*
 *  > HackMemory initialization
 *-----------------------------------------------------------------------*/
void init_hack_values(){
    string msg[] = {"Wood: ", "Food: ", "Gold: ", "Stone: "};
    for(int i=0;i<4;i++){
        HackMemory<float> resources(procHandle, 0x0, Offsets[i], 8000);
        ResourcesStorage[i] = resources;
        ResourcesStorage[i].message = msg[i];
    }

    string name[] = {"Castle", "Tower", };
    for(int i=0;i<RangeOffsets.size();i++){
        HackMemory<float> range(procHandle, 0x0, RangeOffsets[i]);
        Range[i] = range;
        Range[i].message = name[i];
    }

    CurPopulation.message = "\nPlease enter the number of current population you want to change to: ";
    MaxPopulation.message = "\nPlease enter the number you desire: ";
    RssCapacityPointer.message = "\nPlease enter the number you want to change to: ";
    HPPointer.message = "\nPlease enter the value you want(buildings can't excess max hp): ";
}

/*-----------------------------------------------------------------------*
 *  > Global variable initialization
 *-----------------------------------------------------------------------*/
void initialize(){
    running        = true;
    procOpened     = false;
    refresh_needed = true;
    connect_needed = true;
    HGameWindow    = NULL;
    procID         = NULL;
    procHandle     = NULL;

    for(int i=0;i<HotkeySize;i++){
        hotkey_id_table[ supported_hotkeys[i] ] = i;
    }

    init_hack_values();
}
