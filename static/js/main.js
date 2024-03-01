var g_ds;
var g_port;

function initPort(port) {
    g_port = port;    
}

function doCompare() {
    $("#form1").attr("action", "compare");
    $("#form1").attr("target", "_blank");
    if ($("#form1").valid()) {
        //$.blockUI();
        $('#form1').submit();
    }
}

function doCompareData() {
    $("#form1").attr("action", "compare_data");
    $("#form1").attr("target", "_blank");
    if ($("#form1").valid()) {
        $('#form1').submit();
    }    
}

function doSavingResult() {
    var memo = prompt('Add Notes:');
    if(memo == '' || memo == null) {
        return;    
    }
    $.post('save_vr', {memo:memo}, function(data) {
        alert("Saving Successful");
    });    
}

function doView() {
    $("#form1").attr("action", "view_result");
    $("#form1").attr("target", "_blank");
    $('#form1').submit();
}

function doViewDetailResult(id) {
    $("#form1").attr("action", "view_result_detail");
    $("#form1").attr("target", "_self");
    document.form1.id.value = id;
    $('#form1').submit();  	 
}

function doDeleteResult(id) {
    if(confirm('Really delete?')) {
		    $("#form1").attr("action", "delete_result");
		    $("#form1").attr("target", "_self");
		    document.form1.id.value = id;
		    $('#form1').submit();     	
    }
}

function doSave(dsId) {
    //it is a new datasource
    var value = ui().getSelectedValue(dsId);
    var param = {};
    var name;
    if(value == '-1') {
        name = prompt('Please input name:');
        if(name == '' || name == null) {
            return;    
        }
    }
    else {
        name = value;
    }
    param.name = name;
    param.db_type = $("#form1 :radio:checked").val();
    if(dsId == 'ownerDS') {
        param.host_name = document.form1.owner_host_name.value;
        param.db_name = document.form1.owner_db_name.value;
        param.user_name = document.form1.owner_user_name.value;
        param.password = document.form1.owner_password.value;
        param.port = document.form1.owner_port.value;        
    }
    else {
        param.host_name = document.form1.target_host_name.value;
        param.db_name = document.form1.target_db_name.value;
        param.user_name = document.form1.target_user_name.value;
        param.password = document.form1.target_password.value;
        param.port = document.form1.target_port.value;
    }
    $.post('save_ds', param, function(data) {
        initDS(data);
        alert("Saving Successful");
    });
}

function doDelete(dsId) {
    var value = ui().getSelectedValue(dsId);
    var dbType = $("#form1 :radio:checked").val();
    if(value == '-1'){
        return;
    }
    if(confirm('Really delete?')) {
        $.post('delete_ds', {name:value, db_type:dbType}, function(data) {
            initDS(data);
            alert("Deleting Successful");
        });
    }
}

function initDS(data) {
    g_ds = ui().getJsonObject(data);
    refreshDataSource();
}

function refreshDataSource() {
    $('#ownerDS').empty();
    $('#ownerDS').append('<option value="-1">New DataSource</option>');
    for(i = 0; i < g_ds.length; i ++) {
        $('#ownerDS').append('<option value="' + g_ds[i].NAME + '">' + g_ds[i].NAME + '</option>');
    }
    $('#ownerDS').trigger('change');
    $('#targetDS').empty();
    $('#targetDS').append('<option value="-1">New DataSource</option>');
    for(i = 0; i < g_ds.length; i ++) {
        $('#targetDS').append('<option value="' + g_ds[i].NAME + '">' + g_ds[i].NAME + '</option>');
    }
    $('#targetDS').trigger('change');
}

function registerEvent(dsId) {
    $("#" + dsId).change(function() {
        var value = ui().getSelectedValue(dsId);
        if(value == '-1') {
            if(dsId == 'ownerDS') {
                document.form1.owner_host_name.value = '';
                document.form1.owner_db_name.value = '';
                document.form1.owner_user_name.value = '';
                document.form1.owner_password.value = '';
                document.form1.owner_port.value = g_port;
            }
            else {
                document.form1.target_host_name.value = '';
                document.form1.target_db_name.value = '';
                document.form1.target_user_name.value = '';
                document.form1.target_password.value = '';
                document.form1.target_port.value = g_port;
            }
        }
        for(i = 0; i < g_ds.length; i ++) {
            if(value == g_ds[i].NAME) {
                if(dsId == 'ownerDS') {
                    document.form1.owner_host_name.value = g_ds[i].HOST_NAME;
                    document.form1.owner_db_name.value = g_ds[i].DB_NAME;
                    document.form1.owner_user_name.value = g_ds[i].USER_NAME;
                    document.form1.owner_password.value = g_ds[i].PASSWORD;
                    document.form1.owner_port.value = g_ds[i].PORT;
                }
                else {
                    document.form1.target_host_name.value = g_ds[i].HOST_NAME;
                    document.form1.target_db_name.value = g_ds[i].DB_NAME;
                    document.form1.target_user_name.value = g_ds[i].USER_NAME;
                    document.form1.target_password.value = g_ds[i].PASSWORD;
                    document.form1.target_port.value = g_ds[i].PORT;
                }
                return;
            }
        }
    });
}

function changeDBType() {
    $("#form1").attr("action", "");
    $("#form1").attr("target", "_self");
    $('#form1').submit();  
}

function toggleSource(obj) {
    $(obj).next().toggle();
}
