#define MyAppName "Albayan"
#define MyAppVersion "4.0.0"
#define AppVersion "4.0.0"
#define MyAppPublisher "Tecwindow"
#define MyAppURL "https://tecwindow.net/"
#define MyAppExeName "Albayan.exe"

[Setup]
AppName={#MyAppName}
AppId={{5BDDE425-E22F-4A82-AF2F-72AF71301D3F}
AppVersion={#AppVersion}
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
ArchitecturesAllowed=x64compatible arm64
ArchitecturesInstallIn64BitMode=x64compatible arm64
SetupIconFile=Albayan.ico

DefaultDirName={sd}\program files\tecwindow\{#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=albayan_build
OutputBaseFilename=AlbayanSetup
Compression=lzma
CloseApplications=force
restartApplications=yes
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=no
MinVersion=0,6.2

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[CustomMessages]
arabic.AppLNGfile=Arabic
english.DeleteSettingsPrompt=Do you want to delete the settings folder?
arabic.DeleteSettingsPrompt=هل تريد حذف مجلد الإعدادات؟
english.autorun=auto start albayan with windows?
arabic.autorun=فتح برنامج البيان تلقائيا مع بدء تشغيل النظام

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autorun"; Description: "{cm:autorun}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "albayan_build\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "albayan_build\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "albayan_build\Audio\athkar\*"; DestDir: "{userappdata}\tecwindow\albayan\Audio\athkar"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Albayan"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Albayan.ico"
Name: "{autodesktop}\Albayan"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Albayan.ico"; Tasks: desktopicon

[INI]
Filename: "{userappdata}\tecwindow\{#MyAppName}\config.ini"; Section: "general"; Key: "run_in_background_enabled"; String: "true"; Tasks: autorun
Filename: "{userappdata}\tecwindow\{#MyAppName}\config.ini"; Section: "general"; Key: "auto_start_enabled"; String: "true"; Tasks: autorun

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "albayan"; ValueData: "{app}\albayan.exe --minimized"; Flags: uninsdeletevalue; Tasks: autorun

[UninstallRun]
Filename: "taskkill"; Parameters: "/F /IM Albayan.exe"; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{pf}\tecwindow\Albayan"

[InstallDelete]
Type: filesandordirs; Name: "{app}\*"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall

[Code]
procedure DeleteSettingsFolder();
begin
  DelTree(ExpandConstant('{userappdata}\tecwindow\albayan'), True, True, True);
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    if FileExists(ExpandConstant('{userappdata}\tecwindow\{#MyAppName}\Settingss.ini')) then
    begin
      RenameFile(ExpandConstant('{userappdata}\tecwindow\{#MyAppName}\Settingss.ini'),
                 ExpandConstant('{userappdata}\tecwindow\{#MyAppName}\config.ini'));
    end;
  end;
end;

procedure DeinitializeUninstall();
begin
  if MsgBox(ExpandConstant('{cm:DeleteSettingsPrompt}') + #13#10 +
            ExpandConstant('{userappdata}\tecwindow\albayan'),
            mbConfirmation, MB_YESNO) = IDYES then
  begin
    DeleteSettingsFolder();
  end;
end;
