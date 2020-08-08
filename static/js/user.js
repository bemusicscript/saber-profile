$( document ).ready(function() {


    $("#acc_graph").percircle({percent: 0, text: " "});
    set_level_exp();
    set_pp();
    set_count();

});

function to_comma_split(int_value){
    return int_value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function set_pp(){
    var pp_graph = $("#pp_graph");
    var pp = pp_graph.attr("pp");
    var predict_min_pp = pp_graph.attr("prdct_min_pp");
    var predict_max_pp = pp_graph.attr("prdct_max_pp");
    var exp_pct = ((pp-predict_min_pp)/(predict_max_pp-predict_min_pp) * 100).toFixed(2);
    pp_graph.percircle({
        percent: exp_pct, text: " "
    });
}

function set_level_exp(){
    var lv_graph = $("#level_graph");
    var lv = lv_graph.attr("lv");
    var min = lv_graph.attr("min");
    var max = lv_graph.attr("max");
    var exp = lv_graph.attr("exp");
    if(lv == "100"){
        var exp_pct = 100;
    }
    else{
        var exp_pct = ((exp-min)/(max-min) * 100).toFixed(2);
    }
    lv_graph.percircle({percent: exp_pct, text: " "});
    $("#level_graph>span>.sub_desc").text(
        "(Exp: " + to_comma_split(exp) + ")"
    );
}

function set_count(){
    var cnt_graph = $("#count_graph");
    var total_cnt = cnt_graph.attr("total");
    var ranked_cnt = cnt_graph.attr("ranked")
    var exp_pct = (ranked_cnt * 100) / total_cnt;
    cnt_graph.percircle({percent: exp_pct, text: " "});
}


function set_score_count(){
    console.log(parseFloat($(".scores .ranked").attr("accuracy")).toFixed(2));
    $(".scores .ranked").text(
        "Ranked Score: " +
        to_comma_split( $(".scores .ranked").attr("score") +
        " (" +
        parseFloat($(".scores .ranked").attr("accuracy")).toFixed(2) +
        "%)")
    );
    $(".scores .total").text(
        "Total Score: " + to_comma_split( $(".scores .total").attr("score") )
    );
    $(".count .ranked").text(
        "Ranked Play Count: " + to_comma_split( $(".count .ranked").attr("count") )
    );
    $(".count .total").text(
        "Total Play Count: " + to_comma_split( $(".count .total").attr("count") )
    );

}

function create_share_icons(){
    var contents = "<i class=\"hovicon small effect-1 sub-a share twitter_btn\"><b class=\"icon-twitter\"></b></i>\
                    <i class=\"hovicon small effect-1 sub-a share link_copy\"><b class=\"icon-link\"></b></i>\
                    <i class=\"hovicon small effect-1 sub-a share image_save\"><b class=\"icon-save\"></b></i>";
    $('.icon_tab').append(contents);
    $(".profile_div").show();

     $('[data-toggle="tooltip"]').tooltip();
}

$(document).on('click','.twitter_btn',function(){
    player_id = $(".icon_tab").attr('id');
    text = "MY%20BEATSABER%20PROFILE%21%20%3A%29%20%23SABER_PROFILE%20"
    text += "https://bs.slime.kr/u/" + player_id;
    window.open("https://twitter.com/intent/tweet?text="+text);
});

$(document).on('click','.link_copy',function(){
    var tmp_ele = document.createElement('textarea');
    var text = "https://bs.slime.kr/u/" + $(".icon_tab").attr('id');
    tmp_ele.value = text;
    document.body.appendChild(tmp_ele);
    tmp_ele.select();
    document.execCommand("copy");
    document.body.removeChild(tmp_ele);
    alert("Your profile link has been copied :)");
});

$(document).on('click','.image_save',function(){
    var image_path = $(".profile_image>img").attr('src');
    fetch(image_path)
    .then(resp => resp.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = "profile_"+image_path.replace(/^.*[\\\/]/, '');
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
    .catch(() => alert('Download failed :('));

});

am4core.ready(function() {
    am4core.useTheme(am4themes_animated);

    var chart = am4core.create("chartdiv", am4charts.XYChart);
    chart.numberFormatter.numberFormat = "'#'#.";
    chart.colors.step = 1;

    var chartData = [];
    var history = $(".rank_graph").attr('history').split(',');
    var hist_len = history.length;

    today = new Date();
    for(i=0; i<hist_len;i++){
        _rel_value = hist_len - i;
        _rel_day = new Date(today);
        _rel_day.setDate(today.getDate() - _rel_value + 1);

        chartData.push({
            date: _rel_day,
            rank: parseInt(history[i], 10)
        });
    }
    chart.data = chartData;

    // Create axes
    var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
    dateAxis.renderer.minGridDistance = 50;

    // Create series
    function createAxisAndSeries(field, name, opposite) {
        var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
        valueAxis.renderer.inversed = true;
        if(chart.yAxes.indexOf(valueAxis) != 0){
            valueAxis.syncWithAxis = chart.yAxes.getIndex(0);
        }
        valueAxis.renderer.labels.template.fill = am4core.color("#FFF");
        dateAxis.renderer.labels.template.fill = am4core.color("#FFF");

        var series = chart.series.push(new am4charts.LineSeries());
        series.dataFields.valueY = field;
        series.dataFields.dateX = "date";
        series.strokeWidth = 2;
        series.name = field;
        series.tooltipText = "{name}: [bold]{valueY}[/]";
        series.tensionX = 0.8;
        series.showOnInit = true;
    }
    createAxisAndSeries("rank");

    // Add cursor
    chart.cursor = new am4charts.XYCursor();



}); // end am4core.ready()