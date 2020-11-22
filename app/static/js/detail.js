function displayMyDevices(){
    var path = "getMyDevices";
    setProgress(30);
    $.get(path,
        function(data){showMyDevices(data)}, 'json');
    setProgress(70);
}

function showMyDevices(data) {
    console.log(data);
    var devices = data.data;
    var htmlStr = "";
    devices.forEach(v=> {
        console.log(v);
        htmlStr += '<button class="btn ' + v.status + '" id="' + v.id + '" onclick="renderContent(this)" style="margin: 2px">' + v.name + '</button>'
    });
    htmlStr += ' <div class="row">\n' +
        '            <div class="col">\n' +
        '                <hr class="text-dark" style="margin: 12px">\n' +
        '            </div>\n' +
        '            <div class="col-md-auto" style="padding:0" id="down" onclick="updown(\'up\')">\n' +
        '                <i class="fas fa-chevron-down"></i>\n' +
        '            </div>\n' +
        '            <div class="col-md-auto" style="padding:0; display: none" id="up" onclick="updown(\'down\')">\n' +
        '                <i class="fas fa-chevron-up"></i>\n' +
        '            </div>\n' +
        '            <div class="col">\n' +
        '                <hr class="text-dark" style="margin: 12px">\n' +
        '            </div>\n' +
        '        </div>';
    htmlStr += '<script>$(function($){renderBtnStatus(); hideItems()})</script>';
    $("#myHeader").empty().append(htmlStr);
}

function hideItems(){
    $("#up").hide();
    var myWidth=10;
    $("button.btn").each(function(){
        if((myWidth+this.offsetWidth)<$("#myHeader")[0].offsetWidth){
            this.hidden=false;
        }
        else{
            this.hidden=true;
        }
        myWidth += this.offsetWidth+10;
        });
}

function renderBtnStatus(){
    $("button").each(function(){
        if ($(this).hasClass("UNKNOWN"))
        {
            $(this).removeClass("UNKNOWN").addClass("btn-outline-secondary");
        }
        else if($(this).hasClass("ONLINE"))
        {
            $(this).removeClass("ONLINE").addClass("btn-outline-success");
        }
        else if($(this).hasClass("COREDUMP"))
        {
            $(this).removeClass("COREDUMP").addClass("btn-outline-warning");
        }
        else if($(this).hasClass("OFFLINE"))
        {
            $(this).removeClass("OFFLINE").addClass("btn-outline-danger");
        }
    });
}

function renderContent(data){
    p1 = 'btn-outline-([a-z]+)';
    p2 = 'border-[a-z]+';
    $("button.btn").each(function(){
        $(this).removeClass("active");
    });
    $(data).addClass("active");
    for (i=0; i<data.classList.length; i++){
        m = data.classList[i].match(p1);
        if(m != null){
            for(j=0; j<$("#myCard")[0].classList.length; j++){
                n = $("#myCard")[0].classList[j].match(p2);
                if(n != null){
                    $("#myCard").removeClass(n[0]).addClass("border-"+m[1])
                    $("#myHeader").removeClass(n[0]).addClass("border-"+m[1])
                }
            }
        }
    }
    showContent(data);
}


function showContent(item){
    var path = "deviceStatus";
    $.get(path, {id: item.id}, function(data){
        console.log(data);
        var status = data.data;
        var htmlStr = "Current Status: " + status;
        $("#cont1").empty().append(htmlStr);
    },'json');

    $("#cont2").empty().append("This is Content area 2 for id " + item.id);
    $("#cont2").append("<br>SSH " + item.id + " has been clicked and actived");
    var i = item.id;
    $("#cont2").append("<div id='container' style='margin:10px 15%;'> <script type='text/javascript'> draw_pic(i) </script></div>");
}