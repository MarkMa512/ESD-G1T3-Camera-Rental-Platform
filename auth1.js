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

//login
const loginForm = document.querySelector("#loginForm");
loginForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const email = loginForm['loginEmail'].value;
    const password = loginForm['loginPswd'].value;

    console.log(email, password)

    auth.signInWithEmailAndPassword(email, password).then(cred => {
        console.log(cred.user)
        loginForm.reset()

        swal("Done!", "You have successfully login!", "success").then(function () {
            window.location = 'index.html';
        }
        )

    }).catch(error => swal("Oh no!", error.message, "error"))


})

function showLogin() {
    console.log('login btn clicked')
    var loginpage = document.getElementById('login')
    var signuppage = document.getElementById('register')

    signuppage.style.display = 'none'
    login.style.display = 'block'

}
function loginWithGoogle(event) {
    var provider = new firebase.auth.GoogleAuthProvider();
    firebase.auth()
        .signInWithPopup(provider)
        .then((result) => {
            // /** @type {firebase.auth.OAuthCredential} */
            var credential = result.credential;
            console.log('google', credential)
            var token = credential.accessToken;
           
            var user = result.user;
            // console.log(user.email, user.display_name)
            console.log('google sign in', user)
            window.location = 'index.html';

            // auth.createUserWithEmailAndPassword(email, password).then(cred => {

            //     console.log(cred.user)

            //     db.collection('users').doc(cred.user.uid).set({
            //         user_name: signupForm['signUpUsername'].value,
            //         user_email: signupForm['signUpEmail'].value,
            //         residential_address: signupForm['signUpAddress'].value,
            //         phone: signupForm['signUpPhone'].value

            //     });
            // })
            //     .catch(error => console.log(error.message))


        }).catch((error) => {
            // Handle Errors here.
            var errorCode = error.code;
            var errorMessage = error.message;
            // The email of the user's account used.
            var email = error.email;
            // The firebase.auth.AuthCredential type that was used.
            var credential = error.credential;
            console.log(error)
        });

}
firebase.auth().signOut().then(function () {
    // Sign-out successful.
}).catch(function (error) {
    // An error happened.
});