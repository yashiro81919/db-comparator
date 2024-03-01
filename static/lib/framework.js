//UI common functionality
var ui = function() {
    return {
    //get Json Object
        getJsonObject:function (/*String*/jsonString) {
            return eval("(" + jsonString + ")");
        },
    //dynamic loading a page by a URL
        dynamicLoading:function (/*Jquery Object*/obj, /*String*/url, /*Object*/params, /*Function*/callback) {
            obj.html(UI_MESSAGE_LOADING);
            $.post(url, params, function(data) {
                obj.html(data);
                if (callback != undefined) {
                    callback();
                }
            });
            obj.ajaxError(function(event, request, settings) {
                obj.html(request.responseText);
            });
        },
    //refresh current page
        refreshPage:function() {
            window.location.reload();
        },
    //generate random number between 0 and 99999999
        randomId:function() {
            return Math.floor(Math.random() * 99999999 + 1);
        },
    //go to the url
        goUrl:function(/*String*/url) {
            window.location = url;
        },
    //show a dialog using browser's API(IE,firefox,Safari will use modalDialog, Opera will use open window)
        showDialog:function(/*String*/url, /*Function*/callback, /*Object*/option) {
            if (option == undefined || option == null) {
                option = new Object();
                option.height = 400;
                option.width = 600;
                option.left = 150;
                option.top = 200;
                option.modal = true;
            }
            if (option.modal && window.showModalDialog) {
                var flag = window.showModalDialog(url, window,
                        'edge: raised; center: yes; help: no; resizable: no; status: no; scroll: yes; ' +
                        'dialogHeight:' + option.height + 'px; ' +
                        'dialogWidth:' + option.width + 'px; ' +
                        'dialogLeft:' + option.left + 'px; ' +
                        'dialogTop:' + option.top + 'px;');
                if (flag === true) {
                    callback();
                }
            }
            else {
                window.open(url, '',
                        'height=' + option.height + ', ' +
                        'width=' + option.width + ', ' +
                        'top=' + option.top + ', ' +
                        'left=' + option.left + ', toolbar=no, menubar=no,' +
                        ' scrollbars=yes, resizable=no,location=no, status=no');
                $("head").append('<script type="text/javascript">var UI_DialogCallback = ' + callback.toString() + ';</script>');
            }
        },
    //get selected value from a Select element
        getSelectedValue:function(/*String*/selectId) {
            var obj = $('#' + selectId + ' option:selected');
            if(obj.length == 1) {
                return obj[0].value;    
            }
            var values = [];
            for(var i = 0; i < obj.length; i ++) {
                values[i] = obj[i].value;
            }
            return values;
        },
        //add one hidden element for a form
        addHiddenElement:function(/*String*/formId,/*String*/name,/*String*/value) {
            var jForm = $('#'+formId);
            var hiddenEl = jForm.get()[0][name];
            if(hiddenEl == null || hiddenEl == undefined) {
                jForm.append("<input type='hidden' name='"+name+"'>");
                hiddenEl = jForm.get()[0][name];
            }
            if(value != undefined && value != null) {
                hiddenEl.value=value;    
            }
        }
    };
};