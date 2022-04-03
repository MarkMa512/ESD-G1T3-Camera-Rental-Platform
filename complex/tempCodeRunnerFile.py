



@app.route("/place_rental", methods=['POST'])
def place_rental():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try: