param(
    [Parameter(Mandatory = $true)][string]$PresentationPath,
    [Parameter(Mandatory = $true)][string]$ManifestPath,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [switch]$CloseTargetWhenDone
)

$ErrorActionPreference = 'Stop'
$expectedPath = [IO.Path]::GetFullPath($PresentationPath)
$manifestFullPath = [IO.Path]::GetFullPath($ManifestPath)
$app = $null
$presentation = $null
$openedTargetByScript = $false
$fileItem = $null
$originalReadOnly = $null

function Read-Utf8Json {
    param([string]$Path)
    $utf8 = New-Object System.Text.UTF8Encoding($false, $true)
    $text = [IO.File]::ReadAllText($Path, $utf8)
    if ($text.Contains([char]0xFFFD)) {
        throw "UTF-8 replacement character found in manifest: $Path"
    }
    return $text | ConvertFrom-Json
}

function Get-ActivePowerPoint {
    try { return [Runtime.InteropServices.Marshal]::GetActiveObject('PowerPoint.Application') }
    catch { return $null }
}

function Get-ExactPresentation {
    param($Application, [string]$Path)
    if ($null -eq $Application) { return $null }
    $matches = @()
    foreach ($candidate in @($Application.Presentations)) {
        try {
            $actual = [IO.Path]::GetFullPath([string]$candidate.FullName)
            if ([string]::Equals($actual, $Path, [StringComparison]::OrdinalIgnoreCase)) {
                $matches += $candidate
            }
        } catch {}
    }
    if ($matches.Count -gt 1) { throw "Multiple exact-path presentations are open: $Path" }
    if ($matches.Count -eq 1) { return $matches[0] }
    return $null
}

function Normalize-PowerPointText {
    param([string]$Text)
    if ($null -eq $Text) { return '' }
    return ([regex]::Replace($Text, "\r\n?|\n", "`n")).TrimEnd([char]10)
}

try {
    if (!(Test-Path -LiteralPath $expectedPath)) {
        throw "Presentation does not exist: $expectedPath"
    }
    if (!(Test-Path -LiteralPath $manifestFullPath)) {
        throw "Audit manifest does not exist: $manifestFullPath"
    }

    $manifest = Read-Utf8Json -Path $manifestFullPath
    $slideIndex = if ($null -ne $manifest.slide_index) { [int]$manifest.slide_index } else { 1 }
    $renderWidth = if ($null -ne $manifest.render_width) { [int]$manifest.render_width } else { 1440 }
    $renderHeight = if ($null -ne $manifest.render_height) { [int]$manifest.render_height } else { 1080 }
    $expectedSlideCount = if ($null -ne $manifest.expected_slide_count) { [int]$manifest.expected_slide_count } else { 1 }
    $expectedShapeCount = if ($null -ne $manifest.expected_shape_count) { [int]$manifest.expected_shape_count } else { $null }
    $expectedImageCount = if ($null -ne $manifest.expected_image_count) { [int]$manifest.expected_image_count } else { $null }
    $expectedIconCount = if ($null -ne $manifest.expected_icon_count) { [int]$manifest.expected_icon_count } else { $null }
    $expectedConnectorCount = if ($null -ne $manifest.expected_connector_count) { [int]$manifest.expected_connector_count } else { $null }
    $requireFullRegistry = if ($null -ne $manifest.require_full_registry) { [bool]$manifest.require_full_registry } else { $true }

    $layerRank = @{
        background = 0
        path = 1
        node = 2
        complex_image = 3
        icon = 4
        text = 5
    }
    $objectLayer = @{}
    foreach ($entry in @($manifest.objects)) {
        $name = [string]$entry.name
        $layer = [string]$entry.layer
        if (!$layerRank.ContainsKey($layer)) { throw "Unknown layer '$layer' for object '$name'." }
        if ($objectLayer.ContainsKey($name)) { throw "Duplicate object in audit manifest: $name" }
        $objectLayer[$name] = $layer
    }

    $expectedText = @{}
    foreach ($entry in @($manifest.expected_text)) {
        $name = [string]$entry.name
        if ($expectedText.ContainsKey($name)) { throw "Duplicate expected_text object: $name" }
        $expectedText[$name] = $entry
    }
    $missingTextExpectations = @(
        $objectLayer.Keys |
        Where-Object { $objectLayer[$_] -eq 'text' -and !$expectedText.ContainsKey($_) } |
        Sort-Object
    )
    $orphanTextExpectations = @(
        $expectedText.Keys |
        Where-Object { !$objectLayer.ContainsKey($_) } |
        Sort-Object
    )

    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

    $app = Get-ActivePowerPoint
    $presentation = Get-ExactPresentation -Application $app -Path $expectedPath
    if ($null -eq $presentation) {
        $fileItem = Get-Item -LiteralPath $expectedPath -Force
        $originalReadOnly = [bool]$fileItem.IsReadOnly
        $fileItem.IsReadOnly = $true
        Start-Process -FilePath $expectedPath -WindowStyle Hidden | Out-Null
        $openedTargetByScript = $true
        $deadline = [DateTime]::UtcNow.AddSeconds(30)
        while ($null -eq $presentation -and [DateTime]::UtcNow -lt $deadline) {
            Start-Sleep -Milliseconds 250
            $app = Get-ActivePowerPoint
            $presentation = Get-ExactPresentation -Application $app -Path $expectedPath
        }
    }
    if ($null -eq $presentation) {
        throw "PowerPoint did not expose the exact presentation within 30 seconds."
    }

    $actualPath = [IO.Path]::GetFullPath([string]$presentation.FullName)
    if (![string]::Equals($actualPath, $expectedPath, [StringComparison]::OrdinalIgnoreCase)) {
        throw "ActivePresentation.FullName mismatch. Expected=$expectedPath Actual=$actualPath"
    }
    if (-not [bool]$presentation.ReadOnly) {
        throw "The audit presentation is not actually read-only."
    }
    if ([int]$presentation.Slides.Count -ne $expectedSlideCount) {
        throw "Slide count mismatch. Expected=$expectedSlideCount Actual=$($presentation.Slides.Count)"
    }

    $slide = $presentation.Slides.Item($slideIndex)
    $renderPath = Join-Path $OutputDirectory ("slide-{0}.png" -f $slideIndex)
    $slide.Export($renderPath, 'PNG', $renderWidth, $renderHeight)

    $shapeByName = @{}
    $nameCounts = @{}
    $connectors = @()
    $images = @()
    $icons = @()
    foreach ($shape in @($slide.Shapes)) {
        $name = [string]$shape.Name
        if (!$nameCounts.ContainsKey($name)) { $nameCounts[$name] = 0 }
        $nameCounts[$name]++
        $shapeByName[$name] = $shape
        try { if ([bool]$shape.Connector) { $connectors += $shape } } catch {}
        try { if ([int]$shape.Type -eq 11 -or [int]$shape.Type -eq 13) { $images += $shape } } catch {}
        try { if ([int]$shape.Type -eq 28) { $icons += $shape } } catch {}
    }

    $duplicates = @(
        $nameCounts.GetEnumerator() |
        Where-Object { $_.Value -ne 1 } |
        ForEach-Object { [pscustomobject]@{ name = $_.Key; count = $_.Value } }
    )
    $missingObjects = @($objectLayer.Keys | Where-Object { !$shapeByName.ContainsKey($_) } | Sort-Object)
    $unregisteredObjects = if ($requireFullRegistry) {
        @($shapeByName.Keys | Where-Object { !$objectLayer.ContainsKey($_) } | Sort-Object)
    } else {
        @()
    }

    $layerViolations = @()
    $registeredNames = @($objectLayer.Keys)
    for ($i = 0; $i -lt $registeredNames.Count; $i++) {
        for ($j = $i + 1; $j -lt $registeredNames.Count; $j++) {
            $nameA = $registeredNames[$i]
            $nameB = $registeredNames[$j]
            if (!$shapeByName.ContainsKey($nameA) -or !$shapeByName.ContainsKey($nameB)) { continue }
            $rankA = [int]$layerRank[$objectLayer[$nameA]]
            $rankB = [int]$layerRank[$objectLayer[$nameB]]
            if ($rankA -eq $rankB) { continue }
            if ($rankA -lt $rankB) {
                $lowerName = $nameA
                $upperName = $nameB
            } else {
                $lowerName = $nameB
                $upperName = $nameA
            }
            $lower = $shapeByName[$lowerName]
            $upper = $shapeByName[$upperName]
            if ([int]$lower.ZOrderPosition -ge [int]$upper.ZOrderPosition) {
                $layerViolations += [pscustomobject]@{
                    lower = $lowerName
                    lower_layer = $objectLayer[$lowerName]
                    lower_z = [int]$lower.ZOrderPosition
                    upper = $upperName
                    upper_layer = $objectLayer[$upperName]
                    upper_z = [int]$upper.ZOrderPosition
                }
            }
        }
    }

    $unconnectedEndpoints = @()
    foreach ($connector in $connectors) {
        try {
            if (-not [bool]$connector.ConnectorFormat.BeginConnected) {
                $unconnectedEndpoints += "$($connector.Name):source"
            }
            if (-not [bool]$connector.ConnectorFormat.EndConnected) {
                $unconnectedEndpoints += "$($connector.Name):target"
            }
        } catch {
            $unconnectedEndpoints += "$($connector.Name):read_error"
        }
    }

    $axisViolations = @()
    foreach ($constraint in @($manifest.axis_constraints)) {
        $sourceName = [string]$constraint.source
        $targetName = [string]$constraint.target
        $axis = [string]$constraint.axis
        if (!$shapeByName.ContainsKey($sourceName) -or !$shapeByName.ContainsKey($targetName)) {
            $axisViolations += [pscustomobject]@{
                source = $sourceName
                target = $targetName
                axis = $axis
                error = 'missing_shape'
            }
            continue
        }
        $source = $shapeByName[$sourceName]
        $target = $shapeByName[$targetName]
        if ($axis -eq 'vertical') {
            $delta = [Math]::Abs(
                ([double]$source.Left + [double]$source.Width / 2) -
                ([double]$target.Left + [double]$target.Width / 2)
            )
        } elseif ($axis -eq 'horizontal') {
            $delta = [Math]::Abs(
                ([double]$source.Top + [double]$source.Height / 2) -
                ([double]$target.Top + [double]$target.Height / 2)
            )
        } else {
            throw "Unknown axis '$axis' for $sourceName -> $targetName"
        }
        if ($delta -gt 0.1) {
            $axisViolations += [pscustomobject]@{
                source = $sourceName
                target = $targetName
                axis = $axis
                delta_pt = [Math]::Round($delta, 4)
            }
        }
    }

    $textOverflows = @()
    $textMismatches = @()
    $textSafetyViolations = @()
    $textLengthViolations = @()
    $orphanLineViolations = @()
    foreach ($name in @($expectedText.Keys)) {
        if (!$shapeByName.ContainsKey($name)) {
            $textMismatches += [pscustomobject]@{ name = $name; error = 'missing_shape' }
            continue
        }
        $shape = $shapeByName[$name]
        try {
            $entry = $expectedText[$name]
            $expectedValue = Normalize-PowerPointText -Text ([string]$entry.text)
            $actualText = Normalize-PowerPointText -Text ([string]$shape.TextFrame2.TextRange.Text)
            if ($actualText -ne $expectedValue -or $actualText.Contains([char]0xFFFD)) {
                $textMismatches += [pscustomobject]@{
                    name = $name
                    expected = $expectedValue
                    actual = $actualText
                }
            }
            $availableW = [double]$shape.Width - [double]$shape.TextFrame2.MarginLeft - [double]$shape.TextFrame2.MarginRight
            $availableH = [double]$shape.Height - [double]$shape.TextFrame2.MarginTop - [double]$shape.TextFrame2.MarginBottom
            $boundW = [double]$shape.TextFrame2.TextRange.BoundWidth
            $boundH = [double]$shape.TextFrame2.TextRange.BoundHeight
            if ($boundW -gt ($availableW + 0.75) -or $boundH -gt ($availableH + 0.75)) {
                $textOverflows += [pscustomobject]@{
                    name = $name
                    bound_width = [Math]::Round($boundW, 3)
                    bound_height = [Math]::Round($boundH, 3)
                    available_width = [Math]::Round($availableW, 3)
                    available_height = [Math]::Round($availableH, 3)
                }
            }

            if ($null -ne $entry.max_chars) {
                $semanticLength = ([regex]::Replace($actualText, '\s+', '')).Length
                if ($semanticLength -gt [int]$entry.max_chars) {
                    $textLengthViolations += [pscustomobject]@{
                        name = $name
                        semantic_length = $semanticLength
                        max_chars = [int]$entry.max_chars
                    }
                }
            }

            if ($null -ne $entry.reject_orphan_lines -and [bool]$entry.reject_orphan_lines) {
                $lineCount = 0
                try { $lineCount = [int]$shape.TextFrame2.TextRange.Lines().Count } catch {}
                for ($lineIndex = 1; $lineIndex -le $lineCount; $lineIndex++) {
                    $lineText = ''
                    try { $lineText = Normalize-PowerPointText -Text ([string]$shape.TextFrame2.TextRange.Lines($lineIndex, 1).Text) } catch {}
                    $trimmedLine = $lineText.Trim()
                    $isSingleCjk = $trimmedLine -match '^[\p{IsCJKUnifiedIdeographs}]$'
                    $isSingleToken = $trimmedLine -match '^[A-Za-z0-9_+\-]+$' -and $trimmedLine.Length -le 2
                    $isPunctuationOnly = $trimmedLine -match '^[\p{P}\p{S}]+$'
                    if ($isSingleCjk -or $isSingleToken -or $isPunctuationOnly) {
                        $orphanLineViolations += [pscustomobject]@{
                            name = $name
                            line_index = $lineIndex
                            line_text = $trimmedLine
                        }
                    }
                }
            }

            if ($null -ne $entry.min_clearance_factor -or $null -ne $entry.max_clearance_factor) {
                $fontSize = [double]$shape.TextFrame2.TextRange.Font.Size
                if ($fontSize -le 0 -and $null -ne $entry.font_size_pt) { $fontSize = [double]$entry.font_size_pt }
                if ($fontSize -le 0) {
                    $textSafetyViolations += [pscustomobject]@{ name = $name; error = 'font_size_unavailable' }
                } else {
                    $innerLeft = [double]$shape.Left + [double]$shape.TextFrame2.MarginLeft
                    $innerTop = [double]$shape.Top + [double]$shape.TextFrame2.MarginTop
                    $innerRight = [double]$shape.Left + [double]$shape.Width - [double]$shape.TextFrame2.MarginRight
                    $innerBottom = [double]$shape.Top + [double]$shape.Height - [double]$shape.TextFrame2.MarginBottom
                    $boundLeft = [double]$shape.TextFrame2.TextRange.BoundLeft
                    $boundTop = [double]$shape.TextFrame2.TextRange.BoundTop
                    $clearances = [ordered]@{
                        left = $boundLeft - $innerLeft
                        top = $boundTop - $innerTop
                        right = $innerRight - ($boundLeft + $boundW)
                        bottom = $innerBottom - ($boundTop + $boundH)
                    }
                    $minClearance = if ($null -ne $entry.min_clearance_factor) { [double]$entry.min_clearance_factor * $fontSize } else { $null }
                    $maxClearance = if ($null -ne $entry.max_clearance_factor) { [double]$entry.max_clearance_factor * $fontSize } else { $null }
                    foreach ($side in @('left', 'top', 'right', 'bottom')) {
                        $value = [double]$clearances[$side]
                        if (($null -ne $minClearance -and $value -lt ($minClearance - 0.75)) -or
                            ($null -ne $maxClearance -and $value -gt ($maxClearance + 0.75))) {
                            $textSafetyViolations += [pscustomobject]@{
                                name = $name
                                side = $side
                                clearance_pt = [Math]::Round($value, 3)
                                font_size_pt = [Math]::Round($fontSize, 3)
                                min_clearance_pt = if ($null -ne $minClearance) { [Math]::Round($minClearance, 3) } else { $null }
                                max_clearance_pt = if ($null -ne $maxClearance) { [Math]::Round($maxClearance, 3) } else { $null }
                            }
                        }
                    }
                }
            }
        } catch {
            $textMismatches += [pscustomobject]@{ name = $name; error = 'text_read_error' }
        }
    }

    $nativeFormulaViolations = @()
    foreach ($formulaEntry in @($manifest.native_formulas)) {
        $formulaName = [string]$formulaEntry.name
        if (!$shapeByName.ContainsKey($formulaName)) {
            $nativeFormulaViolations += [pscustomobject]@{ name = $formulaName; error = 'missing_shape' }
            continue
        }
        try {
            $mathZoneCount = [int]$shapeByName[$formulaName].TextFrame2.TextRange.MathZones.Count
            if ($mathZoneCount -lt 1) {
                $nativeFormulaViolations += [pscustomobject]@{ name = $formulaName; error = 'no_native_math_zone' }
            }
        } catch {
            $nativeFormulaViolations += [pscustomobject]@{ name = $formulaName; error = 'formula_type_read_error' }
        }
    }

    $arrowGeometryViolations = @()
    foreach ($arrowEntry in @($manifest.arrow_constraints)) {
        $arrowName = [string]$arrowEntry.name
        if (!$shapeByName.ContainsKey($arrowName)) {
            $arrowGeometryViolations += [pscustomobject]@{ name = $arrowName; error = 'missing_shape' }
            continue
        }
        try {
            $arrowShape = $shapeByName[$arrowName]
            $weight = [double]$arrowShape.Line.Weight
            $beginStyle = [int]$arrowShape.Line.BeginArrowheadStyle
            $endStyle = [int]$arrowShape.Line.EndArrowheadStyle
            $beginWidth = [int]$arrowShape.Line.BeginArrowheadWidth
            $endWidth = [int]$arrowShape.Line.EndArrowheadWidth
            $beginLength = [int]$arrowShape.Line.BeginArrowheadLength
            $endLength = [int]$arrowShape.Line.EndArrowheadLength
            $targetEnd = if ($null -ne $arrowEntry.target_end) { [string]$arrowEntry.target_end } else { 'end' }
            $targetStyle = if ($targetEnd -eq 'begin') { $beginStyle } else { $endStyle }
            $targetWidth = if ($targetEnd -eq 'begin') { $beginWidth } else { $endWidth }
            $targetLength = if ($targetEnd -eq 'begin') { $beginLength } else { $endLength }
            if ($null -ne $arrowEntry.require_solid_triangle -and [bool]$arrowEntry.require_solid_triangle -and $targetStyle -ne 2) {
                $arrowGeometryViolations += [pscustomobject]@{ name = $arrowName; error = 'target_arrowhead_not_triangle'; actual_style = $targetStyle }
            }
            $thinLineMax = if ($null -ne $arrowEntry.thin_line_max_pt) { [double]$arrowEntry.thin_line_max_pt } else { 1.3 }
            if ($weight -le $thinLineMax -and ($targetWidth -gt 1 -or $targetLength -gt 1)) {
                $arrowGeometryViolations += [pscustomobject]@{
                    name = $arrowName
                    error = 'thin_line_requires_narrow_short_head'
                    line_weight_pt = [Math]::Round($weight, 3)
                    arrowhead_width = $targetWidth
                    arrowhead_length = $targetLength
                }
            }
        } catch {
            $arrowGeometryViolations += [pscustomobject]@{ name = $arrowName; error = 'arrow_geometry_read_error' }
        }
    }

    $countMismatches = @()
    if ($null -ne $expectedShapeCount -and [int]$slide.Shapes.Count -ne $expectedShapeCount) {
        $countMismatches += "shape_count:$($slide.Shapes.Count)!=$expectedShapeCount"
    }
    if ($null -ne $expectedImageCount -and $images.Count -ne $expectedImageCount) {
        $countMismatches += "image_count:$($images.Count)!=$expectedImageCount"
    }
    if ($null -ne $expectedIconCount -and $icons.Count -ne $expectedIconCount) {
        $countMismatches += "icon_count:$($icons.Count)!=$expectedIconCount"
    }
    if ($null -ne $expectedConnectorCount -and $connectors.Count -ne $expectedConnectorCount) {
        $countMismatches += "connector_count:$($connectors.Count)!=$expectedConnectorCount"
    }

    $result = [ordered]@{
        ok = (
            $duplicates.Count -eq 0 -and
            $missingObjects.Count -eq 0 -and
            $unregisteredObjects.Count -eq 0 -and
            $layerViolations.Count -eq 0 -and
            $unconnectedEndpoints.Count -eq 0 -and
            $axisViolations.Count -eq 0 -and
            $textOverflows.Count -eq 0 -and
            $textMismatches.Count -eq 0 -and
            $textSafetyViolations.Count -eq 0 -and
            $textLengthViolations.Count -eq 0 -and
            $orphanLineViolations.Count -eq 0 -and
            $nativeFormulaViolations.Count -eq 0 -and
            $arrowGeometryViolations.Count -eq 0 -and
            $missingTextExpectations.Count -eq 0 -and
            $orphanTextExpectations.Count -eq 0 -and
            $countMismatches.Count -eq 0
        )
        full_name = $actualPath
        read_only = [bool]$presentation.ReadOnly
        slide_count = [int]$presentation.Slides.Count
        slide_index = $slideIndex
        shape_count = [int]$slide.Shapes.Count
        image_count = $images.Count
        icon_count = $icons.Count
        connector_count = $connectors.Count
        duplicate_name_count = $duplicates.Count
        missing_object_count = $missingObjects.Count
        unregistered_object_count = $unregisteredObjects.Count
        layer_violation_count = $layerViolations.Count
        unconnected_endpoint_count = $unconnectedEndpoints.Count
        axis_violation_count = $axisViolations.Count
        text_overflow_count = $textOverflows.Count
        text_mismatch_count = $textMismatches.Count
        text_safety_violation_count = $textSafetyViolations.Count
        text_length_violation_count = $textLengthViolations.Count
        orphan_line_violation_count = $orphanLineViolations.Count
        native_formula_violation_count = $nativeFormulaViolations.Count
        arrow_geometry_violation_count = $arrowGeometryViolations.Count
        missing_text_expectation_count = $missingTextExpectations.Count
        orphan_text_expectation_count = $orphanTextExpectations.Count
        count_mismatch_count = $countMismatches.Count
        render_path = $renderPath
        duplicates = $duplicates
        missing_objects = $missingObjects
        unregistered_objects = $unregisteredObjects
        layer_violations = $layerViolations
        unconnected_endpoints = $unconnectedEndpoints
        axis_violations = $axisViolations
        text_overflows = $textOverflows
        text_mismatches = $textMismatches
        text_safety_violations = $textSafetyViolations
        text_length_violations = $textLengthViolations
        orphan_line_violations = $orphanLineViolations
        native_formula_violations = $nativeFormulaViolations
        arrow_geometry_violations = $arrowGeometryViolations
        missing_text_expectations = $missingTextExpectations
        orphan_text_expectations = $orphanTextExpectations
        count_mismatches = $countMismatches
    }
    $json = $result | ConvertTo-Json -Depth 10
    [IO.File]::WriteAllText(
        (Join-Path $OutputDirectory 'native-audit.json'),
        $json,
        (New-Object System.Text.UTF8Encoding($false))
    )
    $json
} finally {
    if ($CloseTargetWhenDone -and $openedTargetByScript -and $null -ne $presentation) {
        try {
            $closingPath = [IO.Path]::GetFullPath([string]$presentation.FullName)
            if ([string]::Equals($closingPath, $expectedPath, [StringComparison]::OrdinalIgnoreCase)) {
                $presentation.Close()
            }
        } catch {}
    }
    if ($null -ne $presentation) {
        try { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation) } catch {}
    }
    if ($null -ne $app) {
        try { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($app) } catch {}
    }
    if ($null -ne $fileItem -and $null -ne $originalReadOnly) {
        try { $fileItem.IsReadOnly = [bool]$originalReadOnly } catch {}
    }
}
