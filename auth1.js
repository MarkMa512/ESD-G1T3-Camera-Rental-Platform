auth.onAuthStateChanged(user => {
    console.log(user)
})

const signupForm = document.querySelector("#signUpForm");


signupForm.addEventListener('submit', (e) => {
    e.preventDefault();

    //get user info
    const username = signupForm['signUpUsername'].value;
    const email = signupForm['signUpEmail'].value;
    const password = signupForm['signUpPswd'].value;
    const address = signupForm['signUpAddress'].value;
    const phone = signupForm['signUpPhone'].value

    console.log(email, password)

    //sign up the user
    if (username === "") {
        swal("Oh no!", "Username cannot be empty.", "error")
    } else {

        auth.createUserWithEmailAndPassword(email, password).then(cred => {

            console.log(cred.user)

            db.collection('users').doc(cred.user.uid).set({
                user_name: signupForm['signUpUsername'].value,
                user_email: signupForm['signUpEmail'].value,
                residential_address: signupForm['signUpAddress'].value,
                phone: signupForm['signUpPhone'].value

            });

            // cred.user.updateProfile({
            //     displayName: document.getElementById("signUpUsername").value
            // })

            signupForm.reset()

            swal("Done!", "You have successfully signed up!", "success").then(function () {
                window.location = 'index.html';
            }
            )

        })
            .catch(error => swal("Oh no!", error.message, "error"))

    }

})

// google sign in still doesnt work, need time to figure out later
function googleSignIn() {
    var provider = new firebase.auth.GoogleAuthProvider();
    firebase.auth().signInWithPopup(provider).then(function (result) {
        // This gives you a Google Access Token. You can use it to access the Google API.
        var token = result.credential.accessToken;
        // The signed-in user info.
        var user = result.user;
        // ...
    }).catch(function (error) {
        // Handle Errors here.
        var errorCode = error.code;
        var errorMessage = error.message;
        // The email of the user's account used.
        var email = error.email;
        // The firebase.auth.AuthCredential type that was used.
        var credential = error.credential;
        // ...
    });

    firebase.auth().signInWithRedirect(provider);
    firebase.auth().getRedirectResult().then((result) => {
    if (result.credential) {
      /** @type {firebase.auth.OAuthCredential} */
      var credential = result.credential;

      // This gives you a Google Access Token. You can use it to access the Google API.
      var token = credential.accessToken;
      // ...
    }
    // The signed-in user info.
    var user = result.user;
  }).catch((error) => {
    // Handle Errors here.
    var errorCode = error.code;
    var errorMessage = error.message;
    // The email of the user's account used.
    var email = error.email;
    // The firebase.auth.AuthCredential type that was used.
    var credential = error.credential;
    // ...
  });

}

firebase.auth().signOut().then(function () {
    // Sign-out successful.
}).catch(function (error) {
    // An error happened.
});