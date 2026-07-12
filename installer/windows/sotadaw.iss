; SOTA DAW — Inno Setup script (SCAFFOLD, 2026-07-12: never yet compiled/run —
; the Windows binary itself does not exist until the CI windows job goes green).
; Produces the standard Windows install wizard: license page, dir choice,
; Start Menu + optional desktop icon, uninstaller.
[Setup]
AppName=SOTA DAW
AppVersion=0.9.0
AppPublisher=SOTA DAW
DefaultDirName={autopf}\SOTA DAW
DefaultGroupName=SOTA DAW
UninstallDisplayIcon={app}\bin\SOTA DAW.exe
LicenseFile=payload\THIRD_PARTY_LICENSES.md
OutputBaseFilename=SOTA_DAW_Setup_win64
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\..\app\build\sotadaw_artefacts\Release\SOTA DAW.exe"; DestDir: "{app}\bin"
Source: "..\..\app\build\m1_artefacts\Release\m1.exe"; DestDir: "{app}\bin"
Source: "payload\*"; DestDir: "{app}\payload"; Flags: recursesubdirs
Source: "python-embed\*"; DestDir: "{app}\python"; Flags: recursesubdirs skipifsourcedoesntexist
Source: "faust.dll"; DestDir: "{app}\bin"; Flags: skipifsourcedoesntexist
Source: "faustlibs\*"; DestDir: "{app}\faustlibs"; Flags: recursesubdirs skipifsourcedoesntexist
Source: "sotadaw-launch.cmd"; DestDir: "{app}"

[Icons]
Name: "{group}\SOTA DAW"; Filename: "{app}\sotadaw-launch.cmd"; IconFilename: "{app}\bin\SOTA DAW.exe"
Name: "{autodesktop}\SOTA DAW"; Filename: "{app}\sotadaw-launch.cmd"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon"

[Run]
Filename: "{app}\sotadaw-launch.cmd"; Description: "Launch SOTA DAW"; Flags: postinstall nowait skipifsilent
