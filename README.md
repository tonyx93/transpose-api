## Requirements

- Python 3.10+

## Starting the Development Server

1. `pip install -r requirements.txt`
2. `flask --app transpose_api run`

## Sample API calls
Simple Implementation: `curl -d '[[1,2,3,4],[4,5,6,7],[7,8,9,0]]' -H 'Content-Type: application/json; charset=utf-16' http://localhost:5000/simple`

Explicit Implementation: `curl -d '[[1,2,3,4],[4,5,6,7],[7,8,9,0]]' -H 'Content-Type: application/json; charset=utf-16' http://localhost:5000/explicit`

Raw Implementation: `curl -d '[[1,2,3,4],[4,5,6,7],[7,8,9,0]]' -H 'Content-Type: application/json; charset=utf-16' http://localhost:5000/raw`