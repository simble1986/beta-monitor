//projects页面

$(function($){
    $('#addProjectModal').on('hidden.bs.modal', function () {
        $("#addProjectForm").removeClass("was-validated").trigger("reset");
    });
    $("#firstNewYes").click(function(){
        $("#firstNewConfirmModal").modal("hide");
        $("#addProjectModal").modal("show");
    })
});


function selectAllProjs(self){
    if ($(self).prop("checked")) {
        $(":checkbox[name='projSelect']").not(":disabled").each(function(){
　　　　　　this.checked=true;
　　　　});
    } else {
        $(":checkbox[name='projSelect']").not(":disabled").each(function(){
　　　　　　this.checked=false;
　　　　});
    }
}


//project列表显示
function displayProjects(owner="", page=1){
    var path = "getProjList";
    setProgress(30);
    $.get(path, {owner: owner, page: page},
        function(data){displayProjectsTable(data)}, 'json');
    setProgress(70);
    displayProjectPages(owner=owner);
    setProgress(90);
}

function displayProjectsTable(data){
    console.log(data);
    var projects = data.data;
    if (projects.length == 0){
        $("#firstNewConfirmModal").modal("show");
    }
    var htmlStr = "";
    htmlStr +=
        '<thead>' +
        '    <tr>' +
        '        <th scope="col text-center">' +
        '            <input class="form-check-inline" type="checkbox" id="checkedAll" onclick="selectAllProjs(this)">' +
        '        </th>' +
        '        <th scope="col">名称</th>' +
        '        <th scope="col">描述</th>';
    if ($("#myProjs").hasClass("active") == false)
    {
        htmlStr += '        <th scope="col">Owner</th>'
    }
    htmlStr +=
        '        <th scope="col">设备数</th>\n' +
        '        <th scope="col">操作</th>\n' +
        '    </tr>\n' +
        '</thead>' +
        '<tbody>';
    projects.forEach(v=> {
        console.log(v);
        htmlStr +=
            '<tr id="project_' + v.id + '">' +
            '   <th scope="row">' +
            '       <input value="' + v.id + '" project="' + v.name + '" name="projSelect" class="form-check-inline" type="checkbox" ';
        if (!v.deleteable){
            htmlStr += " disabled"
        }
        htmlStr +=
            '>' +
            '   </th>' +
            '   <td><a href="#" onclick="getProjectDetail(' + v.id + ')">' + v.name +  '</a></td>' +
            '   <td>' + v.desc +'</td>';
        if ($("#myProjs").hasClass("active") == false)
        {
            htmlStr += '   <td>' + v.owner + '</td>'

        }
        htmlStr +=
            '   <td><a href="#" onclick="displayDevices(' + v.id +')">' + v.dcount + '</a></td>' +
            '   <td >';
        if (v.editable){
            htmlStr +=
                '       <a href="#" onclick="getProjectDetail(' + v.id + ', true)" data-toggle="tooltip" title="编辑项目">' +
                '           <i class="fas fa-pen-square text-primary"></i>' +
                '       </a>'
        }
        if (v.rssable){
            htmlStr +=
                '        <a rel="projects" id="' + v.id + '" name="' + v.name + '" onclick="rssProject(' + v.id + ')" href="#" data-toggle="tooltip" title="关注动态">' +
                '            <i class="fas fa-rss-square" style="color: #fd7e14;"></i>' +
                '        </a>';
        }
        if (v.deleteable){
            htmlStr +=
                '       <a href="#" onclick="delProject(\'' + v.name +'\', ' + v.id + ')" data-toggle="tooltip" title="删除项目">' +
                '           <i class="fas fa-minus-square text-danger"></i>' +
                '       </a>'
        }
        htmlStr += '   </td>';
        htmlStr += '</tr>'
    });
    htmlStr += '</tbody>';
    $("#projLists").empty().append(htmlStr);
}

function displayProjectPages(owner="", per=10){
    var path = "getProjectPages";
    $.get(path,
        {owner: owner, per: 10},
        function(data){
        var pages = data.data.pages;
        var htmlStr = "";
        if($("#myProjs").hasClass("active") == true)
        {
            for (var i=0; i< (pages); i++)
            {
                htmlStr +=
                    '<li class="page-item"><a class="page-link" href="#" onclick="displayProjects(owner=' + owner + ', page=' + (i+1) + ')">' +
                    (i+1) + '</a></li>'
            }
        }
        else{
            for (var i=0; i< (pages); i++)
            {
                htmlStr +=
                    '<li class="page-item"><a class="page-link" href="#" onclick="displayProjects(owner=\'\', page=' + (i+1) + ')">' +
                    (i+1) + '</a></li>'
            }
        }
        $("#projectPages").empty().append(htmlStr);
        },
        'json')
}


function displayDevices(project="", page=1){
    var path = "getDeviceByProject";
    $.get(path,
        {project: project, page: page},
        function(data){displayDevicesTable(data)}, 'json');
    displayDevicePages(project=project);
    $("#showDevicesModal").modal("show");
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
        '       <th scope="col">名称</th>' +
        '       <th scope="col">Status</th>';
    htmlStr += '<th scope="col">Owner</th>' +
        '   </tr>' +
        '</thead>' +
        '<tbody>';
    devices.forEach(v=> {
        console.log(v);
        htmlStr +=
            '   <tr id="device_'+ v.id + '">' +
            '       <td>' +
            '           <a href="/detail/' + v.id + '">' + v.name + '</a>' +
            '       </td>' +
            '       <td>' +
            '           <span class="d-inline btn-sm status" data-toggle="tooltip" data-placement="top" title="' + v.status_info +'">' + v.status +'</span>' +
            '       </td>';
        htmlStr += '       <td>' + v.owner +'</td>';
        htmlStr += '</tr>'
    });
    htmlStr += '</tbody>';
    htmlStr += '<script>' +
        ' $(function($){renderStatus()})' +
        '</script>';
    $("#devLists").empty().append(htmlStr);
}

/**
 * 生成页码栏
 * @param project project id，默认为空，为空时，获取所有设备
 * @param per 每页显示条目数
 */
function displayDevicePages(project="", per=10){
    var path = "getDevicePagesByProject";
    $.get(path,
        {project: project, per: 10},
        function(data){
        var pages = data.data.pages;
        var htmlStr = "";
        for (var i=0; i< (pages); i++)
        {
            htmlStr +=
                '<li class="page-item"><a class="page-link" href="#" onclick="displayDevices(project=' + project + ', page=' + (i+1) + ')">' +
                (i+1) + '</a></li>'
        }
        $("#devPages").empty().append(htmlStr);
        },
        'json')
}

/**
 * 批量删除
 */
function delProjects(){
    var selectedObj = $("input[name=projSelect]:checked");
    if (selectedObj.length == 0) {
        $.toastr.warning("没有项目被选中")
    }
    else{
        var ids = new Array(), names = "";
        var path = '/projects';
        var i = 0;
        selectedObj.each(function(index) {
            ids.push(Number($(this).val()));
            i +=1;
            if (i <= 3) {
                names += "," + $(this).attr("project");
                }
            else if (i == 4) {
                names += "...";
                }
        });
        ids = JSON.stringify(ids);
        names = names.substr(1);
        $("#delProjConfirmInfo").html("<h5>你确认删除项目: <span class='text-danger'>" + names + "</span>吗？</h5><br>请确保已经删除该项目中的所有设备，否则项目将无法删除");
        $("#delProjModalYes").attr("onclick", "delItems('" + path + "', '" + ids + "')");
        $("#confirmModal").modal("show");
    }
}

/**
 * 单个删除
 */
function delProject(name, id){
    var path = '/projects';
    var ids = JSON.stringify([id]);
    $("#delProjConfirmInfo").html("<h5>你确认删除项目: <span class='text-danger'>" + name + "</span>吗？</h5><br>请确保已经删除该项目中的所有设备，否则项目将无法删除");
    $("#delProjModalYes").attr("onclick", "delItems('" + path + "', '" + ids + "')");
    $("#confirmModal").modal("show");
}

/**
 * 获取项目详情
 * @param id
 * @param editable 是否可编辑true or false，如果是查看详情，不能编辑,如果是编辑项目信息，可以编辑
 */
function getProjectDetail(id, editable) {
    $.get("/projects/detail", {'id': id}, function(data){getProjectDetailReturn(data,id, editable)}, 'json');
}

/**
 * 获取项目详情回调
 * @param data
 * @param id
 * @param editable
 */
function getProjectDetailReturn(data,id, editable) {
    console.log(data);
    if (data.result != "success") {
        alert(data.msg);
        return;
    }
    var detail = data.data;
    var htmlStr = "";
    htmlStr += '<div>';
    if (!editable) {
        htmlStr += '<fieldset disabled>';
    }
    htmlStr +=         '<div class="form-group row">'
            +          '<label class="col-3">名称</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" id="detailname" value="' + detail.name + '"required >'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">描述</label>'
            +          '<div class="col-9">'
            +              '<textarea type="text" class="form-control" id="detaildesc">' + detail.desc + '</textarea>'
            +          '</div>'
            +          '</div>';
    if (!editable) {
        htmlStr += '</fieldset>';
        $("#projDetailModalLabel").text("项目详细信息");
        $("#cancelBtn").removeClass("btn-default").addClass("btn-primary");
        $("#okBtn").css("display", "none").removeAttr("onclick");
    } else {
        $("#projDetailModalLabel").text("编辑项目");
        $("#cancelBtn").removeClass("btn-primary").addClass("btn-default");
        $("#okBtn").css("display", "").attr("onclick", "saveProjectInfo('" + id + "')");
    }
    htmlStr +=   '</div>';
    $("#detailInfo").empty().append(htmlStr).css("min-height", "240px");
    $("#projDetailModal").modal("show");

}

/**
 * 编辑保存项目
 * @param id
 */
function saveProjectInfo(id){
    var path = '/projects/edit';
    var params = JSON.stringify({
        "id": id,
        "name": $("#detailname").val().trim(),
//        "email": $("#detailowner").val().trim(),
        "desc": $("#detaildesc").val()
    });
    postItems(path, params);
    $("#projDetailModal").modal("hide");
}

/**
 * 新增项目
 */

function addProject(){
    var path = 'projects/add';
    var params = JSON.stringify({
        "name": $("#projName").val().trim(),
        "desc": $("#projDesc").val()
    });
    //console.log(params);
    var noteStr = "";
    if ($("#projName").val().trim() === ""){
        noteStr += "'Name' ";
    }
    if (noteStr != ""){
        noteStr += "must specified";
        $("#addProjectForm").addClass('was-validated');
        $.toastr.error(noteStr);
    }
    else{
        postItems(path, params);
        $("#addProjectModal").modal("hide");
    }
}

function rssProject(id) {
    $.get("/projects/rss", {'id': id}, function(data){getProjectRssReturn(data, id)}, 'json');
}

function getProjectRssReturn(data, id) {
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
            +  '    <div class="col-10" id=projectRssInfo">'
            +  '        <div class="form-group row">';
    if (rssdetail.rss_flag){
        htmlStr += '            <div class="col-5">'
        +  '                    <input class="form-check-inline" type="radio" id="projectRssenable" name="projectRssFlag" value=True checked>'
        +  '                    <label class="form-check-label form-control-sm" for="projectRssenable">Enable</label>'
        +  '                </div>'
        +  '                <div class="col-5">'
        +  '                    <input class="form-check-inline" type="radio" id="projectRssdisable" name="projectRssFlag" value=False>'
        +  '                    <label class="form-check-label form-control-sm" for="projectRssdisable">Disable</label>'
        +  '                </div>';
    }
    else{
        htmlStr += '            <div class="col-5">'
        +  '                    <input class="form-check-inline" type="radio" id="projectRssenable" name="projectRssFlag" value=True >'
        +  '                    <label class="form-check-label form-control-sm" for="projectRssenable">Enable</label>'
        +  '                </div>'
        +  '                <div class="col-5">'
        +  '                    <input class="form-check-inline" type="radio" id="projectRssdisable" name="projectRssFlag" value=False checked>'
        +  '                    <label class="form-check-label form-control-sm" for="projectRssdisable">Disable</label>'
        +  '                </div>';
    }
    
    htmlStr += '         </div>'
            +  '    </div>'
            +  '</div>'
            +  '<div class="form-group row">'
            +  '    <label class="col-2">收件人</label>'
            +  '    <div class="col-10">'
            +  '        <textarea class="form-control form-control-sm" aria-label="Description" id="projectRssMail" value="'+rssdetail.rss_mail+'" placeholder="请输入收件人邮箱地址，多个收件人以,分隔">'+rssdetail.rss_mail+'</textarea>'
            +  '    </div>'
            +  '</div>';
            

    $("#projectRssokBtn").css("display", "").attr("onclick", "saveProjectRssInfo('" + id + "')");
    htmlStr +=   '</div>';
    $("#projectRssInfo").empty().append(htmlStr).css("min-height", "240px");
    $("#projectRssModal").modal("show");
}

function saveProjectRssInfo(id){
    var path = '/projects/rss';
    var params = JSON.stringify({
        "id": id,
        "rss_flag":$("input[name=projectRssFlag]:checked").val(),
        "mail":$("#projectRssMail").val().trim()        
    });
    postItems(path, params);
    $("#projectRssModal").modal("hide");
}