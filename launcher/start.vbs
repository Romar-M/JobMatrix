' ============================================================
'  JobMatrix — полностью скрытый запуск (рекомендуется)
'  Двойной клик -> сервер стартует в фоне БЕЗ окна консоли,
'  браузер открывается автоматически.
'  Остановка: stop.vbs или stop.bat
' ============================================================
Option Explicit
Dim shell, fso, dir, bat
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
bat = dir & "\_start_hidden.bat"
' 0 = скрытое окно, False = не ждать завершения
shell.Run """" & bat & """", 0, False

