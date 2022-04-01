# test_invoke_http.py
from invokes import invoke_http

# invoke book microservice to get all books
results = invoke_http("http://127.0.0.1:5000/listing", method='GET')

print( type(results) )
print()
print( results )
