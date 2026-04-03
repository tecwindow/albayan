#define MyAppName "Albayan"
#define MyAppVersion "6.0.0"
#define AppVersion "6.0.0"
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
VersionInfoCopyright=copyright, ©2026; tecwindow
VersionInfoProductName=Albayan
VersionInfoProductVersion={#MyAppVersion}
VersionInfoOriginalFileName=Albayan_Setup.exe
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
ArchitecturesAllowed=x64compatible arm64
ArchitecturesInstallIn64BitMode=x64compatible arm64
SetupIconFile=Albayan.ico
DefaultDirName={code:GetDefaultDirName}

DisableProgramGroupPage=yes
DisableDirPage=no
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

; Dynamically prevents uninstaller generation and registry writes in Portable mode
Uninstallable=IsNormalInstall

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[CustomMessages]
arabic.AppLNGfile=Arabic
english.DeleteSettingsPrompt=Do you want to delete the settings folder?
arabic.DeleteSettingsPrompt=هل تريد حذف مجلد الإعدادات؟
english.autorun=auto start albayan with windows?
arabic.autorun=فتح برنامج البيان تلقائيا مع بدء تشغيل النظام

; Translations for the custom Installation Mode page
english.InstallModeTitle=Installation Mode
arabic.InstallModeTitle=نوع التثبيت
english.InstallModeDesc=Please select how you want to install {#MyAppName}.
arabic.InstallModeDesc=الرجاء تحديد كيف تريد تثبيت {#MyAppName}.
english.InstallModeText=Select Normal Installation for a standard setup with shortcuts, or Portable Version to extract files into a standalone folder without modifying your system registry.
arabic.InstallModeText=حدد "تثبيت عادي" لإعداد قياسي مع اختصارات، أو "نسخة محمولة" لاستخراج الملفات في مجلد مستقل دون تعديل سجل النظام الخاص بك.
english.InstallModeNormal=Normal Installation (Recommended)
arabic.InstallModeNormal=تثبيت عادي (مستحسن)
english.InstallModePortable=Portable Version
arabic.InstallModePortable=نسخة محمولة

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Check: IsNormalInstall
Name: "autorun"; Description: "{cm:autorun}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; Check: IsNormalInstall

[Files]
Source: "albayan_build\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "albayan_build\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "albayan_build\Audio\athkar\*"; DestDir: "{userappdata}\tecwindow\albayan\Audio\athkar"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: IsNormalInstall
Source: "albayan_build\Audio\athkar\*"; DestDir: "{app}\user_data\audio\athkar"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: IsPortableInstall

[Icons]
Name: "{autoprograms}\Albayan"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Albayan.ico";  Check: IsNormalInstall
Name: "{autodesktop}\Albayan"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\Albayan.ico"; Tasks: desktopicon;  Check: IsNormalInstall

[INI]
Filename: "{userappdata}\tecwindow\{#MyAppName}\config.ini"; Section: "general"; Key: "run_in_background_enabled"; String: "true"; Tasks: autorun;  Check: IsNormalInstall
Filename: "{userappdata}\tecwindow\{#MyAppName}\config.ini"; Section: "general"; Key: "auto_start_enabled"; String: "true"; Tasks: autorun;  Check: IsNormalInstall

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "albayan"; ValueData: "{app}\albayan.exe --minimized"; Flags: uninsdeletevalue; Tasks: autorun;  Check: IsNormalInstall

[UninstallRun]
Filename: "taskkill"; Parameters: "/F /IM Albayan.exe"; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{pf}\tecwindow\Albayan"

[InstallDelete]

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall

[Code]
var
  InstallModePage: TInputOptionWizardPage;
  IsPortableMode: Boolean;
  UserProvidedDir: String;

// Helper: Check if a specific parameter (like /PORTABLE) was passed to Setup.exe
function HasCmdLineParam(const ParamName: String): Boolean;
var
  I: Integer;
begin
  Result := False;
  for I := 1 to ParamCount do
  begin
    if CompareText(ParamStr(I), ParamName) = 0 then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

// InitializeSetup fires before the UI even loads. 
// Perfect place to capture our command-line arguments.
function InitializeSetup(): Boolean;
begin
  // Check for the custom /PORTABLE switch
  IsPortableMode := HasCmdLineParam('/PORTABLE');

  // Check if user utilized Inno's native /DIR="X:\Path" argument
  UserProvidedDir := ExpandConstant('{param:DIR}');

  Result := True;
end;

// Provides the initial dynamic default directory for the engine.
// This guarantees that /SILENT installs work flawlessly without UI interaction.
function GetDefaultDirName(Param: String): String;
begin
  if IsPortableMode then
    Result := ExpandConstant('{src}\{#MyAppName}')
  else
    Result := ExpandConstant('{sd}\program files\tecwindow\{#MyAppName}');
end;

// Used by Check: parameters in [Tasks], [Icons], [Setup]
function IsNormalInstall: Boolean;
begin
  Result := not IsPortableMode;
end;

function IsPortableInstall: Boolean;
begin
  Result := IsPortableMode;
end;

procedure DeleteSettingsFolder();
begin
  DelTree(ExpandConstant('{userappdata}\tecwindow\albayan'), True, True, True);
end;


procedure InitializeWizard;
begin
  // Create our custom mode selection page
  InstallModePage := CreateInputOptionPage(wpWelcome,
    CustomMessage('InstallModeTitle'), 
    CustomMessage('InstallModeDesc'),
    CustomMessage('InstallModeText'),
    True, False);

  InstallModePage.Add(CustomMessage('InstallModeNormal'));
  InstallModePage.Add(CustomMessage('InstallModePortable'));

  // Pre-select radio button based on command-line argument
  if IsPortableMode then
  begin
    InstallModePage.Values[0] := False;
    InstallModePage.Values[1] := True;
  end
  else
  begin
    InstallModePage.Values[0] := True;
    InstallModePage.Values[1] := False;
  end;
end;

// Intercept "Next" button click to change the target directory dynamically
function NextButtonClick(CurPageID: Integer): Boolean;
var
  ExpectedNormalDir, ExpectedPortableDir: String;
begin
  if CurPageID = InstallModePage.ID then
  begin
    ExpectedNormalDir := ExpandConstant('{sd}\program files\tecwindow\{#MyAppName}');
    ExpectedPortableDir := ExpandConstant('{src}\{#MyAppName}');

    // Smart Directory Override Logic:
    // Only auto-switch the target path if the user hasn't specified /DIR via command line
    // AND hasn't manually clicked "Browse" to set a custom path yet.
    if (UserProvidedDir = '') and
       ((CompareText(WizardForm.DirEdit.Text, ExpectedNormalDir) = 0) or
        (CompareText(WizardForm.DirEdit.Text, ExpectedPortableDir) = 0)) then
    begin
      IsPortableMode := InstallModePage.Values[1]; // Get UI state
      if IsPortableMode then
        WizardForm.DirEdit.Text := ExpectedPortableDir
      else
        WizardForm.DirEdit.Text := ExpectedNormalDir;
    end
    else
    begin
      // If they have a custom browsed path or used /DIR, respect it and just update internal state
      IsPortableMode := InstallModePage.Values[1];
    end;
  end;
  Result := True;
end;

// Skip the Start Menu program group and Task selection pages if Portable mode is active
function ShouldSkipPage(PageID: Integer): Boolean;
begin
  if ((PageID = wpSelectProgramGroup) or (PageID = wpSelectTasks)) and IsPortableMode then
    Result := True
  else
    Result := False;
end;


procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDir: String;
begin
  if CurStep = ssInstall then
  begin
    if IsPortableInstall then
    begin
      AppDir := ExpandConstant('{app}');

      // Delete specific folders
      DelTree(AppDir + '\Audio',         True, True, True);
      DelTree(AppDir + '\database',      True, True, True);
      DelTree(AppDir + '\documentation', True, True, True);
      DelTree(AppDir + '\lib',           True, True, True);

      // Delete specific files
      DeleteFile(AppDir + '\Albayan.exe');
      DeleteFile(AppDir + '\Albayan.ico');
      DeleteFile(AppDir + '\bass.dll');
      DeleteFile(AppDir + '\frozen_application_license.txt');
      DeleteFile(AppDir + '\python3.dll');
      DeleteFile(AppDir + '\python313.dll');
      DeleteFile(AppDir + '\unins000.dat');
      DeleteFile(AppDir + '\unins000.exe');
    end;

    if FileExists(ExpandConstant('{userappdata}\tecwindow\{#MyAppName}\Settingss.ini')) then
    begin
      RenameFile(
        ExpandConstant('{userappdata}\tecwindow\{#MyAppName}\Settingss.ini'),
        ExpandConstant('{userappdata}\tecwindow\{#MyAppName}\config.ini')
      );
    end;
  end;

  if CurStep = ssPostInstall then
  begin
    DelTree(ExpandConstant('{app}\Audio\athkar'), True, True, True);
  end;
end;


procedure DeinitializeUninstall();
begin
  if MsgBox(
      ExpandConstant('{cm:DeleteSettingsPrompt}') + #13#10 +
      ExpandConstant('{userappdata}\tecwindow\albayan'),
      mbConfirmation, MB_YESNO) = IDYES then
  begin
    DeleteSettingsFolder();
  end;
end;

