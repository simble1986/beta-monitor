//Profile 页面

/**
 * 修改用户信息
 */
function updateUser(){
    var path = '/users/edit';
    var params = JSON.stringify({
        "id": $("#userID").val().trim(),
        "fullname": $("#myfullname").val().trim(),
        "email": $("#myemail").val().trim(),
        "password": $("#myconfrim").val().trim()
    });
    postItems(path, params);
}

function uploadAvatar() {
    if($("#inputAvatarImg").val().trim() != ""){
        path = "/uploadavatar";
        item = "avatar";
        uploadFile(path, item);
    }
    else{
        console.log("No avatar given")
    }
}

function clearAvatar() {
    $("#clearAvatarModal").modal("hide");
    path = "/deleteavatar";
    delItems(path, id="");
}
