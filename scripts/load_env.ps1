param(
    [string]$Path = ".env"
)

if (-not (Test-Path $Path)) {
    throw "Environment file not found: $Path"
}

Get-Content $Path | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) {
        return
    }

    $parts = $line -split "=", 2
    if ($parts.Count -ne 2) {
        return
    }

    $key = $parts[0].Trim()
    $value = $parts[1].Trim().Trim('"').Trim("'")
    Set-Item -Path "Env:$key" -Value $value
}

Write-Host "Loaded environment variables from $Path"
