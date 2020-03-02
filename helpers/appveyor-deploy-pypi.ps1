Write-Output ("APPVEYOR_REPO_TAG: " + $Env:APPVEYOR_REPO_TAG)

if ($Env:APPVEYOR_REPO_TAG -eq 'true') {
  Write-Output ("Deploying " + $Env:APPVEYOR_REPO_TAG_NAME + " to PyPI...")
  & "${Env:PYTHON}/python.exe" -m pip install twine
  & "${Env:PYTHON}/python.exe" -m twine upload -u ${Env:PYPI_USER} -p ${Env:PYPI_PASS} --skip-existing dist/*.whl
}
else {
  Write-Output "No tag for deployment"
}