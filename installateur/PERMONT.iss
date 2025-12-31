; Script Inno Setup pour PERIMONT_ERP
; Créé le 31/12/2025

[Setup]
; Informations sur l'application
AppName=PERIMONT_ERP
AppVersion=1.0
AppPublisher=Gaël
DefaultDirName={autopf}\PERIMONT_ERP
DefaultGroupName=PERIMONT_ERP
; Icône de l'installateur et de l'application dans le menu désinstallation
SetupIconFile=C:\PERIMONT_ERP\assets\logo.ico
UninstallDisplayIcon={app}\PERIMONT_ERP.exe
; Où sera enregistré le fichier d'installation final (.exe)
OutputDir=C:\PERIMONT_ERP\installateur
OutputBaseFilename=PERIMONT_ERP_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; L'exécutable principal
Source: "C:\PERIMONT_ERP\dist\PERIMONT_ERP\PERIMONT_ERP.exe"; DestDir: "{app}"; Flags: ignoreversion
; Tous les fichiers et dossiers générés par PyInstaller
Source: "C:\PERIMONT_ERP\dist\PERIMONT_ERP\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Note : Inno Setup ignorera les doublons de l'exécutable principal grâce aux flags.

[Icons]
Name: "{group}\PERIMONT_ERP"; Filename: "{app}\PERIMONT_ERP.exe"
Name: "{autodesktop}\PERIMONT_ERP"; Filename: "{app}\PERIMONT_ERP.exe"; Tasks: desktopicon

[Run]
; Option pour lancer l'application immédiatement après l'installation
Filename: "{app}\PERIMONT_ERP.exe"; Description: "{cm:LaunchProgram,PERIMONT_ERP}"; Flags: nowait postinstall skipifsilent