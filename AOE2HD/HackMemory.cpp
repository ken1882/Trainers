#include "main.h"

HANDLE procHandle;

/**================================================================================*
 *  > HackMemory
 * --------------------------------------------------------------------------------
 *  The target value that need to change
 *================================================================================**/
/*-----------------------------------------------------------------------*
 *  > Object initialization
 *-----------------------------------------------------------------------*/
template <typename T>
HackMemory<T>::HackMemory(){init_base();}

template <typename T>
HackMemory<T>::HackMemory(DWORD base, initializer_list<DWORD> _offsets, T _value){
    init_base();
    base_address = base;
    value = _value;
    offsets.clear();
    for(auto offset:_offsets){
        offsets.push_back(offset);
    }
    if(base){FindMemory();}
}
/*-----------------------------------------------------------------------*
 *  > Init base variables
 *-----------------------------------------------------------------------*/
template <typename T>
void HackMemory<T>::init_base(){
    base_address = 0;
    hotkey  = 0;
    freeze  = false;
    active  = false;
    message = "";
}
/*-----------------------------------------------------------------------*
 *  > Rescan memory
 *-----------------------------------------------------------------------*/
template <typename T>
void HackMemory<T>::realloc_memory(DWORD base, bool forced){
    if(base_address == base && !forced)return ;
    base_address = base;
    FindMemory();
}
/*-----------------------------------------------------------------------*
 *  > Find target final address
 *-----------------------------------------------------------------------*/
template <typename T>
void HackMemory<T>::FindMemory(){
    DWORD temp;
    target_address = base_address;
    ReadProcessMemory(procHandle, (LPCVOID) target_address, &temp,
                        sizeof(temp), NULL);
    if(debugmode){
        printf("Track final address from %x -> %x\n", base_address, temp);
    }
    int _size = offsets.size();
    for(int i=0;i<_size;i++){
        target_address = temp + offsets[i];
        if(debugmode){
            printf("%x + %x => %x\n", temp, offsets[i], target_address);
        }
        ReadProcessMemory(procHandle, (LPCVOID)target_address, &temp,
                            sizeof(temp), NULL);
    }
    utility::debug_pause();
}
/*-----------------------------------------------------------------------*
 *  > Get current value
 *-----------------------------------------------------------------------*/
template <typename T>
T HackMemory<T>::GetCurrentValue(){
    if(!base_address){return 0;}
    T target_value;
    ReadProcessMemory(procHandle, (BYTE*)target_address, &target_value,
                        sizeof(target_value), NULL);
    return target_value;
}
/*-----------------------------------------------------------------------*
 *  > Modify value
 *-----------------------------------------------------------------------*/
template <typename T>
void HackMemory<T>::modify(T _value){
    if(_value == -1)return ;
    value = _value;

    auto target_value = GetCurrentValue();
    if(target_value == value)return ;
    if(debugmode){
        printf("Base/Target Address: %x/%x\n", base_address, target_address);
        cout << "Base/Target Value: " << target_value << " / " << value << endl;
        utility::debug_pause();
    }
    WriteProcessMemory(procHandle,(BYTE*)target_address, &value,
                        sizeof(value), NULL);
}
/*-----------------------------------------------------------------------*
 *  > Frame update
 *-----------------------------------------------------------------------*/
template <typename T>
void HackMemory<T>::update(){
    if(freeze){modify(value);}
}
/*-----------------------------------------------------------------------*
 *  > Switch activity
 *-----------------------------------------------------------------------*/
template <typename T>
void HackMemory<T>::toggle_active(){
    active ? deactivate() : activate();
    refresh_needed = true;
}
/*-----------------------------------------------------------------------*
 *  > Set active
 *-----------------------------------------------------------------------*/
template <typename T>
void HackMemory<T>::activate(){
    active = freeze = true;
}
/*-----------------------------------------------------------------------*
 *  > Set inactive
 *-----------------------------------------------------------------------*/
template <typename T>
void HackMemory<T>::deactivate(){
    active = freeze = false;
}
/*-----------------------------------------------------------------------*
 *  > Check whether this hack is active
 *-----------------------------------------------------------------------*/
template <typename T>
bool HackMemory<T>::is_active(){
    return active;
}
