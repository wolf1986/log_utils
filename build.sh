pytest -vv -s
python -m build --sdist --wheel

cat <<-"_EOF"
  # Reminder: How to setup ~/.pypirc
  [pypi]
  username = __token__
  password = <TOKEN FROM PyPI>

  [testpypi]
  username = __token__
  password = <TOKEN FROM PyPI-TEST>
_EOF

twine upload --repository testpypi dist/*
#twine upload dist/*
