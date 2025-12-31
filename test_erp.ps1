Write-Host "--- DIAGNOSTIC PERIMONT ERP ---" -ForegroundColor Cyan

# 1. Test des dossiers
$folders = "database", "utils", "ui", "exports", "assets/photos"
foreach ($f in $folders) {
    if (Test-Path $f) { Write-Host "[OK] Dossier $f trouvé" -ForegroundColor Green }
    else { Write-Host "[ERREUR] Dossier $f manquant" -ForegroundColor Red }
}

# 2. Test de la base de données
if (Test-Path "database/perimont.db") {
    Write-Host "[OK] Base de données trouvée" -ForegroundColor Green
} else {
    Write-Host "[ALERTE] Fichier .db non détecté" -ForegroundColor Yellow
}

# 3. Test des dépendances Python
Write-Host "Vérification des bibliothèques..." -ForegroundColor Gray
python -c "import customtkinter, fpdf, PIL, cv2, sqlite3; print('[OK] Toutes les dépendances sont installées')" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERREUR] Dépendances manquantes. Lancez : pip install -r requirements.txt" -ForegroundColor Red
}

Write-Host "--- FIN DU TEST ---" -ForegroundColor Cyan