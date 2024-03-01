#!/usr/bin/env python
# main controller
import web
import json

import model.constant
import model.service

urls = (
    '/', 'Index',
    '/compare', 'Compare',
    '/save_ds', 'SaveDS',
    '/delete_ds', 'DeleteDS',
    '/view_result', 'ViewResult',
    '/delete_result', 'DeleteResult',
    '/view_result_detail', 'ViewResultDetail',
    '/save_vr', 'SaveVR'
)

render = web.template.render('templates/', base='page')

#global compared result for saving
g_compared_result = None


class Index:
    def GET(self):
        i = web.input(db_type=model.constant.DB_TYPE_ORACLE)
        db_type = i.db_type
        if db_type == model.constant.DB_TYPE_ORACLE:
            port = 1521
        if db_type == model.constant.DB_TYPE_SQLSERVER:
            port = 1433
        results = model.service.get_data_source(db_type)
        ds = json.dumps(list(results))
        return render.index(db_type, port, ds)

    def POST(self):
        return self.GET()


class Compare:
    def POST(self):
        i = web.input()
        global g_compared_result
        g_compared_result = model.service.do_compare(i)
        return render.compare(g_compared_result)


class SaveDS:
    def POST(self):
        i = web.input()
        model.service.save_data_source(i)
        results = model.service.get_data_source(i.db_type)
        return json.dumps(list(results))


class DeleteDS:
    def POST(self):
        i = web.input()
        model.service.delete_data_source(i.name);
        results = model.service.get_data_source(i.db_type)
        return json.dumps(list(results))


class ViewResult:
    def POST(self):
        results = model.service.get_compared_result()
        return render.history(results)


class DeleteResult:
    def POST(self):
        i = web.input()
        model.service.delete_compared_result(i.id)
        return ViewResult().POST()


class ViewResultDetail:
    def POST(self):
        i = web.input()
        compared_result = model.service.get_compared_result_detail(i.id)
        return render.compare(compared_result['CONTENT'], compared_result)


class SaveVR:
    def POST(self):
        i = web.input()
        model.service.save_compared_result(i.memo, g_compared_result)
        return json.dumps('')


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
