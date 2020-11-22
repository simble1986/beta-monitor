$.toastr.config({
    time: 4000,
    position: 'top-right',
});

function setProgress(percent){
    $("#progressBar").show();
    var htmlStr = '<div class="progress-bar" role="progressbar" style="width: ' + percent +
        '%;" aria-valuenow="' + percent + '" aria-valuemin="0" aria-valuemax="100"></div>';
    $("#progressBar").empty().append(htmlStr);
    if(percent=100){
        setTimeout('$("#progressBar").hide()',1000);
    }
}

$(function($){
    setProgress(0);
    bsCustomFileInput.init();
    $('[data-toggle="tooltip"]').tooltip();
    getLoginUser();
    $('#loginModal').on('hidden.bs.modal', function () {
        $("#loginForm").removeClass("was-validated").trigger("reset");
        $("#registForm").removeClass("was-validated").trigger("reset");
    });
    // todo: 设备详情子页面如何展示
    $("#topMenu >li").each(function() {
        if($(this).find("a").attr("href")==window.location.pathname){
            $(this).addClass("active");
        }
        else{
            $(this).removeClass("active");
        }
    });
    setProgress(100);
});


function getLoginUser() {
    $.get("/getauth", function(data){doAuth(data)}, 'json');
    setProgress(25);
}

function doAuth(data){
    console.log(data);
    var htmlStr = "";
    htmlStr += '<a class="nav-link dropdown-toggle" href="#" id="loginMenu" role="button" data-toggle="dropdown"  aria-expanded="false">'
            +  '    <img class="rounded-circle" style="width: 30px; height: 30px;" src='
            +  data.avatar
            +  '></a>'
            +  '<div class="dropdown-menu dropdown-menu-right" aria-labelledby="loginMenu">'
            +  '<div class="dropdown-header"><h6 class="text-uppercase mb-0">'
            +  data.fullname
            +  '</h6>@' + data.name +'</div>'
            +  '<div class="dropdown-divider"></div>';
    if (data.id == '0'){
        htmlStr += '<a class="dropdown-item font-weight-light" href="#">Profile</a>'
                +  '<a class="dropdown-item font-weight-light" href="#">Settings</a>'
    }
    else{
        htmlStr += '<a class="dropdown-item font-weight-light" href="/profile">Profile</a>'
                +  '<a class="dropdown-item font-weight-light" href="/settings">Settings</a>'
    }
    htmlStr += '<div class="dropdown-divider"></div>'
            +  '<a class="dropdown-item font-weight-light" target="_blank" href="https://beta.testsite.com/ppg/beta-monitor/blob/master/CONTRIBUTING.md">'
            +  'Contribute <i class="fab fa-git-square"></i></a>'
            +  '<div class="dropdown-divider"></div>';
    if(data.login == '0'){
        htmlStr += '<a class="dropdown-item" data-toggle="modal" data-target="#loginModal" href="#">Login</a>'
    }
    else{
        htmlStr += '<a class="dropdown-item" data-toggle="modal" data-target="#logoutModal" href="#">Logout</a>'
    }
    htmlStr += '</div>';
    $("#useravatar").empty().append(htmlStr);
}

function login(self){
    var username = document.getElementById("loginusername");
    var password = document.getElementById("loginpassword");
    if( username.value == "" ){
        document.getElementById("usernameinvalid").hidden=false;
        username.classList.add("is-invalid")
    }
    else{
        document.getElementById("usernameinvalid").hidden=true;
        username.classList.add("is-valid")
    }
    if( password.value == "" ){
        document.getElementById("passwordinvalid").hidden=false;
        password.classList.add("is-invalid")
    }
    else{
        document.getElementById("passwordinvalid").hidden=true;
        password.classList.add("is-valid")
    }
    if( username.value == "" || password.value == "" ){
        return false
    }

    var path = 'login';
    var params = JSON.stringify({
        "username": $("#loginusername").val().trim(),
        "password": $("#loginpassword").val().trim(),
        "keeplogin": $("input[name=loginkeeplogin]").is(":checked")
    });
    postItems(path, params);
    $("#loginModal").modal("hide");
}

function logout(self){
    var path = 'logout';
    var params = JSON.stringify({});
    postItems(path, params);
    $("#logoutModal").modal("hide");
    setTimeout('window.location.href="/"', 3000);
}

function register(self){
    var path = 'register';
    var params = JSON.stringify({
        "username": $("#reguser").val().trim(),
        "fullname": $("#fullname").val().trim(),
        "password": $("#confpass").val().trim(),
        "email": $("#regemail").val().trim()
    });
        postItems(path, params);
    $("#loginModal").modal("hide");
}

function selectAll(self){
    if ($(self).prop("checked")) {
        /* $("input[name=projectselected]").prop("checked", true); */
        $(":checkbox[name='projectselected']").not(":disabled").each(function(){
　　　　　　this.checked=true;
　　　　});
    } else {
        /* $("input[name=projectselected]").prop("checked", false); */
        $(":checkbox[name='projectselected']").not(":disabled").each(function(){
　　　　　　this.checked=false;
　　　　});
    }
}

//用户页面

/**
 * 获取用户详情
 * @param id
 * @param editable 是否可编辑true or false，如果是查看详情，不能编辑,如果是编辑项目信息，可以编辑
 */
function getUserDetail(id, editable) {
    $.get("/users/detail", {'id': id}, function(data){getUserDetailReturn(data,id, editable)}, 'json');
}

/**
 * 获取用户详情回调
 * @param data
 * @param id
 * @param editable
 */
function getUserDetailReturn(data,id, editable) {
    console.log(data);
    if (data.result != "success") {
        alert(data.msg);
        return;
    }
    var detail = data.data;
    var group = new Array(1, 2);
    var groupname = new Array('Admin','User');
    var htmlStr = "";
    htmlStr += '<div>';
    if (!editable) {
        htmlStr += '<fieldset disabled>';
    }
    htmlStr +=         '<div class="form-group row">'
            +          '<label class="col-3">Name</label>'
            +          '<div class="col-8">'
            +              '<input type="text" class="form-control" id="detailname" value="' + detail.name + '"disabled >'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">FullName</label>'
            +          '<div class="col-8 input-group">'
            +              '<input type="text" class="form-control" id="detailfullname" value="' + detail.fullname + '">'
            +          '</div>'
            +          '</div>'
            +  '<div class="form-group row">'
            +  '    <label class="col-3 col-form-label" for="os">OS</label>'
            +  '        <div class="col-8">'
            +  '            <select id="detailgroup" class="form-control form-control-sm">';
    for (var i=0;i<group.length;i++){
        if(detail.group == group[i]){
            htmlStr += '<option selected value="' + group[i] + '">' + groupname[i] + '</option>'
        }
        else{
            htmlStr += '<option value="' + group[i] + '">' + groupname[i] + '</option>'
        }
    }
    htmlStr += '            </select>'
            +  '        </div>'
            +          '</div>'
            +          '</div>';
    if (!editable) {
        htmlStr += '</fieldset>';
        $("#myModalLabel").text("用户详细信息");
        $("#cancelBrn").removeClass("btn-default").addClass("btn-primary");
        $("#okBtn").css("display", "none").removeAttr("onclick");
    } else {

        $("#myModalLabel").text("更新用户信息");
        $("#cancelBrn").removeClass("btn-primary").addClass("btn-default");
        $("#okBtn").css("display", "").attr("onclick", "saveUserInfo('" + id + "')");
    }
    htmlStr +=   '</div>';
    $("#detailInfo").empty().append(htmlStr).css("min-height", "240px");
    $("#detailModal").modal("show");

}

/**
 * 编辑保存用户
 * @param id
 */
function saveUserInfo(id){
    var path = '/users/edit';
    var params = JSON.stringify({
        "id": id,
        "fullname": $("#detailfullname").val().trim(),
        "group": $("#detailgroup").val().trim()
    });
    postItems(path, params);
    $("#detailModal").modal("hide");

}

/**
 * 删除用户
 */
function delUser(name, id){
    var path = '/users';
    var ids = JSON.stringify([id]);
    $("#confirmInfo").html("<h5>你确认删除用户: <span class='text-danger'>" + name + "</span>吗？</h5>");
    $("#ModalYes").attr("onclick", "delItems('" + path + "', '" + ids + "')");
    $("#confirmModal").modal("show");
}

/**
 * 重设密码为beta
 * @param id
 */
function resetPassword(id){
    var path = '/users/reset';
    var ids = JSON.stringify([id]);
    $("#resetModal").modal("show");
    $("#confirmreset").html("<h5>你确认重置密码为: <span class='text-danger'> beta </span>吗？</h5>");
    $("#resetYes").attr("onclick", "resetandclose('" + path + "', '" + ids + "', reload=false)");
}

function resetandclose(path,id){
    postItems(path, id, reload=false);
    $("#resetModal").modal("hide");
}



function renderStatus(){
    $("span.status").each(function(){
        if (this.textContent == "UNKNOWN")
        {
            $(this).removeClass("status").addClass("btn btn-outline-secondary");
            $(this).prepend('<i class="fas fa-minus-circle"></i> ');
        }
        else if(this.textContent == "ONLINE" || this.textContent == "PASS")
        {
            $(this).removeClass("status").addClass("btn btn-outline-success");
            $(this).prepend('<i class="fas fa-check-circle"></i> ');
        }
        else if(this.textContent == "COREDUMP" || this.textContent == "ABORT")
        {
            $(this).removeClass("status").addClass("btn btn-outline-warning");
            $(this).prepend('<i class="fas fa-info-circle"></i> ');
        }
        else if(this.textContent == "OFFLINE" || this.textContent == "FAIL")
        {
            $(this).removeClass("status").addClass("btn btn-outline-danger");
            $(this).prepend('<i class="fas fa-times-circle"></i> ');
        }
        else if(this.textContent == "PENDING")
        {
            $(this).removeClass("status").addClass("btn btn-outline-primary");
            $(this).prepend('<i class="fas fa-pause-circle"></i> ');
        }
        else if(this.textContent == "RUNNING")
        {
            $(this).removeClass("status").addClass("btn btn-outline-success");
            $(this).prepend('<i class="fas fa-spinner fa-pulse"></i> ');
        }
        else
        {
            $(this).removeClass("status").addClass("btn btn-outline-dark");
        }
    });
}
