// Libraries
var bbparser = new bbcode.Parser();

// Vars
var socket;
var socket_url = "ws://localhost:8080/socket";
var first_load = true;

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
    // Messages Div
    var msg_div = document.querySelector("#msgs");

    // Get and Process Data into JSON Object
    console.log(event.data);
    var data = JSON.parse(event.data);

    // Create HTML Elements
    var msg_tag = document.createElement("p");
    var usr_tag = document.createElement("b");
    usr_tag.innerHTML = data["usrname"];
    msg_tag.appendChild(usr_tag);
    msg_tag.innerHTML += (" "+bbparser.toHTML(data["message"]));

    // Add HTML to Document
    msg_div.appendChild(msg_tag);

    // Scroll to bottom of div
    msg_div.scrollTop = msg_div.scrollHeight;
  };

  // Socket Closed
  socket.onclose = function() {
    console.log("Reconnecting...");
    setTimeout(function(){connect();}, 100);
  }
}

// Onload
window.onload = function() {
  connect();
  window.username = prompt("username");

  // Enter to send
  document.querySelector("input").addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      document.getElementById("send-btn").click();
    }
  });
};

// Send message to server
function send() {
  // Send Message
  var msg = document.querySelector("#msg-input").value;
  var json = {message: msg, usrname: window.username};
  socket.send(JSON.stringify(json));

  // Reset Message Bar
  document.querySelector("#msg-input").value = "";
}

// Egg
function egg() {
  var egg = new Image();
  egg.src = "https://magnetic2247.github.io/imgs/easter_egg.png";
  egg.style.height="100%";
  document.body.innerHTML = "";
  document.body.style.textAlign = "center";
  document.body.appendChild(egg);
}
