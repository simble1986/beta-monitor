
/**
 * 公共函数：上传文件
 * @param path
 * @param item
 * @param reload
 */
function uploadFile(path, item, reload=true) {
    var formData = new FormData();
    formData.append(item, document.getElementById("inputAvatarImg").files[0]);
    $.ajax({
        type: "post",
        async: true,
        url: path,
        contentType: false,
        processData : false,
        data: formData,
        dataType: "json",
        success: function(data) {
            var status = data.status;
            var msg = data.msg;
            if (status) {
                $.toastr.success(msg)
            }
            else {
                $.toastr.warning(msg)
            }
        },
        error: function(){
            $.toastr.error("未知错误")
        }


    });
    if(reload){
        setTimeout("location.reload()",3000);
    }
}

/**
 * 公共函数：编辑对象，edit操作可尝试调用
 * @param path
 * @param params
 * @param reload
 */
function postItems(path, params, reload=true) {
    $.ajax({
        type: 'post',
        async: true,
        url: path,
        contentType: "json",
        dataType: "json",
        data : params,
        success: function(data) {
            var status = data.status;
            var msg = data.msg;
            if (status) {
                $.toastr.success(msg)
            }
            else {
                $.toastr.warning(msg)
            }
        },
        error: function(){
            $.toastr.error("未知错误")
        }

    });
    if(reload){
        setTimeout("location.reload()",3000);
    }
}


/**
 * 公共函数：删除对象，delete操作可尝试调用
 * @param path
 * @param id
 * @param reload
 */
function delItems(path, id, reload=true) {
    $.ajax({
        type: 'delete',
        async: true,
        url: path,
        contentType: "json",
        dataType: "json",
        data : id,
        success: function(data) {
            var status = data.status;
            var msg = data.msg;
            if (status) {
                $.toastr.success(msg)
            }
            else {
                $.toastr.warning(msg)
            }
        },
        error: function(){
            $.toastr.error("未知错误")
        }

    });
    $("#confirmModal").modal("hide");
    if(reload){
        setTimeout("location.reload()",3000);
    }
}

