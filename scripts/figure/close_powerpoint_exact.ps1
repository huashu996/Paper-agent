param(
    [Parameter(Mandatory=$true)][string]$PresentationPath,
    [switch]$AuthorizedClose
)
$ErrorActionPreference='Stop'
$expectedPath=[IO.Path]::GetFullPath($PresentationPath)
if(-not$AuthorizedClose){throw 'Closing the target presentation requires explicit -AuthorizedClose.'}
. (Join-Path $PSScriptRoot 'powerpoint_window_binding.ps1')
$binding=Get-FormulaSkillExactVisiblePresentation -PresentationPath $expectedPath
if($null-eq$binding){throw "The exact PowerPoint presentation is not open: $expectedPath"}
$presentation=$binding.Presentation;$powerPoint=$binding.Application
if(-not[string]::Equals([IO.Path]::GetFullPath([string]$presentation.FullName),$expectedPath,[StringComparison]::OrdinalIgnoreCase)){throw 'Bound presentation path does not match the authorized target.'}
try{$presentation.Save();$presentation.Close()}finally{try{[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation)}catch{};try{[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($powerPoint)}catch{}}
[pscustomobject]@{presentation=$expectedPath;saved=$true;closed=$true}|ConvertTo-Json
