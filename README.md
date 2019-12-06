# UDM Group Matrix

Generates a user-group matrix from an Univention Directory Manager export 

1. Create a UDM dump using `univention-directory-manager users/user list > userdump.txt`
2. Run `pipenv install` and `pipenv shell`.
3. Run `main.py`. It outputs CSV-data to stdout that you can redirect to disk and open with your favorite spreadsheet tool.
It also generates a graphical representation using matplotlib and saves that to `matrix.png`. 