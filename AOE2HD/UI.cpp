#include "Trainer.h"
#include "Utility.inl"
#include "HackMemory.inl"

bool error_occurred;

void print_value_info(){
    cout << SplitLine;
    cout << "Value information:\n\n";

    for(int i=0;i<4;i++){
        string msg = ResourcesStorage[i].message;
        ResourcesStorage[i].show_status(msg);
    }

    CurPopulation.show_status("Current Population: ");
    MaxPopulation.show_status("Max Population: ");

    cout << "*======|Current Status of selected unit|======*\n";
    HPPointer.show_status("HP: ");
    cout << "*** Below stats not applied to enemy ***\n";
    RangePointer.show_status("Range: ");
    cout << "Attack: [";
    for(int i=0;i<4;i++){
        cout << AttackPointer[i].GetCurrentValue();
        if(i<3)cout << ',';
    }
    cout << "]\n";
    cout << "Armor: [";
    for(int i=0;i<4;i++){
        cout << ArmorPointer[i].GetCurrentValue();
        if(i<3)cout << ',';
    }
    cout << "]\n";
    RssCapacityPointer.show_status("Resource carried: ");
    cout << SplitLine << endl;
}

/*-----------------------------------------------------------------------*
 *  > Print program information
 *-----------------------------------------------------------------------*/
void print_info(){
    system("CLS");
    std::cout << "Name: " << Title << '\n';
    std::cout << "Version: " << Version << '\n';
    std::cout << "*---------------------------------> Information <---------------------------------*\n";
    std::cout << "* This application can change the value of wood, food, gold, stone, population    *\n";
    std::cout << "* hack and unit resources capacity hack.                                          *\n";
    std::cout << "*                Programmed by Compeador(https://github.com/ken1882)              *\n";
    std::cout << "*---------------------------------------------------------------------------------*\n";
    std::cout << "*                                 > User Guide  <                                 *\n";
    std::cout << "*---------------------------------------------------------------------------------*\n";
    std::cout << "* After you start/load a game in AOE2 HD, open up this window then press key that *\n";
    std::cout << "* shows in the window, each accorded to a feature, enjoy!                         *\n";
    std::cout << "* When entering a value, enter -1 for no change.                                  *\n";
    std::cout << "* If you think it's done, press alt+ESC to close this window.                     *\n";
    std::cout << "*---------------------------------------------------------------------------------*\n";
    cout << endl;
    cout << "Process [" << LGameWindow << "] >> ";
    cout << (procOpened ? "Ready" : "Not detected") << '\n';
    if(error_occurred){
        cout << ">> An error occurred during detect memories, please restart the program later <<\n";
    }
    if(procOpened){
        cout << "Process ID: " << procID << endl;
        print_value_info();
        cout << "[F1] Hack resources\n";
        cout << "[F2] Hack current population\n";
        cout << "[F3] Hack max population\n";
        cout << "[1]  Hack resource capacity of current selected unit\n";
        cout << "[2]  Hack HP of selected unit\n";
        cout << "[3]  Hack attack range of selected unit\n";
        cout << "[4]  Hack attack damage of selected unit\n";
        cout << "[5]  Hack armor of selected unit\n";

    }
}

void utility::debug_pause(){
    if(debugmode){
        system("pause");
        puts("");
    }
}
