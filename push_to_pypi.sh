rm -rf dist
rm -rf build
rm -rf fluorseg.egg-info
python setup.py sdist bdist_wheel
python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*