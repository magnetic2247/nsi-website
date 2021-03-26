var xhttp = new XMLHttpRequest();

// Login to account
function login() {
    document.querySelector("form").submit();
}

// Register for an account
function register() {
    // On server response
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Check if username is available
            if (xhttp.responseText == "ok") {
                // Check if passwords match
                if (document.getElementById("pass1").value == document.getElementById("pass2").value) {
                    // All good, submit the form
                    document.querySelector("form").submit();
                }
                else {
                    // Passwords don't match, warn user
                    document.querySelector("#error").innerHTML = "Passwords don't match";
                }
            }
            else {
                // Username taken, warn user
                document.querySelector("#error").innerHTML = "Username already taken";
            }
        }
    };
    // XML Http Request
    xhttp.open("GET", "/api/username/"+document.querySelector("input").value, true);
    xhttp.send();
}

// Run after page loaded
window.onload = function() {
    const url_params = new URLSearchParams(window.location.search);
    // Username of Password was incorrect
    if(url_params.has('error')) {
        document.querySelector("#error").innerHTML = "Username or Password Incorrect";
    }
}