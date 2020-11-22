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
                console.log($("#myCard").attr("class"));
            }
        }
    }
    showContent(data);
}


function showContent(data){ 
    var deviceDesc = data.getAttribute("data-desc");
    var deviceIp = data.getAttribute("data-ip");
    var deviceOs =data.getAttribute("data-os");
    var deviceUser = data.getAttribute("data-user");
    $("#cont1").empty().append("<table class='table'><tr><th colspan='8'>device " + data.id + "info</th></tr></thead>");
    $("#cont1").append("<tbody><tr><th>Name</th><td>" + data.innerText + "</td><th>OS</th><td>" + deviceOs + "</td></tr><tr><th>IP</th><td>" + deviceIp + "</td><th>User</th><td>" + deviceUser + "</td></tr>");
    $("#cont2").empty().append("<th>Desc:</th><td>" + deviceDesc + "</td>");
    var i = data.id;
    $("#cont2").append("<div id='container' style='margin:10px 15%;'> <script type='text/javascript'> draw_pic(i) </script></div>");
}

function draw_pic(dev_id){
    $(function () {
        $('#container').bind('mousemove touchmove touchstart', function (e) {
                    var chart,
                        point,
                        i,
                        event;
                    for (i = 0; i < Highcharts.charts.length; i = i + 1) {
                        chart = Highcharts.charts[i];
                        event = chart.pointer.normalize(e.originalEvent); // Find coordinates within the chart
                        point = chart.series[0].searchPoint(event, true); // Get the hovered point
                        if (point) {
                            point.highlight(e);
                        }
                    }
            });
                /**
                 * 重写内部的方法， 这里是将提示框即十字准星的隐藏函数关闭
                 */
                Highcharts.Pointer.prototype.reset = function () {
                    return undefined;
                };
                /**
                 * 高亮当前的数据点，并设置鼠标滑动状态及绘制十字准星线
                 */
                Highcharts.Point.prototype.highlight = function (event) {
                    this.onMouseOver(); // 显示鼠标激活标识
                    this.series.chart.tooltip.refresh(this); // 显示提示框
                    this.series.chart.xAxis[0].drawCrosshair(event, this); // 显示十字准星线
                };
                /**
                 * 同步缩放效果，即当一个图表进行了缩放效果，其他图表也进行缩放
                 */
                function syncExtremes(e) {
                    var thisChart = this.chart;
                    if (e.trigger !== 'syncExtremes') {
                        Highcharts.each(Highcharts.charts, function (chart) {
                            if (chart !== thisChart) {
                                if (chart.xAxis[0].setExtremes) {
                                    chart.xAxis[0].setExtremes(e.min, e.max, undefined, false, { trigger: 'syncExtremes' });
                                }
                            }
                        });
                    }
                }
                Highcharts.setOptions({
                    global:{
                        useUTC: false
                    }
                });

                // 获取 JSON 数据，数据文件地址：
                $.getJSON("detail_json/"+dev_id, function (activity) {
                    $.each(activity.datasets, function (i, dataset) {
                        // 添加 X 数据
                        dataset.data = Highcharts.map(dataset.data, function (val, j) {
                            return [activity.xData[j], val];
                        });
                        $('<div style="height:220px;">')
                            .appendTo('#container')
                            .highcharts({
                                chart: {
                                    marginLeft: 60, // Keep all charts left aligned
                                    spacingTop: 20,
                                    spacingBottom: 20,
                                    zoomType: 'x'
                                },
                                title: {
                                    text: dataset.name + '趋势图(最近1天)',
                                    style: {
                                        fontSize: "14px"
                                    },
                                    align: 'left',
                                    margin: 0,
                                    x: 50
                                },
                                credits: {
                                    enabled: false
                                },
                                legend: {
                                    enabled: false
                                },
                                xAxis: {
                                    type: 'datetime',
                                    crosshair: true,
                                    events: {
                                        setExtremes: syncExtremes
                                    },
                                },
                                yAxis: {
                                    title: {
                                        text: null
                                    }
                                },
                                tooltip: {
                                    formatter: function(){
                                        return '<b>' + this.series.name + '</b><br/>' +
                                            Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                                            Highcharts.numberFormat(this.y, dataset.valueDecimals) + ' ' + dataset.unit;
                                    }
                                },
                                series: [{
                                    data: dataset.data,
                                    name: dataset.name,
                                    type: dataset.type,
                                    color: Highcharts.getOptions().colors[i],
                                    fillOpacity: 0.3,
                                }]
                            });
                    });
                });
    });
}

function updown(a){
    if(a=="down"){
        $("#up").hide();
        $("#down").show();
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
    else{
        $("#up").show();
        $("#down").hide();
        $("button.btn").each(function(){
            this.hidden=false;
        });
    }
}

