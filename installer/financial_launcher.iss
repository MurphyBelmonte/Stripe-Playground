; Inno Setup script for Financial Command Center AI
; Requires Inno Setup (ISCC.exe). Build with:
;   iscc installer\financial_launcher.iss

#define MyAppName "Financial Command Center AI"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Financial Command Center"
#define MyAppExeName "Financial-Command-Center-Launcher.exe"

[Setup]
AppId={{C1A9F8C9-0E8D-4F0B-9D6C-FFC-LAUNCHER}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=Financial-Command-Center-Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=assets\launcher_icon.ico
WizardStyle=modern

[Files]
; Ensure you've run build_launcher.py so dist contains the EXE
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "Launch-Financial-Command-Center.cmd"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

