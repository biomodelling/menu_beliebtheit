# Release Workflow

1. Bump version in `libs/__init__.py`
2. Update Twine `pip install --upgrade twine`
3. Create wheel: `python setup.py bdist`
4. Check build: `twine check dist/`
5. Upload to TestPy: `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
6. Check on TestPy if all worked out well.
7. Upload to PyPi: `twine upload dist/*`
8. Set Git Tag according to version number: `git tag -a <tag_name_starting_with_v> -m "message"`
9. Push to Github including the tags: `git push --tags`

## Future Improvements

- Use GitHub Actions for the whole process or at least for publishing.
