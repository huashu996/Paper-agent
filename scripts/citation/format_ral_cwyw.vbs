Option Explicit

' Usage:
'   cscript.exe //nologo format_ral_cwyw.vbs <working.docx> <preview.pdf> [expected-citation-fields] [clear-footers]
' Preconditions:
'   - The document is a disposable working copy.
'   - Temporary citations use real EndNote record numbers, or real CWYW fields already exist.
'   - The required EndNote output style is selected before this script runs.

Dim docxPath, pdfPath, expectedCites, clearFooters
Dim word, doc, macroUsed, field, code, citeCount, refField
Dim section, columns, footer, body, intro, refStart, beforeStart
Dim beforeText, headingRange, refHeading, re, resultText

If WScript.Arguments.Count < 2 Then
  WScript.Echo "Usage: cscript.exe //nologo format_ral_cwyw.vbs <working.docx> <preview.pdf> [expected-citation-fields] [clear-footers]"
  WScript.Quit 2
End If

docxPath = WScript.Arguments(0)
pdfPath = WScript.Arguments(1)
expectedCites = 0
clearFooters = False
If WScript.Arguments.Count >= 3 Then
  If IsNumeric(WScript.Arguments(2)) Then expectedCites = CInt(WScript.Arguments(2))
End If
If WScript.Arguments.Count >= 4 Then
  clearFooters = (LCase(WScript.Arguments(3)) = "clear-footers")
End If

Sub AbortRun(message)
  Dim detail
  detail = message
  If Err.Number <> 0 Then detail = detail & ": " & Err.Description & " (" & CStr(Err.Number) & ")"
  On Error Resume Next
  If IsObject(doc) Then doc.Close False
  If IsObject(word) Then word.Quit
  WScript.Echo detail
  WScript.Quit 1
End Sub

On Error Resume Next
Set word = CreateObject("Word.Application")
If Err.Number <> 0 Then AbortRun "Could not create Word.Application"
word.Visible = False
If Err.Number <> 0 Then AbortRun "Could not configure Word visibility"
word.DisplayAlerts = 0
If Err.Number <> 0 Then AbortRun "Could not configure Word alerts"
Set doc = word.Documents.Open(docxPath)
If Err.Number <> 0 Then AbortRun "Could not open working document"

doc.Save
If Err.Number <> 0 Then AbortRun "Could not save working document before CWYW"
WScript.Sleep 2000

macroUsed = ""
Err.Clear
word.Run "Project.EndNoteMacros.ENFormatBibliography"
If Err.Number = 0 Then macroUsed = "Project.EndNoteMacros.ENFormatBibliography"
If macroUsed = "" Then
  Err.Clear
  word.Run "EndNoteMacros.ENFormatBibliography"
  If Err.Number = 0 Then macroUsed = "EndNoteMacros.ENFormatBibliography"
End If
If macroUsed = "" Then
  Err.Clear
  word.Run "ENFormatBibliography"
  If Err.Number = 0 Then macroUsed = "ENFormatBibliography"
End If
If macroUsed = "" Then AbortRun "Could not run EndNote formatting macro"
On Error GoTo 0
WScript.Sleep 8000

Set re = New RegExp
re.Pattern = "\{[^{}]+#[0-9]+[^{}]*\}"
re.Global = True
If re.Test(doc.Content.Text) Then AbortRun "Temporary EndNote citations remain after formatting"

citeCount = 0
Set refField = Nothing
For Each field In doc.Fields
  code = field.Code.Text
  If InStr(1, code, "ADDIN EN.CITE", vbTextCompare) > 0 And InStr(1, code, "EN.CITEDATA", vbTextCompare) = 0 Then
    citeCount = citeCount + 1
  ElseIf InStr(1, code, "ADDIN EN.REFLIST", vbTextCompare) > 0 Then
    Set refField = field
  End If
Next
If citeCount = 0 Then AbortRun "No EndNote citation fields were created"
If expectedCites > 0 And citeCount < expectedCites Then AbortRun "EndNote created fewer citation fields than expected"
If refField Is Nothing Then AbortRun "EndNote bibliography field was not created"

For Each section In doc.Sections
  section.PageSetup.PageWidth = 612
  section.PageSetup.PageHeight = 792
  section.PageSetup.TopMargin = 54
  section.PageSetup.BottomMargin = 45
  section.PageSetup.LeftMargin = 48
  section.PageSetup.RightMargin = 48
  section.PageSetup.Gutter = 0
  Set columns = section.PageSetup.TextColumns
  columns.SetCount 2
  columns.EvenlySpaced = True
  columns.Spacing = 18
  If clearFooters Then
    For Each footer In section.Footers
      footer.Range.Text = ""
    Next
  End If
Next

Set body = doc.Content
body.Font.Name = "Times New Roman"
body.Font.Size = 10
body.Font.Bold = False
body.Font.Italic = False
body.Font.Superscript = False
body.ParagraphFormat.Alignment = 3
body.ParagraphFormat.LeftIndent = 0
body.ParagraphFormat.RightIndent = 0
body.ParagraphFormat.FirstLineIndent = 12
body.ParagraphFormat.SpaceBefore = 0
body.ParagraphFormat.SpaceAfter = 0
body.ParagraphFormat.LineSpacingRule = 0
body.ParagraphFormat.WidowControl = True

If doc.Paragraphs.Count > 0 Then
  Set intro = doc.Paragraphs.Item(1).Range
  If InStr(1, Trim(Replace(intro.Text, vbCr, "")), "I.", vbTextCompare) = 1 Then
    intro.Font.Name = "Times New Roman"
    intro.Font.Size = 10
    intro.Font.Bold = False
    intro.Font.SmallCaps = True
    intro.ParagraphFormat.Alignment = 1
    intro.ParagraphFormat.FirstLineIndent = 0
    intro.ParagraphFormat.SpaceBefore = 0
    intro.ParagraphFormat.SpaceAfter = 4
    intro.ParagraphFormat.KeepWithNext = True
  End If
End If

For Each field In doc.Fields
  code = field.Code.Text
  If InStr(1, code, "ADDIN EN.CITE", vbTextCompare) > 0 And InStr(1, code, "EN.CITEDATA", vbTextCompare) = 0 Then
    field.Result.Font.Name = "Times New Roman"
    field.Result.Font.Size = 10
    field.Result.Font.Bold = False
    field.Result.Font.Superscript = False
  End If
Next

refStart = refField.Result.Start
beforeStart = refStart - 40
If beforeStart < 0 Then beforeStart = 0
beforeText = UCase(doc.Range(beforeStart, refStart).Text)
If InStr(beforeText, "REFERENCES") = 0 And InStr(beforeText, "BIBLIOGRAPHY") = 0 Then
  Set headingRange = doc.Range(refStart, refStart)
  headingRange.InsertBefore "REFERENCES" & vbCr
  Set refHeading = doc.Range(refStart, refStart + 10).Paragraphs.Item(1).Range
  refHeading.Font.Name = "Times New Roman"
  refHeading.Font.Size = 10
  refHeading.Font.Bold = False
  refHeading.Font.SmallCaps = True
  refHeading.ParagraphFormat.Alignment = 1
  refHeading.ParagraphFormat.FirstLineIndent = 0
  refHeading.ParagraphFormat.SpaceBefore = 6
  refHeading.ParagraphFormat.SpaceAfter = 3
  refHeading.ParagraphFormat.KeepWithNext = True
End If

refField.Result.Font.Name = "Times New Roman"
refField.Result.Font.Size = 8
refField.Result.Font.Bold = False
refField.Result.Font.Superscript = False
refField.Result.ParagraphFormat.Alignment = 3
refField.Result.ParagraphFormat.LeftIndent = 14
refField.Result.ParagraphFormat.FirstLineIndent = -14
refField.Result.ParagraphFormat.SpaceBefore = 0
refField.Result.ParagraphFormat.SpaceAfter = 0
refField.Result.ParagraphFormat.LineSpacingRule = 0

doc.Save
If Err.Number <> 0 Then AbortRun "Could not save formatted document"
doc.ExportAsFixedFormat pdfPath, 17
If Err.Number <> 0 Then AbortRun "Could not export PDF preview"

resultText = "{""Path"":""" & Replace(docxPath, "\", "\\") & """," & _
  """PreviewPdf"":""" & Replace(pdfPath, "\", "\\") & """," & _
  """Macro"":""" & macroUsed & """," & _
  """CitationFields"":" & CStr(citeCount) & "," & _
  """BibliographyFields"":1," & _
  """WordFields"":" & CStr(doc.Fields.Count) & "," & _
  """Paragraphs"":" & CStr(doc.Paragraphs.Count) & "," & _
  """Pages"":" & CStr(doc.ComputeStatistics(2)) & "}"

doc.Close True
word.Quit
WScript.Echo resultText
