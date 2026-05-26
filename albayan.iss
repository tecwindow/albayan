#define MyAppName "Albayan"
#define MyAppVersion "6.2.0"
#define AppVersion "6.2.0-"
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


english.OpenUserGuide=Open User Guide
arabic.OpenUserGuide=فتح دليل المستخدم
english.OpenWhatsNew=Open What's New
arabic.OpenWhatsNew=فتح المستجدات
english.TelegramBtn=Follow TecWindow on Telegram
arabic.TelegramBtn=تابع نافذة التقنية على Telegram
english.WebsiteBtn=Visit TecWindow Website
arabic.WebsiteBtn=زيارة موقع نافذة التقنية
english.BlogBtn=Visit TecWindow Blog
arabic.BlogBtn=زيارة مدونة نافذة التقنية
english.FollowUsBtn=TecWindow Accounts
arabic.FollowUsBtn=حسابات نافذة التقنية

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
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "{app}\documentation\UserGuide.html"; Description: "{cm:OpenUserGuide}"; Flags: shellexec nowait postinstall unchecked skipifsilent
Filename: "{app}\documentation\WhatsNew.html"; Description: "{cm:OpenWhatsNew}"; Flags: shellexec nowait postinstall unchecked skipifsilent
Filename: "{app}\{#MyAppExeName}"; Flags: nowait; Check: WizardSilent

[Code]
var
  InstallModePage: TInputOptionWizardPage;
  IsPortableMode: Boolean;
  UserProvidedDir: String;
  TelegramBtn, WebsiteBtn, BlogBtn, FollowUsBtn: TNewButton;

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

function InitializeSetup(): Boolean;
begin
  IsPortableMode := HasCmdLineParam('/PORTABLE');
  UserProvidedDir := ExpandConstant('{param:DIR}');
  Result := True;
end;

function GetDefaultDirName(Param: String): String;
begin
  if IsPortableMode then
    Result := ExpandConstant('{src}\{#MyAppName}')
  else
    Result := ExpandConstant('{sd}\program files\tecwindow\{#MyAppName}');
end;

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


procedure OpenURL(URL: string);
var
  ErrorCode: Integer;
begin
  ShellExec('open', URL, '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
end;

procedure TelegramClick(Sender: TObject);
begin
  OpenURL('https://t.me/tecwindow');
end;

procedure WebsiteClick(Sender: TObject);
begin
  OpenURL('https://tecwindow.net');
end;

procedure BlogClick(Sender: TObject);
begin
  OpenURL('https://blog.tecwindow.net');
end;

procedure FollowUsClick(Sender: TObject);
begin
  OpenURL('https://tecwindow.net/follow-us/');
end;

procedure InitializeWizard;
begin
  InstallModePage := CreateInputOptionPage(wpWelcome,
    CustomMessage('InstallModeTitle'),
    CustomMessage('InstallModeDesc'),
    CustomMessage('InstallModeText'),
    True, False);

  InstallModePage.Add(CustomMessage('InstallModeNormal'));
  InstallModePage.Add(CustomMessage('InstallModePortable'));

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

  
  TelegramBtn := TNewButton.Create(WizardForm);
  TelegramBtn.Parent := WizardForm.FinishedPage;
  TelegramBtn.Caption := CustomMessage('TelegramBtn');
  TelegramBtn.OnClick := @TelegramClick;
  TelegramBtn.Width := ScaleX(150);
  TelegramBtn.Height := ScaleY(25);


  WebsiteBtn := TNewButton.Create(WizardForm);
  WebsiteBtn.Parent := WizardForm.FinishedPage;
  WebsiteBtn.Caption := CustomMessage('WebsiteBtn');
  WebsiteBtn.OnClick := @WebsiteClick;
  WebsiteBtn.Width := ScaleX(150);
  WebsiteBtn.Height := ScaleY(25);


  BlogBtn := TNewButton.Create(WizardForm);
  BlogBtn.Parent := WizardForm.FinishedPage;
  BlogBtn.Caption := CustomMessage('BlogBtn');
  BlogBtn.OnClick := @BlogClick;
  BlogBtn.Width := ScaleX(150);
  BlogBtn.Height := ScaleY(25);


  FollowUsBtn := TNewButton.Create(WizardForm);
  FollowUsBtn.Parent := WizardForm.FinishedPage;
  FollowUsBtn.Caption := CustomMessage('FollowUsBtn');
  FollowUsBtn.OnClick := @FollowUsClick;
  FollowUsBtn.Width := ScaleX(150);
  FollowUsBtn.Height := ScaleY(25);
end;


procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin

    if TelegramBtn.Top = 0 then
    begin

      WizardForm.RunList.Height := WizardForm.RunList.Height - (TelegramBtn.Height * 2 + ScaleY(20));
      

      TelegramBtn.Left := WizardForm.RunList.Left;
      TelegramBtn.Top := WizardForm.RunList.Top + WizardForm.RunList.Height + ScaleY(10);
      
      WebsiteBtn.Left := TelegramBtn.Left + TelegramBtn.Width + ScaleX(10);
      WebsiteBtn.Top := TelegramBtn.Top;
      

      BlogBtn.Left := WizardForm.RunList.Left;
      BlogBtn.Top := TelegramBtn.Top + TelegramBtn.Height + ScaleY(10);
      
      FollowUsBtn.Left := BlogBtn.Left + BlogBtn.Width + ScaleX(10);
      FollowUsBtn.Top := BlogBtn.Top;
      

      WizardForm.RunList.TabOrder := 0;
      TelegramBtn.TabOrder := 1;
      WebsiteBtn.TabOrder := 2;
      BlogBtn.TabOrder := 3;
      FollowUsBtn.TabOrder := 4;

    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  ExpectedNormalDir, ExpectedPortableDir: String;
begin
  if CurPageID = InstallModePage.ID then
  begin
    ExpectedNormalDir := ExpandConstant('{sd}\program files\tecwindow\{#MyAppName}');
    ExpectedPortableDir := ExpandConstant('{src}\{#MyAppName}');

    if (UserProvidedDir = '') and
       ((CompareText(WizardForm.DirEdit.Text, ExpectedNormalDir) = 0) or
        (CompareText(WizardForm.DirEdit.Text, ExpectedPortableDir) = 0)) then
    begin
      IsPortableMode := InstallModePage.Values[1];
      if IsPortableMode then
        WizardForm.DirEdit.Text := ExpectedPortableDir
      else
        WizardForm.DirEdit.Text := ExpectedNormalDir;
    end
    else
    begin
      IsPortableMode := InstallModePage.Values[1];
    end;
  end;
  Result := True;
end;

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
    AppDir := ExpandConstant('{app}');

    DelTree(AppDir + '\Audio',         True, True, True);
    DelTree(AppDir + '\database',      True, True, True);
    DelTree(AppDir + '\documentation', True, True, True);
    DelTree(AppDir + '\lib',           True, True, True);

    DeleteFile(AppDir + '\Albayan.exe');
    DeleteFile(AppDir + '\Albayan.ico');
    DeleteFile(AppDir + '\bass.dll');
    DeleteFile(AppDir + '\frozen_application_license.txt');
    DeleteFile(AppDir + '\python3.dll');
    DeleteFile(AppDir + '\python313.dll');
    DeleteFile(AppDir + '\python314.dll');

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