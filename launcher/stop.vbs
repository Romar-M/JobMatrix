' ============================================================
'  JobMatrix — скрытая остановка фонового сервера
'  Двойной клик -> сервер останавливается, окна нет
' ============================================================
Option Explicit
Dim shell, fso, dir, bat
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
bat = dir & "\_stop_hidden.bat"
shell.Run """" & bat & """", 0, False

