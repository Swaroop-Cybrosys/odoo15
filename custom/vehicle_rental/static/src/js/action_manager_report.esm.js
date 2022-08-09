/** @odoo-module **/

import {download} from "@web/core/network/download";
import {registry} from "@web/core/registry";
import framework from 'web.framework';
import session from 'web.session';

registry
    .category("ir.actions.report handlers")
    .add("xlsx_handler", async function (action) {
        if (action.report_type === 'xlsx') {
    	framework.blockUI({ message: '<h1> Just a moment...</h1>' });
    	var def = $.Deferred();
    	session.get_file({
        	url: '/xlsx_reports',
        	data: action.data,
        	success: def.resolve.bind(def),
        	complete: framework.unblockUI,
    	});
    	return def;
	}
})