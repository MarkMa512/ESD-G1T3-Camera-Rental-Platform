# test_invoke_http.py
from invokes import invoke_http

# invoke book microservice to get all books
results = invoke_http("http://localhost:5000/rental", method='GET')

print( type(results) )
print()
print( results )
