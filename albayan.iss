#define MyAppName "Albayan"
#define MyAppVersion "1.3.0"
#define AppVersion "1.3.0"
#define MyAppPublisher "Tecwindow"
#define MyAppURL "https://tecwindow.net/"
#define MyAppExeName "Albayan.exe"


[Setup]
AppName={#MyAppName}
AppId={{5BDDE425-E22F-4A82-AF2F-72AF71301D3F}
AppVersion={#AppVersion}
;AppVersion={#MyAppVersion}
VersionInfoDescription=Albayan كل ما يخص الإسلام.
AppPublisher=tecwindow
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany=tecwindow
VersionInfoCopyright=copyright, ©2023; tecwindow
VersionInfoProductName=Albayan
VersionInfoProductVersion={#MyAppVersion}
VersionInfoOriginalFileName=Albayan_Setup.exe
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
ArchitecturesAllowed=x64

DefaultDirName={sd}\program files\tecwindow\{#MyAppName}
DisableProgramGroupPage=yes
; Uncomment the following line to run in non-administrative install mode (install for the current user only.)
PrivilegesRequired=admin
OutputDir=Albayan
OutputBaseFilename=AlbayanSetup
Compression=lzma
CloseApplications=force
restartApplications=yes
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=no

ArchitecturesInstallIn64BitMode=x64
MinVersion=0,6.2

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "Albayan\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "Albayan\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Audio\athkar\*"; DestDir: "{userappdata}\tecwindow\albayan\Audio\athkar"; Flags: ignoreversion recursesubdirs createallsubdirs

[CustomMessages]
arabic.AppLNGfile=Arabic

[Icons]
Name: "{autoprograms}\Albayan"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Albayan"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon


[INI]
Filename: "{userappdata}\tecwindow\{#MyAppName}\Settingss.ini"; Section: "General"; Key: "language"; String: "{cm:AppLNGfile}"

[UninstallDelete]
Type: filesandordirs; Name: "{pf}\tecwindow\Albayan"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall