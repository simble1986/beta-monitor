//Settings 页面



function showEmailForm(){
    var path = '/emailSetting';
    $.get(path,function(data){
        var mailSettings = data.data;
        var htmlStr = "";
        htmlStr += '<fieldset>' +
            '    <div class="row" hidden>' +
            '       <div class="form-group col-md-12">' +
            '           <input class="form-control" id="mailID" type="text" value="' + mailSettings.id + '" disabled>' +
            '       </div>' +
            '   </div>' +
            '   <div class="row">' +
            '       <div class="form-group col-md-12">' +
            '           <label class="font-weight-bold" for="mailHost">' +
            '               服务器' +
            '           </label>' +
            '           <input class="form-control" id="mailHost" type="text" value="' + mailSettings.host + '">' +
            '       </div>' +
            '   </div>' +
            '   <div class="row">' +
            '       <div class="form-group col-md-6">' +
            '           <label class="font-weight-bold" for="mailUser">' +
            '               用户名' +
            '           </label>' +
            '           <input class="form-control" id="mailUser" type="text" value="' + mailSettings.username + '">' +
            '        </div>' +
            '        <div class="form-group col-md-6">' +
            '           <label class="font-weight-bold" for="mailPassword">' +
            '               密码' +
            '           </label>' +
            '           <input class="form-control" id="mailPassword" type="password" value="' + mailSettings.password + '">' +
            '       </div>' +
            '   </div>' +
            '   <div class="row">' +
            '       <div class="form-group col-md-12">' +
            '           <label class="font-weight-bold" for="mailSender">' +
            '               发件者' +
            '           </label>' +
            '           <input class="form-control" id="mailSender" type="email" value="' + mailSettings.sender + '">' +
            '       </div>' +
            '   </div>' +
            '</fieldset>';
        $("#mailSettings").empty().append(htmlStr);
    },
    'json'
    )
}

function showEmailSetting(){
    if ($("input[name=userdef_email]").is(":checked"))
    {
        console.log("User defined Email setting enable");
        $("#mailSettings").show();
    } else {
        $("#mailSettings").hide();
    }
}

/**
 * 修改邮件信息
 */
function changeMail(){
    var path = '/mail';
    var params;
    if ($("input[name=userdef_email]").is(":checked")){
        console.log("update email settings");
        params = JSON.stringify({
            "id": $("#mailID").val().trim(),
            "host": $("#mailHost").val().trim(),
            "username": $("#mailUser").val().trim(),
            "password": $("#mailPassword").val().trim(),
            "sender": $("#mailSender").val().trim()
        });
    }
    else{
        // todo: reset the email with default
        params = JSON.stringify({
            "id": $("#mailID").val().trim(),
            "host": $("#mailHost").val().trim(),
            "username": $("#mailUser").val().trim(),
            "password": $("#mailPassword").val().trim(),
            "sender": $("#mailSender").val().trim()
        });
    }
    postItems(path, params, reload=false);
}


/**
 * 修改探测器信息
 */
function updateScan(){
    var path = 'setschedule';
    var params = JSON.stringify({
        "scantime": $("#scanTime").val().trim(),
        "dailyrepohour": $("#hourSelect").val().trim(),
        "dailyrepomin": $("#minSelect").val().trim(),
        "dailyrepoapm": $("#apm").val().trim()
    });
    postItems(path, params, reload=false);
}



function numChange(){
    var num=document.getElementById("scanTime");
    var location=document.getElementById("timeShow");
    location.value=num.value;
}

function showDailySetting(){
    var path = 'dailyReportSetting';
    $.get(path,function(data){
    displayDailySetting(data)
    },
    'json'
)}

function displayDailySetting(data){
    var dailySetting = data.data;
    var htmlStr = "";
    htmlStr += '<select id="hourSelect" class="custom-select col-2 custom-control-inline">';
    for (var i=1; i<=12; i++){
        htmlStr += '<option value=' + i + '>' + i + '</option>';
    }
    htmlStr += '</select>';
    htmlStr += '<select id="minSelect" class="custom-select col-2 custom-control-inline">';
    htmlStr += '<option value="0">00</option>';
    for (var i=10; i<=50; i=i+10){
        htmlStr += '<option value=' + i + '>' + i + '</option>';
    }
    htmlStr += '</select>';
    htmlStr += '<select id="apm" class="custom-select col-2 custom-control-inline">';
    htmlStr += '<option value="am">AM</option>';
    htmlStr += '<option value="pm">PM</option>';
    htmlStr += '</select>';
    console.log(dailySetting.hour);
    $("#dailyReportTime").empty().append(htmlStr);
    $("#hourSelect").val(dailySetting.hour);
    $("#minSelect").val(dailySetting.min);
    $("#apm").val(dailySetting.apm);
}

function showThemeSetting(){
    var path = '/themeSetting';
    $.get(path,function(data){
    displayThemeSetting(data)
    },
    'json'
)}

function displayThemeSetting(data){
    var themeSetting = data.data;
    var htmlStr = "";
    var themes = new Array("cosmo", "cyborg", "darkly", "flatly", "journal", "litera", "lumen", "lux", "materia", "minty", "pulse", "sandstone", "simplex", "sketchy", "slate", "solar", "spacelab", "superhero", "united", "yeti");
    htmlStr += '<select id="themeSelect" class="custom-select col-5 custom-control-inline">';
    htmlStr += '<option value="">default</option>';
    for (var i=0; i<themes.length; i++){
        htmlStr += '<option value=' + themes[i] + '>' + themes[i] + '</option>';
    }
    htmlStr += '</select>';
    $("#themeSetting").empty().append(htmlStr);
    $("#themeSelect").val(themeSetting);
}

function updateTheme(){
    var path = '/setTheme';
    var params = JSON.stringify({
        "theme": $("#themeSelect").val().trim(),
    });
    postItems(path, params, reload=true);
}