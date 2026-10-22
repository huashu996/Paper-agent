param(
    [Parameter(Mandatory = $true)][string]$PresentationPath,
    [Parameter(Mandatory = $true)][string]$ManifestPath
)

$ErrorActionPreference = 'Stop'
$presentationFile = [IO.Path]::GetFullPath($PresentationPath)
$manifestFile = [IO.Path]::GetFullPath($ManifestPath)
$manifest = [IO.File]::ReadAllText($manifestFile, [Text.Encoding]::UTF8) | ConvertFrom-Json
$equations = @($manifest.equations)
if ([string]$manifest.mode -ne 'Office' -or $equations.Count -eq 0) { throw 'Office manifest contains no equations.' }

. (Join-Path $PSScriptRoot 'powerpoint_window_binding.ps1')
$binding = Get-FormulaSkillExactVisiblePresentation -PresentationPath $presentationFile -LaunchIfMissing
$powerPoint = $binding.Application
$presentation = $binding.Presentation
$actualPath = [IO.Path]::GetFullPath([string]$presentation.FullName)
if (-not [string]::Equals($actualPath, $presentationFile, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Bound presentation does not match the authorized target. Expected=$presentationFile Actual=$actualPath"
}
try { $presentation.Windows.Item(1).Activate() } catch {}
if ($null -eq $powerPoint.ActivePresentation -or -not [string]::Equals(
    [IO.Path]::GetFullPath([string]$powerPoint.ActivePresentation.FullName),
    $presentationFile,
    [StringComparison]::OrdinalIgnoreCase
)) {
    throw 'The authorized target presentation could not be activated.'
}
$results = @()
try {
    foreach ($item in $equations) {
        $target = $item.target
        $slideIndex = [int]$target.slide_index
        if ($slideIndex -lt 1 -or $slideIndex -gt $presentation.Slides.Count) { throw "Invalid slide for $($item.id): $slideIndex" }
        $slide = $presentation.Slides.Item($slideIndex)
        $powerPoint.ActiveWindow.View.GotoSlide($slideIndex)
        if ([string]$target.type -eq 'powerpoint_shape') {
            try { $equation = $slide.Shapes.Item([string]$target.shape_name) } catch { throw "PowerPoint target not found for $($item.id)" }
        }
        elseif ([string]$target.type -eq 'powerpoint_rect' -and @($target.rect).Count -eq 4) {
            $rect = @($target.rect | ForEach-Object { [double]$_ })
            $equation = $slide.Shapes.AddTextbox(1, $rect[0], $rect[1], $rect[2], $rect[3])
        }
        else { throw "Unsupported PowerPoint target for $($item.id): $($target.type)" }

        $left = [double]$equation.Left; $top = [double]$equation.Top; $width = [double]$equation.Width; $height = [double]$equation.Height
        try { $equation.Fill.Visible = 0; $equation.Line.Visible = 0 } catch {}
        $range = $equation.TextFrame2.TextRange
        $range.Text = [string]$item.native_linear
        $range.Font.Name = 'Cambria Math'
        $range.Font.Size = [single]$(if ($item.font_size) { $item.font_size } else { 20 })
        $range.Select()
        if (-not $powerPoint.CommandBars.GetEnabledMso('EquationInsertNew')) { throw 'PowerPoint native equation insertion is unavailable.' }
        $powerPoint.CommandBars.ExecuteMso('EquationInsertNew')
        Start-Sleep -Milliseconds 180
        $mathText = ''
        try { $mathText = [string]$equation.TextFrame2.TextRange.MathZones(1, 1).Text } catch {}
        if ([string]::IsNullOrWhiteSpace($mathText)) { throw "PowerPoint did not create a MathZone for $($item.id)" }
        $range = $equation.TextFrame2.TextRange
        $range.Select()
        if (-not $powerPoint.CommandBars.GetEnabledMso('EquationProfessional')) { throw 'PowerPoint professional equation conversion is unavailable.' }
        $powerPoint.CommandBars.ExecuteMso('EquationProfessional')
        Start-Sleep -Milliseconds 220
        $equation.Left = $left; $equation.Top = $top; $equation.Width = $width; $equation.Height = $height
        $equation.Name = [string]$item.id
        $finalMathText = ''
        try { $finalMathText = [string]$equation.TextFrame2.TextRange.MathZones(1, 1).Text } catch {}
        if ([string]::IsNullOrWhiteSpace($finalMathText)) { throw "PowerPoint equation is empty for $($item.id)" }
        $results += [pscustomobject]@{ id = [string]$item.id; object_type = 'PowerPoint.NativeEquation'; slide = $slideIndex }
        try { $powerPoint.ActiveWindow.Selection.Unselect() } catch {}
    }
    $presentation.Save()
}
finally {
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation)
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($powerPoint)
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

[pscustomobject]@{ mode = 'Office'; target = 'PowerPoint'; output = $presentationFile; inserted_count = $results.Count; equations = $results } | ConvertTo-Json -Depth 6
