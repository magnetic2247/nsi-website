var xhttp = new XMLHttpRequest();

// Start script
get_username();

// Get username
function get_username() {
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Username as response
            var username = xhttp.responseText;

            // Server says user not logged in
            if (username == "not_logged_in") {
                location.href="/login";
            }

            // Callback next function
            get_chats(username);
        }
    }
    xhttp.open("GET", "/api/logged-in", true);
    xhttp.send();
}

// Get chats for user
function get_chats(name) {
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // JSON Object containing all the chats the user is in
            var chats = JSON.parse(this.responseText);

            // Go through the chats and add the right elements
            for (i=0;i<Object.keys(chats).length;i++) {
                create_div(chats[i]);
            }
        }
    }
    xhttp.open("GET", "/api/chats/"+name, true);
    xhttp.send();
}

// Create divs for each chat
function create_div(data) {
    // Get and Process Data into JSON Object
    var chatid = data["chat_id"];
    var chat_name = data["name"];

    // Create Main Chat Element
    var chat_elem = document.createElement("div");
    chat_elem.dataset.chatId = chatid;
    chat_elem.className = "msgs";

    // Create Menu Element
    var menu_elem = document.createElement("p");
    menu_elem.innerHTML = chat_name;    
    menu_elem.dataset.chatId = chatid;
    menu_elem.className = "menu_element";
    menu_elem.onclick = function(){show_chat(chatid)};

    // Show if default chat
    if (chatid == 1) {
        chat_elem.style.display="block";
        window.current_chat = 1;
    }

    // Append elements to page
    document.querySelector("#main").appendChild(chat_elem);
    document.querySelector("#menu").appendChild(menu_elem);
}

// Add new chat through API
function new_chat() {
    // Handle response
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200 && this.responseText == "ok") {
            // Reset page
            document.querySelector("#menu").innerHTML = "<h1>Messages <img onclick='new_chat()' src='/images/plus.svg' alt='New Chat' /></h1>";
            document.querySelector("#main").innerHTML = "";

            // Reload chats
            get_username();
        }
    };

    // Send request
    xhttp.open("GET", "/api/create-chat/"+prompt("Nom du nouveau chat"), true);
    xhttp.send();
}

// Add user to current chat
function add_members() {
    xhttp.onreadystatechange = function(){};
    xhttp.open("GET", "/api/add-user-chat/"+prompt("Pseudo de l'utilisateur à ajouter")+"/"+window.current_chat, true);
    xhttp.send();
}
