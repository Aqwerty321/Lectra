# Create minimal placeholder icons for Tauri
$iconsDir = "C:\edgettstest\LECTRA\ui\src-tauri\icons"

# Minimal 16x16 ICO file (valid ICO format with a simple black square)
$icoBase64 = "AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAA/4QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREAAAAAA"
$icoBytes = [Convert]::FromBase64String($icoBase64)
[IO.File]::WriteAllBytes("$iconsDir\icon.ico", $icoBytes)

# Create other required icon sizes as copies
Copy-Item "$iconsDir\icon.ico" "$iconsDir\32x32.png" -Force
Copy-Item "$iconsDir\icon.ico" "$iconsDir\128x128.png" -Force
Copy-Item "$iconsDir\icon.ico" "$iconsDir\128x128@2x.png" -Force
Copy-Item "$iconsDir\icon.ico" "$iconsDir\icon.icns" -Force

Write-Host "Icons created successfully!" -ForegroundColor Green
