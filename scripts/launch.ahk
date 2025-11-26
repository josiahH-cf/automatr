; Automatr Global Hotkey for Windows
; 
; This script provides a global hotkey (Ctrl+Shift+A) to focus or launch
; the Automatr application running in WSL2.
;
; Installation:
;   1. Install AutoHotkey v2: https://www.autohotkey.com/
;   2. Run this script (double-click or add to startup)
;
; Usage:
;   Press Ctrl+Shift+A from anywhere to:
;   - Focus the Automatr window if it's already open
;   - Launch Automatr in WSL2 if it's not running

#Requires AutoHotkey v2.0
#SingleInstance Force

; Global hotkey: Ctrl+Shift+A
^+a::
{
    ; Window title to look for
    windowTitle := "Automatr"
    
    ; Try to find and focus existing window
    if WinExist(windowTitle)
    {
        WinActivate
        return
    }
    
    ; Not found - try to launch via WSL2
    try
    {
        ; Method 1: Run via wsl.exe
        Run "wsl.exe -e automatr", , "Hide"
    }
    catch
    {
        try
        {
            ; Method 2: Run via wsl.exe with bash
            Run "wsl.exe bash -c 'automatr &'", , "Hide"
        }
        catch
        {
            ; Method 3: Run via Windows Terminal (if available)
            try
            {
                Run "wt.exe -d ~\ wsl.exe -e automatr"
            }
            catch
            {
                MsgBox "Failed to launch Automatr. Please ensure WSL2 is configured and automatr is installed."
            }
        }
    }
}

; Tray menu customization
A_TrayMenu.Delete  ; Remove default items
A_TrayMenu.Add("Automatr Hotkey", (*) => MsgBox("Press Ctrl+Shift+A to launch Automatr"))
A_TrayMenu.Add
A_TrayMenu.Add("Edit Script", (*) => Edit())
A_TrayMenu.Add("Reload", (*) => Reload())
A_TrayMenu.Add
A_TrayMenu.Add("Exit", (*) => ExitApp())

; Set tray tip
A_IconTip := "Automatr - Ctrl+Shift+A"
