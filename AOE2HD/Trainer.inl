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
    {0xc,0x154},                    // 8 Range indicator
};

vector<initializer_list<DWORD>> Attack_Offsets = {
    {0xc,0x14c,0x2},
    {0xc,0x14c,0x6},
    {0xc,0x14c,0xa},
    {0xc,0x14c,0xe},
};

vector<initializer_list<DWORD>> Armor_Offsets = {
    {0xc,0x144,0x2},
    {0xc,0x144,0x6},
    {0xc,0x144,0xa},
    {0xc,0x144,0xe},
};

const int HackDataSize = Offsets.size();
vector< HackMemory<float> > ResourcesStorage(4);
vector< HackMemory<WORD> >  AttackPointer(4);
vector< HackMemory<WORD> >  ArmorPointer(4);
HackMemory<float> CurPopulation(procHandle, 0x0, Offsets[4]);
HackMemory<float> MaxPopulation(procHandle, 0x0, Offsets[5]);
HackMemory<float> RssCapacityPointer(procHandle, 0x0, Offsets[6]);
HackMemory<float> HPPointer(procHandle, 0x0, Offsets[7]);
HackMemory<float> RangePointer(procHandle, 0x0, Offsets[8]);

// Modify value according to id
void process_modification(int id){
    cin.clear();
    cout << SplitLine;
    Sleep(100);

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
        cout << "Freeze this value will also change the value of any unit you selected afterward.\n";
        process_numeric_modification(RangePointer, true);
    }
    else if(id == 7){
        cout << "Value found: \n";
        for(int i=0;i<4;i++){
            cout << i+1 << ". " << AttackPointer[i].GetCurrentValue() << '\n';
        }
        int id = 0;
        do{
            cout << "Which one is correct attack damage?: ";
            cin >> id;
        }while(id < 1 || id > 4);
        process_numeric_modification(AttackPointer[id-1], false);
    }
    else if(id == 8){
        cout << "Value found: \n";
        for(int i=0;i<4;i++){
            cout << i+1 << ". " << ArmorPointer[i].GetCurrentValue() << '\n';
        }

        int id = 0;
        do{
            cout << "Which one is correct melee armor?: ";
            cin >> id;
        }while(id < 1 || id > 4);
        process_numeric_modification(ArmorPointer[id-1], false);
        cout << endl;
        do{
            cout << "Which one is correct pierce armor?: ";
            cin >> id;
        }while(id < 1 || id > 4);
        process_numeric_modification(ArmorPointer[id-1], false);
    }
    refresh_needed = true;
}


int last_sum = -1;
vector< reference_wrapper<HackMemory<float>> > fvalues_to_update = {
    ref(ResourcesStorage[0]), ref(ResourcesStorage[1]),
    ref(ResourcesStorage[2]), ref(ResourcesStorage[3]),
    ref(CurPopulation), ref(MaxPopulation),
    ref(RssCapacityPointer), ref(HPPointer), ref(RangePointer),
};

// Update frozen values
void update_values(){
    int sum = 0;
    for(auto ptr:fvalues_to_update){
        ptr.get().update();
        sum += ptr.get().GetCurrentValue();
    }

    for(int i=0;i<4;i++){
        AttackPointer[i].update();
        ArmorPointer[i].update();
    }

    if(last_sum != sum){
        refresh_needed = true;
        last_sum = sum;
    }
}

// Rescans
void realloc_memories(){
    auto forced = 1;
    auto base_addr = RESBaseAddress[0], base_addr2 = RESBaseAddress[1];
    for(int i=0;i<4;i++){
        ResourcesStorage[i].realloc_memory(procHandle, base_addr, forced);
        AttackPointer[i].realloc_memory(procHandle, base_addr2, forced);
        ArmorPointer[i].realloc_memory(procHandle, base_addr2, forced);
    }

    CurPopulation.realloc_memory(procHandle, base_addr, forced);
    MaxPopulation.realloc_memory(procHandle, base_addr, forced);
    RssCapacityPointer.realloc_memory(procHandle, base_addr, forced);
    HPPointer.realloc_memory(procHandle, base_addr, forced);
    RangePointer.realloc_memory(procHandle, base_addr2, forced);

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
    for(int i=0;i<4;i++){
        HackMemory<WORD> attack(procHandle, 0x0, Attack_Offsets[i], -1);
        AttackPointer[i] = attack;
        AttackPointer[i].message = "\nPlease enter the attack damage you wanna set: ";

        HackMemory<WORD> armor(procHandle, 0x0, Armor_Offsets[i], -1);
        ArmorPointer[i] = armor;
        ArmorPointer[i].message = "\nPlease enter the armor value you want: ";
    }
    CurPopulation.message = "\nPlease enter the number of current population you want to change to: ";
    MaxPopulation.message = "\nPlease enter the number you desire: ";
    RssCapacityPointer.message = "\nPlease enter the number you want to change to: ";
    HPPointer.message = "\nPlease enter the value you want(buildings can't excess max hp): ";
    RangePointer.message = "\nPlease enter the desired range: ";
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
