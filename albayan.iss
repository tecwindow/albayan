#define MyAppName "Albayan"
#define MyAppVersion "5.0.1"
#define AppVersion "5.0.1"
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

DefaultDirName={sd}\program files\tecwindow\{#MyAppName}
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
Source: "albayan_build\Audio\athkar\*"; DestDir: "{userappdata}\tecwindow\albayan\Audio\athkar"; Flags: ignoreversion recursesubdirs createallsubdirs

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
Type: filesandordirs; Name: "{app}\*"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall

[Code]
var
  InstallModePage: TInputOptionWizardPage;
  OriginalDirPath: String;

// Helper function to check if Normal Install is selected
function IsNormalInstall: Boolean;
begin
  if InstallModePage <> nil then
    Result := InstallModePage.Values[0]
  else
    Result := True; // Safe fallback during setup initialization
end;

// Helper function to check if Portable Install is selected
function IsPortableInstall: Boolean;
begin
  if InstallModePage <> nil then
    Result := InstallModePage.Values[1]
  else
    Result := False;
end;
procedure InitializeWizard;
begin
  // Save the default or previous installation path Inno Setup automatically calculated
  OriginalDirPath := WizardForm.DirEdit.Text;
  
  // Create a custom page to ask for the installation mode, using translated strings
  InstallModePage := CreateInputOptionPage(wpWelcome,
    CustomMessage('InstallModeTitle'), 
    CustomMessage('InstallModeDesc'),
    CustomMessage('InstallModeText'),
    True, False);

  // Add the radio button options with translations
  InstallModePage.Add(CustomMessage('InstallModeNormal'));
  InstallModePage.Add(CustomMessage('InstallModePortable'));

  // Set default selection to "Normal Installation"
  InstallModePage.Values[0] := True;
end;

// Intercept the "Next" button click to change the target directory dynamically
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  // When leaving our custom page, update the directory input box
  if CurPageID = InstallModePage.ID then
  begin
    if IsPortableInstall then
    begin
      // Set to Documents\App Name 
      // تم إزالة السطر الذي يقوم بتفريغ مسار قائمة ابدأ لمنع خطأ "يجب إدخال اسم مجلد"
      WizardForm.DirEdit.Text := ExpandConstant('{userdocs}\{#MyAppName}');
    end
    else
    begin
      // Restore the original path (either default Program Files or previously installed path)
      WizardForm.DirEdit.Text := OriginalDirPath;
    end;
  end;
  Result := True;
end;

// Skip the Start Menu program group selection AND Tasks (desktop shortcut) pages if Portable mode is selected
function ShouldSkipPage(PageID: Integer): Boolean;
begin
  if ((PageID = wpSelectProgramGroup) or (PageID = wpSelectTasks)) and IsPortableInstall then
    Result := True
  else
    Result := False;
end;

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
