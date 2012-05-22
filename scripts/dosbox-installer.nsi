!define VER_MAYOR 0
!define VER_MINOR 74
!define VER_BUILD "-python"
!define APP_NAME "DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD}"
!define COMP_NAME "DOSBox Team"
!define COPYRIGHT "Copyright © 2002-2011 DOSBox Team"
!define DESCRIPTION "DOSBox Installer"

VIProductVersion "${VER_MAYOR}.${VER_MINOR}.0.0"
VIAddVersionKey  "ProductName"  "${APP_NAME}"
VIAddVersionKey  "CompanyName"  "${COMP_NAME}"
VIAddVersionKey  "FileDescription"  "${DESCRIPTION}"
VIAddVersionKey  "FileVersion"  "${VER_MAYOR}.${VER_MINOR}.0.0"
VIAddVersionKey  "ProductVersion"  "${VER_MAYOR}, ${VER_MINOR}, 0, 0"
VIAddVersionKey  "LegalCopyright"  "${COPYRIGHT}"

; The name of the installer
Name "${APP_NAME}"

; The file to write
OutFile "DOSBox${VER_MAYOR}.${VER_MINOR}${VER_BUILD}-win32-installer.exe"

; The default installation directory
InstallDir "$PROGRAMFILES\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}"

; The text to prompt the user to enter a directory
DirText "This will install DOSBox v${VER_MAYOR}.${VER_MINOR}${VER_BUILD} on your computer. Choose a directory"
SetCompressor /solid lzma

!cd ..
LicenseData COPYING
LicenseText "DOSBox v${VER_MAYOR}.${VER_MINOR}${VER_BUILD} License" "Next >"

Section "!Python example scripts" Examples
  CreateDirectory "$LOCALAPPDATA\DOSBox"
  SetOutPath "$LOCALAPPDATA\DOSBox"
  File /r scripts\python
SectionEnd

; Else vista enables compatibility mode
RequestExecutionLevel admin
; Shortcuts in all users

ComponentText "Select components for DOSBox"
; The stuff to install
Section "!Core files" Core
SetShellVarContext all

  ; Set output path to the installation directory.
  ClearErrors
  SetOutPath $INSTDIR
  IfErrors error_createdir
  SectionIn RO

  ; Put file there

  CreateDirectory "$INSTDIR\Video Codec"
  CreateDirectory "$INSTDIR\Documentation"

  SetOutPath "$INSTDIR\Documentation"
  File /oname=README.txt README
  File /oname=COPYING.txt COPYING
  File /oname=THANKS.txt THANKS
  File /oname=NEWS.txt NEWS
  File /oname=AUTHORS.txt AUTHORS
  File /oname=INSTALL.txt INSTALL

  SetOutPath "$INSTDIR"

  File "/oname=DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD} Manual.txt" README
  !cd src
  File "/oname=DOSBox.exe" DOSBox.exe
  File SDL.dll
  ;File SDL_net.dll
  File libpdcurses.dll
  File libgcc_s_dw2-1.dll
  /*
  File "/oname=Video Codec\zmbv.dll" zmbv.dll
  File "/oname=Video Codec\zmbv.inf" zmbv.inf
  File "/oname=Video Codec\Video Instructions.txt" README.video
  */
  !cd ../scripts
  File "/oname=DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD} Options.bat" editconf.bat
  File "/oname=Reset KeyMapper.bat" resetmapper.bat
  File "/oname=Reset Options.bat" resetconf.bat
  File "/oname=Screenshots & Recordings.bat" captures.bat
  
  CreateDirectory "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}"
  CreateDirectory "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras"
  CreateDirectory "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Video"
  CreateDirectory "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Options"
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD}.lnk" "$INSTDIR\DOSBox.exe" "-userconf" "$INSTDIR\DOSBox.exe" 0
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD} Manual.lnk" "$INSTDIR\Documentation\README.txt"
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD} (noconsole).lnk" "$INSTDIR\DOSBox.exe" "-noconsole -userconf" "$INSTDIR\DOSBox.exe" 0
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Screenshots & Recordings.lnk" "$INSTDIR\DOSBox.exe" "-opencaptures explorer.exe"

  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Options\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD} Options.lnk" "$INSTDIR\DOSBox.exe" "-editconf notepad.exe -editconf $\"%SystemRoot%\system32\notepad.exe$\" -editconf $\"%WINDIR%\notepad.exe$\""
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Options\Reset Options.lnk" "$INSTDIR\DOSBox.exe" "-eraseconf"
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Options\Reset KeyMapper.lnk" "$INSTDIR\DOSBox.exe" "-erasemapper"
/*
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Video\Video instructions.lnk" "$INSTDIR\Video Codec\Video Instructions.txt"
;change outpath so the working directory gets set to zmbv
SetOutPath "$INSTDIR\Video Codec"
  ; Shortcut creation depends on wether we are 9x of NT
  ClearErrors
  ReadRegStr $R0 HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion" CurrentVersion
  IfErrors we_9x we_nt
we_nt:
  ;shortcut for win NT
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Video\Install movie codec.lnk" "rundll32" "setupapi,InstallHinfSection DefaultInstall 128 $INSTDIR\Video Codec\zmbv.inf"
  goto end
we_9x:
  ;shortcut for we_9x
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Video\Install movie codec.lnk" "rundll" "setupx.dll,InstallHinfSection DefaultInstall 128 $INSTDIR\Video Codec\zmbv.inf"
end:
*/
  CreateShortCut "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Python scripts.lnk" "$LOCALAPPDATA\DOSBox\python"

SetOutPath $INSTDIR
WriteUninstaller "uninstall.exe"

  goto end_section

error_createdir:
  MessageBox MB_OK "Can't create DOSBox program directory, aborting."
  Abort
  goto end_section

end_section:
SectionEnd ; end the section

Section "Desktop Shortcut" SecDesktop
SetShellVarContext all

CreateShortCut "$DESKTOP\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD}.lnk" "$INSTDIR\DOSBox.exe" "-userconf" "$INSTDIR\DOSBox.exe" 0

SectionEnd ; end the section 


UninstallText "This will uninstall DOSBox  v${VER_MAYOR}.${VER_MINOR}${VER_BUILD}. Hit next to continue."

Section "Uninstall"

; Shortcuts in all users
SetShellVarContext all

  Delete "$DESKTOP\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD}.lnk"
  ; remove registry keys
  ; remove files
  Delete $INSTDIR\Documentation\README.txt
  Delete $INSTDIR\Documentation\COPYING.txt
  Delete $INSTDIR\Documentation\THANKS.txt
  Delete $INSTDIR\Documentation\NEWS.txt
  Delete $INSTDIR\Documentation\AUTHORS.txt
  Delete $INSTDIR\Documentation\INSTALL.txt
  Delete "$INSTDIR\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD} Manual.txt"
  Delete "$INSTDIR\DOSBox.exe"
  Delete $INSTDIR\SDL.dll
  Delete $INSTDIR\libgcc_s_dw2-1.dll
  Delete $INSTDIR\libpdcurses.dll
  /*
  Delete $INSTDIR\SDL_net.dll
  Delete "$INSTDIR\Video Codec\zmbv.dll"
  Delete "$INSTDIR\Video Codec\zmbv.inf"
  Delete "$INSTDIR\Video Codec\Video Instructions.txt"
  */
  ;Files left by sdl taking over the console
  Delete $INSTDIR\stdout.txt
  Delete $INSTDIR\stderr.txt
  Delete "$INSTDIR\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD} Options.bat"
  Delete "$INSTDIR\Reset KeyMapper.bat"
  Delete "$INSTDIR\Reset Options.bat"
  Delete "$INSTDIR\Screenshots & Recordings.bat"

  ; MUST REMOVE UNINSTALLER, too
  Delete $INSTDIR\uninstall.exe


  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD}.lnk"
  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD} Manual.lnk"
  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD} (noconsole).lnk"
  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Uninstall.lnk"
  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Screenshots & Recordings.lnk"

  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Options\DOSBox ${VER_MAYOR}.${VER_MINOR}${VER_BUILD} Options.lnk"
  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Options\Reset Options.lnk"
  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Options\Reset KeyMapper.lnk"

  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Video\Video instructions.lnk"
  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Video\Install movie codec.lnk"
  Delete "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Python scripts.lnk"

; remove shortcuts, if any.
; remove directories used.
  RMDir "$INSTDIR\Documentation"
  RMDir "$INSTDIR\Video Codec"
  RMDir "$INSTDIR"
  RMDir "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Options"
  RMDir "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras\Video"
  RMDir "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\Extras"
  RMDir "$SMPROGRAMS\DOSBox-${VER_MAYOR}.${VER_MINOR}${VER_BUILD}\"
SectionEnd

; eof
