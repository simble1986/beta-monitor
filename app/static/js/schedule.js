/**
 * 全选按钮动作
 */
function selectAllTasks(self){
    if ($(self).prop("checked")) {
        $(":checkbox[name='taskSelect']").not(":disabled").each(function(){
　　　　　　this.checked=true;
　　　　});
    } else {
        $(":checkbox[name='taskSelect']").not(":disabled").each(function(){
　　　　　　this.checked=false;
　　　　});
    }
}


//任务页面

function displayTasks(type="", page=1){
    setProgress(30);
    var path = "getSchedules";
    var per;
    if(type == "current"){
        per=50;
    }
    else{
        per=200;
    }
    console.log(per);
    $.get(path, {type: type, page: page, per: per},
        function(data){displayTasksTable(data)}, 'json');
    setProgress(70);
    displayTasksPages(type=type);
    setProgress(90);
}

function displayTasksTable(data){
    console.log(data);
    var projects = data.data;
    var htmlStr = "";
    htmlStr +=
        '<thead>' +
        '    <tr>' +
        '        <th scope="col text-center">' +
        '            <input class="form-check-inline" type="checkbox" id="checkedAll" onclick="selectAllTasks(this)">' +
        '        </th>' +
        '        <th scope="col">ID</th>' +
        '        <th scope="col">Device Name</th>' +
        '        <th scope="col">Start Time</th>';
    if ($("#current").hasClass("active") == true)
    {
        htmlStr += '        <th scope="col">Expected Start Time</th>' +
                   '        <th scope="col">Status</th>'
    }
    else{
        htmlStr += '        <th scope="col">End Time</th>' +
                   '        <th scope="col">Result</th>'
    }
    htmlStr +=
        '        <th scope="col">Action</th>' +
        '    </tr>\n' +
        '</thead>' +
        '<tbody>';
    projects.forEach(v=> {
        console.log(v);
        htmlStr +=
            '<tr id="task_' + v.id + '">' +
            '   <th scope="row">' +
            '       <input value="' + v.id + '" name="taskSelect" class="form-check-inline" type="checkbox" >' +
            '   </th>' +
            '   <td><a href="#" onclick="getTaskDetail(' + v.id + ')">' + v.id +  '</a></td>' +
            '   <td><a href="/detail/' + v.device_id  + '">' + v.device_name +'</a></td>';
        if ($("#current").hasClass("active") == true)
        {
            htmlStr += '   <td>' + v.schedule_time + '</td>' +
                       '   <td>' + v.start_time + '</td>' +
                       '   <td><span class="d-inline btn-sm status" data-toggle="tooltip" data-placement="top" title="' + v.status_info + '">' + v.status + '</span></td>'
        }
        else
        {
            htmlStr += '   <td>' + v.start_time + '</td>' +
                       '   <td>' + v.end_time + '</td>' +
                       '   <td><span class="d-inline btn-sm status" data-toggle="tooltip" data-placement="top" title="' + v.result_info + '">' + v.result + '</span></td>'
        }
        htmlStr +=
            '    <td>' +
            '        <a href="#" onclick="delTask(' + v.id + ')">' +
            '            <i class="fas fa-minus-square text-danger"></i>' +
            '        </a>' +
            '    </td>';

    });
    htmlStr += '</tbody>';
    htmlStr += '<script>' +
        ' $(function($){renderStatus()})' +
        '</script>';
    $("#taskLists").empty().append(htmlStr);
}

function displayTasksPages(type=""){
    var path = "getTaskPages";
    var type = type;
    var per;
    if(type == "current"){
        per=50;
    }
    else{
        per=200;
    }
    $.get(path,
        {type: type, per: per},
        function(data){
        var pages = data.data.pages;
        var htmlStr = "";
        if($("#current").hasClass("active") == true)
        {
            for (var i=0; i< (pages); i++)
            {
                htmlStr +=
                    '<li class="page-item"><a class="page-link" href="#" onclick="displayTasks(type=' + "'current'" + ', page=' + (i+1) + ')">' +
                    (i+1) + '</a></li>'
            }
        }
        else{
            for (var i=0; i< (pages); i++)
            {
                htmlStr +=
                    '<li class="page-item"><a class="page-link" href="#" onclick="displayTasks(type=' + "'history'" + ', page=' + (i+1) + ')">' +
                    (i+1) + '</a></li>'
            }
        }
        $("#taskPages").empty().append(htmlStr);
        },
        'json')
}

/**
 * 获取任务详情
 */
function getTaskDetail(id, editable) {
    if ($("#current").hasClass("active") == true)
    {
        $.get("tasks/detail", {'id': id}, function(data){getTaskDetailReturn(data,id, editable)}, 'json');
    }
    else{
        $.get("historytasks/detail", {'id': id}, function(data){getHistoryTaskDetailReturn(data,id, editable)}, 'json');
    }
}

/**
 * 获取任务详情回调
 * @param data
 * @param id
 * @param editable
 */
function getTaskDetailReturn(data,id, editable) {
    console.log(data);
    if (data.result != "success") {
        alert(data.msg);
        return;
    }
    var detail = data.data;
    var htmlStr = "";
    htmlStr += '<form >';
    if (!editable) {
        htmlStr += '<fieldset disabled>';
    }
    htmlStr +=         '<div class="form-group row">'
            +          '<label class="col-3">ID</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" value="' + detail.id + '"readonly >'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">设备名称</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" value="' + detail.device_name + '">'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">开始时间</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" value="' + detail.schedule_time + '">'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">更新时间</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" value="' + detail.update_time + '">'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">状态</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" value="' + detail.status + '">'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">日志</label>'
            +          '<div class="col-9">'
            +              '<textarea type="text" class="form-control" id="desc">' + detail.log + '</textarea>'
            +          '</div>'
            +          '</div>';
    if (!editable) {
        htmlStr += '</fieldset>';
        $("#myModalLabel").text("任务详细信息");
        $("#cancelBrn").removeClass("btn-default").addClass("btn-primary");
    }

    htmlStr +=   '</form>';
    $("#detailInfo").empty().append(htmlStr).css("min-height", "240px");
    $("#detailModal").modal("show");

}


/**
 * 获取历史任务详情回调
 * @param data
 * @param id
 * @param editable
 */
function getHistoryTaskDetailReturn(data,id, editable) {
    console.log(data);
    if (data.result != "success") {
        alert(data.msg);
        return;
    }
    var detail = data.data;
    var htmlStr = "";
    htmlStr += '<div >';
    if (!editable) {
        htmlStr += '<fieldset disabled>';
    }
    htmlStr +=         '<div class="form-group row">'
            +          '<label class="col-3">ID</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" value="' + detail.id + '"readonly >'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">设备名称</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" value="' + detail.device_name + '">'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">开始时间</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" value="' + detail.start_time + '">'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">结束时间</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" value="' + detail.end_time + '">'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">运行结果</label>'
            +          '<div class="col-9">'
            +              '<input type="text" class="form-control" value="' + detail.result + '">'
            +          '</div>'
            +          '</div>'
            +          '<div class="form-group row">'
            +          '<label class="col-3">日志</label>'
            +          '<div class="col-9">'
            +              '<textarea type="text" class="form-control" id="desc">' + detail.log + '</textarea>'
            +          '</div>'
            +          '</div>';
    if (!editable) {
        htmlStr += '</fieldset>';
        $("#myModalLabel").text("历史任务详细信息");
        $("#cancelBrn").removeClass("btn-default").addClass("btn-primary");
    }

    htmlStr +=   '</div>';
    $("#detailInfo").empty().append(htmlStr).css("min-height", "240px");
    $("#detailModal").modal("show");
}

/**
 * 批量删除任务
 */
function delTasks(){
    var selectedObj = $("input[name=taskSelect]:checked");
    if (selectedObj.length == 0) {
        $.toastr.warning("没有任务被选中");
    }
    else{
        var ids = new Array(), taskids = "";
        if ($("#current").hasClass("active") == true)
        {
            var path = '/tasks';
        }
        else{
            var path = '/historytasks';
        }
        var i = 0;
        selectedObj.each(function(index) {
            ids.push(Number($(this).val()));
            i +=1;
            if (i <= 3) {
                taskids += "," + $(this).attr("value");
                }
            else if (i == 4) {
                taskids += "...";
                }
        });
        ids = JSON.stringify(ids);
        taskids = taskids.substr(1);
        $("#confirmInfo").html("<h5>你确认删除任务ID: <span class='text-danger'>" + taskids + "</span>吗？</h5>");
        $("#ModalYes").attr("onclick", "delItems('" + path + "', '" + ids + "')");
        $("#confirmModal").modal("show");
    }
}

/**
 * 删除任务
 */
function delTask(id){
    if ($("#current").hasClass("active") == true)
    {
        var path = '/tasks';
    }
    else{
        var path = '/historytasks';
    }
    var ids = JSON.stringify([id]);
    $("#confirmInfo").html("<h5>你确认删除任务ID: <span class='text-danger'>" + id + "</span>吗？</h5>");
    $("#ModalYes").attr("onclick", "delItems('" + path + "', '" + ids + "')");
    $("#confirmModal").modal("show");
}
