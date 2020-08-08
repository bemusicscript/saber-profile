var translate_input = document.getElementById("id_search");
let typingTimer;
let doneTypingInterval = 500;

translate_input.addEventListener('keyup', () => {
    clearTimeout(typingTimer);
    if (translate_input.value) {
        typingTimer = setTimeout(doneTyping, doneTypingInterval);
    }
});

function doneTyping() {
    $(".user_div").hide();
    $(".profile_div").hide();
    $(".user_not_found").hide();

    $(".loader_anim").attr("src", "/static/img/loading.gif");
    $(".loader>.loader_anim").show();
    data = new FormData();
    data.append('user_id', translate_input.value);

    console.log(data);

    fetch('/api/user/search', {
        method: 'POST',
        mode: 'cors',
        body: data
    })
    .then((response) => response.json())
    .then((result) => {
        $(".loader>.loader_anim").hide();
        $(".user_div").show();
        var user = result['result'];
        if(result.result != null){
            $(".profile_border .img").attr("src", user['profile_image']);
            $(".user .name").text(user['name']);
            $(".user .name").attr('id', user['id']);
        }
        else{
            $(".user_div").hide();
            $('.user_not_found').show();
        }
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}

$('.profile_border').on('click', function(){

    $(".profile_border").hide();
    $(".loader_anim").attr("src", "/static/img/loading.gif");
    $(".loader>.loader_anim").show();

    data = new FormData();
    player_id = $(".user>.name").attr('id');
    data.append('player_id', player_id);
    fetch('/api/user/get_data', {
        method: 'POST',
        mode: 'cors',
        body: data
    })
    .then((response) => response.json())
    .then((result) => {
        $(".loader>.loader_anim").hide();
        $(".profile_image").empty();
        $(".profile_div").empty();
        if(result.path != null){
            window.location.href = '/u/'+ result.id;
            var image = new Image();
            $(".loader>.loader_anim").hide();
            create_share_icons();
            $("<img>", { "src": result.path, }).appendTo(".profile_image");
            $(".share").attr('id', result.id);
        }
        else{
            $('.user_not_found').show();
        }
    })
    .catch((error) => {
      console.error('Error:', error);
    });
});