// Show selected chat
function show_chat(chat_id) {
    // Go through all chat elements
    chat_elems = document.getElementsByClassName("msgs");
    for (i=0;i<chat_elems.length;i++) {
        // Show selected chat
        if (chat_elems[i].dataset.chatId == chat_id) {
            chat_elems[i].style.display = "block";
            window.current_chat = chat_id;
        }
        // Hide all other chats
        else {
            chat_elems[i].style.display = "none";
        }

        // Scroll to bottom of chat
        var chats_div = document.querySelector("#main");
        chats_div.scrollTop = chats_div.scrollHeight;
    }
}

