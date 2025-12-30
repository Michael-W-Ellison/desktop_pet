; Desktop Pal Installer Script for Inno Setup
; Download Inno Setup from: https://jrsoftware.org/isdl.php

#define MyAppName "Desktop Pal"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Desktop Pal"
#define MyAppURL "https://github.com/desktop-pet"
#define MyAppExeName "DesktopPet.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{8E2F4A3B-5C7D-4E9F-A1B2-3C4D5E6F7A8B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Output settings
OutputDir=..\dist\installer
OutputBaseFilename=DesktopPetSetup
SetupIconFile=..\assets\icon.ico
; Compression
Compression=lzma2
SolidCompression=yes
; Privileges - don't require admin for per-user install
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Modern look
WizardStyle=modern
WizardSizePercent=100

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "startmenuicon"; Description: "Create a Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "autostart"; Description: "Start Desktop Pal when Windows starts"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
; Main executable (built with PyInstaller)
Source: "..\dist\DesktopPet.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include source files for non-frozen mode (optional, for development)
Source: "..\src\*"; DestDir: "{app}\src"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
; Assets
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs; Check: DirExists(ExpandConstant('{src}\..\assets'))
; Documentation
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu icons
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenuicon
; Desktop icon
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Startup (if selected)
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: autostart

[Run]
; Option to launch after install
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up generated files
Type: files; Name: "{app}\pet_data.json"
Type: files; Name: "{app}\install_config.json"
Type: dirifempty; Name: "{app}"

[Code]
// Custom code for additional installation logic

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Add any pre-installation checks here
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Post-installation tasks
    // Mark first run as complete since we're using the installer
    SaveStringToFile(ExpandConstant('{app}\install_config.json'),
      '{"first_run_complete": true, "installed_via_setup": true}', False);
  end;
end;

// Check if the assets directory exists
function DirExists(const DirName: string): Boolean;
begin
  Result := DirExists(DirName);
end;
