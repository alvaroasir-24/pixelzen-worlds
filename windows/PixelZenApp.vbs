Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
here = fso.GetParentFolderName(WScript.ScriptFullName)
extra = ""
For i = 0 To WScript.Arguments.Count - 1
    arg = LCase(WScript.Arguments(i))
    If arg = "--tray" Or arg = "-tray" Then
        extra = extra & " -Tray"
    ElseIf arg = "--solo-aplicar" Or arg = "-soloaplicar" Then
        extra = extra & " -SoloAplicar"
    End If
Next
cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -WindowStyle Hidden -File """ & here & "\PixelZenMenu.ps1""" & extra
sh.Run cmd, 0, False
