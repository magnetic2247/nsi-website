// Vars
var socket;
var socket_url = "ws://localhost:8080/socket";
var first_load = true;

// Onload - Main Function
window.onload = function() {
  // Connect to server
  connect();
  // Enter to send
  document.querySelector("input").addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      document.getElementById("send-btn").click();
    }
  });
};

// Connect to web socket
function connect() {
  // Create WebSocket Object
  socket = new WebSocket(socket_url);

  // Connection opened
  socket.onopen = function (event) {
    console.log("Connected Successfully");
    if (first_load) socket.send("all");
    first_load = false;
  };

  // Listen for messages
  socket.onmessage = function (event) {
    // Is session expired?
    if (event.data == "session_expired" || event.data == "not_logged_in") {
      // Redirect to login page
      location.href="/login";
    } 
    
    // Add new message
    message(event.data)
  };

  // Socket Closed
  socket.onclose = function() {
    console.log("Reconnecting...");
    setTimeout(function(){connect();}, 100);
  }
}

// Send message to server
function send() {
  // Get message from input
  var msg = document.querySelector("#msg-input").value;

  // Egg >:)
  if (msg == "egg") {
    egg();
    socket.send("egg");
    return;
  }

  // Check if message empty
  if (msg != "") {
    var json = {chat_id: window.current_chat, content: msg};
    socket.send(JSON.stringify(json));

    // Reset Message Bar
    document.querySelector("#msg-input").value = "";
  }
}

// Add Mesage to html
function message(cnt) {
  // Egg >:)
  if (cnt == "egg") {
    egg();
  }

  // Get and Process Data into JSON Object
  var data = JSON.parse(cnt);
  var chatid = data["chat_id"];
  var content = data["content"];
  var username = data["username"];

  // Get div for current chat
  var divs = document.getElementsByClassName("msgs");
  var msg_div = null;
  for (i=0;i<divs.length;i++) {
    if (divs[i].dataset.chatId == chatid) {
      var msg_div = divs[i];
      break;
    }
  }

  // Check if div is null
  if (msg_div == null) {
    first_load = true;
    socket.close();
    return;
  }

  // Create HTML Elements
  var msg_tag = document.createElement("p");
  var usr_tag = document.createElement("strong");
  usr_tag.innerHTML = username;
  msg_tag.appendChild(usr_tag);

  // Append message
  msg_tag.innerHTML += (" "+content);

  // Add HTML to Document
  msg_div.appendChild(msg_tag);

  // Scroll to bottom of div
  var chats_div = document.querySelector("#main");
  chats_div.scrollTop = chats_div.scrollHeight;
}

// Egg >:)
function egg() {
  var egg = new Image();
  egg.src = "https://magnetic2247.github.io/imgs/easter_egg.png";
  egg.style.height="100vh";
  document.body.innerHTML = "";
  document.body.style.textAlign = "center";
  document.body.appendChild(egg);
}
