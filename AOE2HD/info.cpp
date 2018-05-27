#include "main.h"

bool error_occurred;
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
    std::cout << "*                                                                                 *\n";
    std::cout << "* If you think it's done, press alt+ESC to close this window.                     *\n";
    std::cout << "*---------------------------------------------------------------------------------*\n";
    cout << endl;
    cout << "Process [" << LGameWindow << "] >> ";
    cout << (procOpened ? "Ready" : "Not detected") << '\n';
    if(error_occurred){
        cout << ">> An error occurred during detect memories, please restart the program later <<\n";
    }
    if(procOpened){
        cout << "Process ID: " << procID << endl << endl;
        cout << "[F1] Hack resources\n";
        cout << "[F2] Lock current population at 0 ";
        cout << (CurPopulation.is_active() ? "(enabled)" : "(disabled)") << '\n';
        cout << "[F3] Hack max population\n";
        cout << "[1]  Hack resource capacity of current selected unit\n";
    }
    refresh_needed = false;
}

void utility::debug_pause(){
    if(debugmode){
        system("pause");
        puts("");
    }
}
