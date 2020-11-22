/**
 * 设备页面
 */

$(function($) {
    $('#addDeviceModal').on('hidden.bs.modal', function () {
        $("#addDeviceForm").removeClass("was-validated").trigger("reset");
    });
    $("#projectEmptyInfoModal").on('hidden.bs.modal', function () {
        $("#addDeviceForm").modal("hide");
    });
    $("#addDeviceModal").on('shown.bs.modal', function(){
        renderProjectList();
    });
});
/**
 * 全选按钮动作
 */
function selectAllDevs(self){
    if ($(self).prop("checked")) {
        $(":checkbox[name='devSelect']").not(":disabled").each(function(){
　　　　　　this.checked=true;
　　　　});
    } else {
        $(":checkbox[name='devSelect']").not(":disabled").each(function(){
　　　　　　this.checked=false;
　　　　});
    }
}

/**
 * renderProjectList
 * 为添加设备的modal生成project列表
 */
function renderProjectList(){
    var path = "getMyProjList";
    $.get(path, function(data){
        console.log(data);
        var projects = data.data;
        if (projects.length == 0){
            $("#addDeviceModal").modal("hide");
            $("#projectEmptyInfoModal").modal("show");
        }
        var htmlStr = "";
        projects.forEach(v=> {
            htmlStr += '<option value="' + v.id + '">' + v.name + '</option>'
        });
        $("#project").empty().append(htmlStr);

    },
        'json');
}

/**
 * displayDevices 读取后台设备列表并生成对应的表格
 * @param owner owner id，默认为空，为空时，为所有用户设备列表
 * @param page 页码
 */
function displayDevices(owner="", page=1){
    var path = "getDeviceList";
    setProgress(30);
    $.get(path,
        {owner: owner, page: page},
        function(data){displayDevicesTable(data)}, 'json');
    setProgress(70);
    displayDevicePages(owner=owner);
    setProgress(90);
}

/**
 * 生成设备列表
 * @param data
 */
function displayDevicesTable(data){
    console.log(data);
    var devices = data.data;
    var htmlStr = "";
    htmlStr +=
        '<thead>' +
        '   <tr>' +
        '       <th scope="col text-center">' +
        '           <input class="form-check-inline" type="checkbox" id="checkedAll" onclick="selectAllDevs(this)">' +
        '       </th>' +
        '       <th scope="col">名称</th>' +
        '       <!--th scope="col">部署方式</th-->' +
        '       <th scope="col">Status</th>';
    if ($("#myDevs").hasClass("active") == false){
        htmlStr += '<th scope="col">Owner</th>'
    }
    htmlStr += '       <th scope="col">项目</th>' +
               '       <th scope="col">操作</th>';
    htmlStr += '   </tr>' +
        '</thead>' +
        '<tbody>';
    devices.forEach(v=> {
        console.log(v);
        htmlStr +=
            '   <tr id="device_'+ v.id + '"';
        if (v.plat_license < 30){
            htmlStr += "bgcolor=\"#FFE773\"";
        }
        htmlStr += '>' +
            '       <th scope="row">' +
            '           <input value="' + v.id + '" device="' + v.name +'" name="devSelect" class="form-check-inline" type="checkbox" ';
        if (! v.deleteable){
            htmlStr += " disabled"
        }
        htmlStr +=
            '>' +
            '       </th>' +
            '       <td>' +
            '           <a href="/detail/' + v.id + '">' + v.name + '</a>' +
            '       </td>' +
            '       <!--td>' + v.deploy + '</td-->' +
            '       <td>' +
            '           <span class="d-inline btn-sm status" data-toggle="tooltip" data-placement="top" title="' + v.status_info +'">' + v.status +'</span>' +
            '       </td>';
        if ($("#myDevs").hasClass("active") == false){
            htmlStr += '       <td>' + v.owner +'</td>'
        }
        htmlStr += '       <td>' + v.project + '</td>' +
                   '    <td>';
        if (v.editable) {
            htmlStr +=
                '        <a href="#" onclick="editDevice(' + v.id + ')" data-toggle="tooltip" title="修改设备信息">' +
                '            <i class="fas fa-pen-square text-primary"></i>' +
                '        </a>'
        }
        if (v.runable) {
            htmlStr +=
                '        <a href="#" onclick="runScanNow(' + v.id + ')" data-toggle="tooltip" title="立即扫描">' +
                '            <i class="far fa-caret-square-right text-success"></i>' +
                '        </a>'
        }
        if (v.rssable){
            htmlStr +=
                '        <a rel="devices" id="' + v.id + '" name="' + v.name + '" onclick="rssDevice(' + v.id + ')" href="#" data-toggle="tooltip" title="关注动态">' +
                '            <i class="fas fa-rss-square" style="color: #fd7e14;"></i>' +
                '        </a>';
        }
        if (v.deleteable) {
            htmlStr +=
                '        <a rel="devices" id="' + v.id + '" name="' + v.name + '" onclick="delDevice(\'' + v.name + '\', ' + v.id + ')" href="#" data-toggle="tooltip" title="删除设备">' +
                '            <i class="fas fa-minus-square text-danger"></i>' +
                '        </a>'
        }
        htmlStr += '   </td>';
        htmlStr += '</tr>';
    });
    htmlStr += '</tbody>';
    htmlStr += '<script>' +
        ' $(function($){renderStatus()})' +
        '</script>';
    $("#devLists").empty().append(htmlStr);
}

/**
 * 生成页码栏
 * @param owner owner id，默认为空，为空时，获取所有设备
 * @param per 每页显示条目数
 */
function displayDevicePages(owner="", per=10){
    var path = "getDevicePages";
    $.get(path,
        {owner: owner, per: 10},
        function(data){
        var pages = data.data.pages;
        var htmlStr = "";
        if($("#myDevs").hasClass("active") == true)
        {
            for (var i=0; i< (pages); i++)
            {
                htmlStr +=
                    '<li class="page-item"><a class="page-link" href="#" onclick="displayDevices(owner=' + owner + ', page=' + (i+1) + ')">' +
                    (i+1) + '</a></li>'
            }
        }
        else{
            for (var i=0; i< (pages); i++)
            {
                htmlStr +=
                    '<li class="page-item"><a class="page-link" href="#" onclick="displayDevices(owner=\'\', page=' + (i+1) + ')">' +
                    (i+1) + '</a></li>'
            }
        }
        $("#devicePages").empty().append(htmlStr);
        },
        'json');
    setProgress(80);
}


function runScanNow(id) {
    var path = "addTask";
    params = JSON.stringify({
        "id": id
    });
    postItems(path, params,reload=false);
}

/**
 * 新增设备
 */
function addDevice() {
    var path = 'devices/add';
    var params = JSON.stringify({
        "name": $("#name").val().trim(),
        "project": $("#project").val(),
//        "owner": $("#owner").val().trim(),
        "ip": $("#ip").val().trim(),
        "sn": $("#sn").val().trim(),
        "os": $("#os").val().trim(),
        "user": $("#user").val().trim(),
        "password": $("#password").val().trim(),
        "ssh": $("#ssh").is(":checked"),
        "ssh_port": $("#sshPort").val().trim(),
        "telnet": $("#telnet").is(":checked"),
        "telnet_port": $("#telnetPort").val().trim(),
        // "rest_api": $("#rest_api").is(":checked"),
        // "rest_url": $("#rest_url").val().trim(),
        "deploy": $("input[name=deploy]:checked").val(),
        "desc": $("#detaildesc").val(),
        "admin_status": $("#admin_status").is(":checked"),
        "daily_report": $("#daily_report").is(":checked")
    });
    var noteStr = "";
    if ($("#name").val().trim() === ""){
        noteStr += "'Device Name' ";
    }
    if ($("#project").val() === ""){
        noteStr += "'Project' ";
    }
    if ($("#ip").val().trim() === ""){
        noteStr += "'IP' ";
    }
    if (noteStr != ""){
        noteStr += "must specified";
        $("#addDeviceForm").addClass('was-validated');
        $.toastr.error(noteStr);
    }
    else{
        postItems(path, params);
        $("#addDeviceModal").modal("hide");
    }
}

function editDevice(id) {
    $.get("/devices/detail", {'id': id}, function(data){getDeviceDetailReturn(data, id)}, 'json');
}


function getDeviceDetailReturn(data, id) {
    console.log(data);
    setProgress(10);
    if (data.result != "success") {
        alert(data.msg);
        return;
    }
    var detail = data.data;
    var projects = data.projects;
    var os = new Array('StoneOS','WAF','BDS','NIPS');
    var htmlStr = "";
    htmlStr += '<div class="m-3">';
    htmlStr += '<div class="form-group row">'
            +  '    <label class="col-2">名称</label>'
            +  '    <div class="col-4">'
            +  '        <input type="text" class="form-control form-control-sm" id="detailname" value="' + detail.name + '" required>'
            +  '    </div>'
            +  '    <label class="col-2">项目</label>'
            +  '    <div class="col-4">'
            +  '         <select id="detailproject" class="form-control form-control-sm">';

    for(var key in projects){
        if(detail.pid == key){
            htmlStr += '<option selected value="' + key + '">' + projects[key] + '</option>'
        }
        else{
            htmlStr += '<option value="' + key + '">' + projects[key] + '</option>'
        }
    }
    htmlStr += '        </select>'
            +  '    </div>'
            +  '</div>'
            +  '<div class="form-group row">'
            +  '    <label class="col-2">用户名</label>'
            +  '    <div class="col-4">'
            +  '        <input type="text" class="form-control form-control-sm" id="detailuser" value="' + detail.user +'">'
            +  '    </div>'
            +  '    <label class="col-2">密码</label>'
            +  '    <div class="col-4">'
            +  '        <input type="password" class="form-control form-control-sm" id="detailpassword" value="' + detail.password +'">'
            +  '    </div>'
            +  '</div>'
            +  '<div class="form-group row">'
            +  '    <label class="col-2 col-form-label">管理IP</label>'
            +  '    <div class="col-4">'
            +  '        <input type="text" class="form-control form-control-sm" id="detailip" value="' + detail.ip + '"required>'
            +  '    </div>'
            +  '    <label class="col-2 col-form-label">S/N</label>'
            +  '    <div class="col-4">'
            +  '        <input type="text" class="form-control form-control-sm" id="detailsn" value="' + detail.sn + '">'
            +  '    </div>'
            +  '</div>'
            +  '<div class="form-group row">'
            +  '    <label class="col-2 col-form-label" for="os">OS</label>'
            +  '        <div class="col-4">'
            +  '            <select id="detailos" class="form-control form-control-sm">';
    for (var i=0;i<os.length;i++){
        if(detail.os == os[i]){
            htmlStr += '<option selected value="' + os[i] + '">' + os[i] + '</option>'
        }
        else{
            htmlStr += '<option value="' + os[i] + '">' + os[i] + '</option>'
        }
    }
    htmlStr += '            </select>'
            +  '        </div>'
            +  '    <!--label class="col-2">Owner</label>'
            +  '    <div class="col-4 input-group">'
            +  '        <input type="email" class="form-control form-control-sm" id="detailowner" aria-describedby="basic-addon2" value="' + detail.owner + '"disabled>'
            +  '    </div-->'
            +  '</div>'
            +  '<div class="form-group row">'
            +  '    <label class="col-2 col-form-label">连接方式</label>'
            +  '    <div class="col-10">'
            +  '        <div class="form-group row mb-0">'
            +  '            <div class="col-2">';
    if (detail.ssh){
        htmlStr += '                <input class="form-check-inline" type="checkbox" id="detailssh" name="detailssh" checked>'
    }
    else{
        htmlStr += '                <input class="form-check-inline" type="checkbox" id="detailssh" name="detailssh">'
    }
    htmlStr += '            <label class="col-form-label col-form-label-sm" for="detailssh">SSH</label>'
            +  '            </div>'
            +  '            <div class="col-4">'
            +  '                <input type="text" class="form-control form-control-sm" id="detailsshPort" value="' + detail.ssh_port + '"/>'
            +  '            </div>'
            +  '            <div class="col-2">';
    if (detail.telnet){
        htmlStr += '                <input class="form-check-inline" type="checkbox" id="detailtelnet" name="detailtelnet" checked>'
    }
    else{
        htmlStr += '                <input class="form-check-inline" type="checkbox" id="detailtelnet" name="detailtelnet">'
    }
    htmlStr += '            <label class="col-form-label col-form-label-sm" for="detailtelnet">Telnet</label>'
            +  '            </div>'
            +  '            <div class="col-4">'
            +  '                <input type="text" class="form-control form-control-sm" id="detailtelnetPort" value="' + detail.telnet_port + '"/>'
            +  '            </div>'
            +  '            <!--div class="col-2">';
    if (detail.rest_api){
        htmlStr += '                <input class="form-check-inline" type="checkbox" id="detailrest_api" name="detailreset_api" checked>'
    }
    else{
        htmlStr += '                <input class="form-check-inline" type="checkbox" id="detailrest_api" name="detailrest_api">'
    }
    htmlStr += '                <label class="col-form-label col-form-label-sm" for="detailresst_api">Rest API</label>'
            +  '            </div-->'
            +  '        </div>'
            +  '    </div>'
            +  '</div>'
            +  '<!--div class="form-group row">'
            +  '    <label class="col-2">部署模式</label>'
            +  '    <div class="col-10" id="detailDeploy">'
            +  '        <div class="form-group row">'
            +  '            <div class="col-5">';
    if (detail.deploy == 1){
        htmlStr += '                <input class="form-check-inline" type="radio" id="detailinline" name="detaildeploy" value="inline" checked>'
            +  '                <label class="form-check-label form-control-sm" for="detailinline">In-Line</label>'
            +  '            </div>'
            +  '            <div class="col-5">'
            +  '                <input class="form-check-inline" type="radio" id="detailtap" name="detaildeploy" value="tap">'
    }
    else{
        htmlStr += '                <input class="form-check-inline" type="radio" id="detailinline" name="detaildeploy" value="inline">'
            +  '                <label class="form-check-label form-control-sm" for="detailinline">In-Line</label>'
            +  '            </div>'
            +  '            <div class="col-5">'
            +  '                <input class="form-check-inline" type="radio" id="detailtap" name="detaildeploy" value="tap" checked>'
    }
    htmlStr += '                <label class="form-check-label form-control-sm" for="detailtap">Tap</label>'
            +  '            </div>'
            +  '        </div>'
            +  '    </div>'
            +  '</div-->'
            +  '<div class="form-group row">'
            +  '    <label class="col-2">描述</label>'
            +  '    <div class="col-10">'
            +  '        <textarea type="text" class="form-control"  id="devDesc">' + detail.desc + '</textarea>'
            +  '    </div>'
            +  '</div>'
            +  '<div class="form-group row">'
            +  '    <div class="col-2"></div>'
            +  '    <div class="col-10">'
            +  '        <div class="custom-control custom-control-inline custom-switch">';
    if(detail.admin_status){
        htmlStr += '        <input class="custom-control-input" type="checkbox" id="detailadmin_status" name="detailadmin_status" checked>'
    }
    else{
        htmlStr += '        <input class="custom-control-input" type="checkbox" id="detailadmin_status" name="detailadmin_status">'
    }
    htmlStr += '        <label class="custom-control-label" for="detailadmin_status">已上线</label>'
            +  '        </div>'
            +  '        <div class="custom-control custom-control-inline custom-switch">';
    if(detail.daily_report){
        htmlStr += '        <input class="custom-control-input" type="checkbox" id="detaildaily_report" name="detaildaily_report" checked>'
    }
    else{
        htmlStr += '        <input class="custom-control-input" type="checkbox" id="detaildaily_report" name="detaildaily_report">'
    }
    htmlStr += '        <label class="custom-control-label" for="detaildaily_report">开启日报</label>'
            +  '        </div>'
            +  '    </div>'
            +  '</div>';
    $("#myModalLabel").text("编辑设备");
    $("#cancelBrn").removeClass("btn-primary").addClass("btn-dark");
    $("#okBtn").css("display", "").attr("onclick", "saveDeviceInfo('" + id + "')");
    htmlStr +=   '</div>';
    $("#detailInfo").empty().append(htmlStr).css("min-height", "240px");
    $("#detailModal").modal("show");
    setProgress(100);
}

function saveDeviceInfo(id){
    var path = '/devices/edit';
    var params = JSON.stringify({
        "id": id,
        "name": $("#detailname").val().trim(),
        "project": $("#detailproject").val(),
//        "owner": $("#detailowner").val().trim(),
        "ip": $("#detailip").val().trim(),
        "sn": $("#detailsn").val().trim(),
        "os": $("#detailos").val().trim(),
        "user": $("#detailuser").val().trim(),
        "password": $("#detailpassword").val().trim(),
        "ssh": $("#detailssh").is(":checked"),
        "ssh_port": $("#detailsshPort").val().trim(),
        "telnet": $("#detailtelnet").is(":checked"),
        "telnet_port": $("#detailtelnetPort").val().trim(),
        // "rest_api": $("#detailrest_api").is(":checked"),
        // "rest_url": $("#detailrest_url").val().trim(),
        "deploy": $("input[name=detaildeploy]:checked").val(),
        "desc": $("#devDesc").val(),
        "admin_status": $("#detailadmin_status").is(":checked"),
        "daily_report": $("#detaildaily_report").is(":checked")
    });
    postItems(path, params);
    $("#detailModal").modal("hide");
}

function delDevices(){
    var selectedObj = $("input[name=devSelect]:checked");
    if (selectedObj.length == 0) {
        $.toastr.warning("没有设备被选中")
    }
    else{
        var ids = new Array(), names = "";
        var path = '/devices';
        var i = 0;
        selectedObj.each(function(index) {
            ids.push(Number($(this).val()));
            i +=1;
            if (i <= 3) {
                names += "," + $(this).attr("device");
                }
            else if (i == 4) {
                names += "...";
                }
        });
        ids = JSON.stringify(ids);
        names = names.substr(1);
        $("#delDevConfirmInfo").html("<h5>你确认删除设备: <span class='text-danger'>" + names + "</span>吗？</h5>");
        $("#delDevModalYes").attr("onclick", "delItems('" + path + "', '" + ids + "')");
        $("#confirmModal").modal("show");
    }
}

/**
 * 单个删除
 */
// todo: 详细信息残留问题
function delDevice(name, id){
    var path = '/devices';
    var ids = JSON.stringify([id]);
    $("#delDevConfirmInfo").html("<h5>你确认删除设备: <span class='text-danger'>" + name + "</span>吗？</h5>");
    $("#delDevModalYes").attr("onclick", "delItems('" + path + "', '" + ids + "')");
    $("#confirmModal").modal("show");
}

function rssDevice(id) {
    $.get("/devices/rss", {'id': id}, function(data){getDeviceRssReturn(data, id)}, 'json');
}

function getDeviceRssReturn(data, id) {
    console.log(data);
    if (data.result != "success") {
        alert(data.msg);
        return;
    }
    var rssdetail = data.data;
    // todo: 是否对projects按照user进行处理了
    //var projects = data.projects;
    //var os = new Array('StoneOS','WAF','BDS','NIPS');
    var htmlStr = "";
       
    
    htmlStr += '<div class="form-group row">'
            +  '    <label class="col-2">订阅</label>'
            +  '    <div class="col-10" id="deviceRssInfo">'
            +  '        <div class="form-group row">';
    if (rssdetail.rss_flag){
        htmlStr += '            <div class="col-5">'
        +  '                    <input class="form-check-inline" type="radio" id="rssenable" name="deviceRssFlag" value=True checked>'
        +  '                    <label class="form-check-label form-control-sm" for="rssenable">Enable</label>'
        +  '                </div>'
        +  '                <div class="col-5">'
        +  '                    <input class="form-check-inline" type="radio" id="rssdisable" name="deviceRssFlag" value=False>'
        +  '                    <label class="form-check-label form-control-sm" for="rssdisable">Disable</label>'
        +  '                </div>';
    }
    else{
        htmlStr += '            <div class="col-5">'
        +  '                    <input class="form-check-inline" type="radio" id="rssenable" name="deviceRssFlag" value=True >'
        +  '                    <label class="form-check-label form-control-sm" for="rssenable">Enable</label>'
        +  '                </div>'
        +  '                <div class="col-5">'
        +  '                    <input class="form-check-inline" type="radio" id="rssdisable" name="deviceRssFlag" value=False checked>'
        +  '                    <label class="form-check-label form-control-sm" for="rssdisable">Disable</label>'
        +  '                </div>';
    }
    
    htmlStr += '         </div>'
            +  '    </div>'
            +  '</div>'
            +  '<div class="form-group row">'
            +  '    <label class="col-2">收件人</label>'
            +  '    <div class="col-10">'
            +  '        <textarea class="form-control form-control-sm" aria-label="Description" id="rssMail" value="'+rssdetail.rss_mail+'" placeholder="请输入收件人邮箱地址，多个收件人以,分隔">'+rssdetail.rss_mail+'</textarea>'
            +  '    </div>'
            +  '</div>';
            

    $("#rssokBtn").css("display", "").attr("onclick", "saveRssInfo('" + id + "')");
    htmlStr +=   '</div>';
    $("#rssInfo").empty().append(htmlStr).css("min-height", "240px");
    $("#rssModal").modal("show");
}

function saveRssInfo(id){
    var path = '/devices/rss';
    var params = JSON.stringify({
        "id": id,
        "rss_flag":$("input[name=deviceRssFlag]:checked").val(),
        "mail":$("#rssMail").val().trim()        
    });
    postItems(path, params);
    $("#rssModal").modal("hide");
}
