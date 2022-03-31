<?php
  session_start();
  $user_id = $_SESSION['user_id'];
  $someVar = 1 # test
?>


<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=device-width">
    

    <title>Update rental Status</title>
    <!--[if lt IE 9]>
      <script src="//html5shiv.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
    <!-- Bootstrap libraries -->
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">


    <!-- Bootstrap CSS -->
    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css'
        rel='stylesheet'
        integrity='sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC'
        crossorigin='anonymous'>

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>

    <style>
        .form-group{
            margin-bottom:10px;
        }
    </style>

</head>

<body>
    <h1 class="display-4 m-4 container mx-auto">Search Rental Status</h1>

    <form id='SearchRental' class="p-4 container">

        <button type="submit" class="btn btn-primary mt-2">Retrieve Rentals</button>
    </form>

    <div id="results">
        <table id="rentalTable" class='table table-striped border-1' id='rental-list' >
            <thead class='border-1'>
                <th>Listing ID</th>
                    <th>Rental ID</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Total rent price</th>
                    <th>Status</th>

            </thead>
        </table>
    </div>

    <div id="results">
        <form id="status" method="GET">
            <input type="submit" value="Confirm">
        </form>
    </div>

    <label id="error" class="text-danger"></label>
    <script>

        // Helper function to display error message
        function showError(message) {
            // Display an error under the the predefined label with error as the id
            $("#results").hide();
            $('#error').text(message);
            $('#error').show();
            $('#status').hide();
        }

        $(async (event) => {

            //Get form data
            var owner = $("#owner_id").val();
            var serviceURL = "http://192.168.18.17:5000/rental" +"/"+ "<?php echo $someVar; ?>";

            try {
                    const response =
                        await fetch(
                            serviceURL, { method: 'GET' }
                        );
                    const data = await response.json();

                    if (response.status === 200) {
                        var rentals = data.data;
                        console.log(rentals);
                        end_date = new Date(rentals.rent_end_date)
                        end_date = end_date.toDateString()
                        start_date = new Date(rentals.rent_start_date)
                        start_date = start_date.toDateString()

                       row ="<td>" + rentals.listing_id + "</td>" +
                                "<td> <input type='hidden' id='rental_id' value="+ rentals.rental_id + ">" + rentals.rental_id + "</td>" +
                                "<td>" +start_date + "</td>" +
                                "<td>" + end_date + "</td>" +
                                "<td> $" + rentals.total_price + "</td>" +
                                "<td>" + 
                                    "<select class='form-select' id='status' aria-label='Default select example'>" +
                                    "<option selected>" + rentals.rental_status + "</option>"
                                    + "<option value='Approved'> Approved </option>"
                                    + "<option value='Delivered'>Delivered</option>"
                                    + "<option value='Returned'>Returned</option>"
                                    + "</select>"
                                    + "</td>"
                                ;
                    
                        // add all the rows to the table
                        $('#rentalTable').append(row);

                    } else if (response.status == 404) {
                        // No books
                        showError(result.message);
                    } else {
                        // unexpected outcome, throw the error
                        throw response.status;
                    }
                
            } catch (error) {
                // Errors when calling the service; such as network error, 
                // service offline, etc
                showError
                    ("There are no rental request, please try again later. " + error);

            } // error
        });


        $("#status").submit(async (event) => {
            //Prevents screen from refreshing when submitting
            event.preventDefault();

            //Get form data
            var rental_id = $("#rental_id").val();
            var rental_status = $('#status').val();
            console.log(rental_id)
            console.log(rental_status)

            var serviceURL = "http://192.168.18.17:5000/rental" +"/"+ rental_id;
            
            try {
                const response =
                    await fetch(
                        serviceURL,{method: 'put',
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({rental_status:rental_status})

            });
                const data = await response.json();


                if (response.ok) {
                    // relocate to home page
                    window.location.replace("index.html");
                    return false;

                } else {
                    console.log(data);
                    showError(data.message);
                }

            } catch (error) {
                // Errors when calling the service; such as network error, 
                // service offline, etc
                showError
                    ("There is a problem adding this update, please try again later. " + error);

            } // error
        });

    </script>

    <!-- Bootstrap Javascript -->
    <script src='https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js'
        integrity='sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM'
        crossorigin='anonymous'></script>

</body>

</html>
