#define MyAppName "Albayan"
#define MyAppVersion "2.0.0"
#define AppVersion "2.0.0"
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
OutputDir=albayan_build
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

[CustomMessages]
arabic.AppLNGfile=Arabic
english.DeleteSettingsPrompt=Do you want to delete the settings folder?
arabic.DeleteSettingsPrompt=هل تريد حذف مجلد الإعدادات؟
english.autorun=auto start albayan with windows?
arabic.autorun=فتح برنامج البيان تلقائيا مع بدء تشغيل النظام

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autorun"; Description: "{cm:autorun}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "albayan_build\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "albayan_build\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "albayan_build\Audio\athkar\*"; DestDir: "{userappdata}\tecwindow\albayan\Audio\athkar"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Albayan"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Albayan"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[INI]
Filename: "{userappdata}\tecwindow\{#MyAppName}\Settingss.ini"; Section: "general"; Key: "language"; String: "{cm:AppLNGfile}"

[UninstallDelete]
Type: filesandordirs; Name: "{pf}\tecwindow\Albayan"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall

[Code]
procedure DeleteOldInstallation();
begin
  if DirExists(ExpandConstant('{sd}\program files\tecwindow\{#MyAppName}\Audio\sounds')) then
  begin
    DelTree(ExpandConstant('{sd}\program files\tecwindow\{#MyAppName}\Audio\sounds'), True, True, True);
  end;
end;

function InitializeSetup(): Boolean;
begin
  DeleteOldInstallation();
  Result := True;
end;

procedure DeleteAthkarFolder();
begin
  DelTree(ExpandConstant('{app}\Audio\athkar'), True, True, True);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    DeleteAthkarFolder();
  end;
end;

procedure DeleteSettingsFolder();
begin
  DelTree(ExpandConstant('{userappdata}\tecwindow\albayan'), True, True, True);
end;

function AskDeleteSettingsFolder(): Boolean;
begin
  Result := MsgBox(ExpandConstant('{cm:DeleteSettingsPrompt}') + #13#10 + ExpandConstant('{userappdata}\tecwindow\albayan'), mbConfirmation, MB_YESNO) = IDYES;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    if AskDeleteSettingsFolder() then
    begin
      DeleteSettingsFolder();
    end;
  end;
end;
