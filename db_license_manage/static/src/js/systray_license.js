/** @odoo-module **/
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component, onWillStart, useState } from "@odoo/owl";

export class LicenseSystray extends Component {
    setup() {
        this.state = useState({
            show: false,
            status: "valid",
            message: "",
            days: 0,
            expiration_date: "",
        });

        onWillStart(async () => {
            try {
                const result = await rpc("/db_license_manage/status");
                this.state.show = true;
                this.state.status = result.status;
                this.state.message = result.message;
                this.state.days = result.days_remaining;
                this.state.expiration_date = result.expiration_date;
            } catch (e) {
                console.error("Failed to fetch license status", e);
            }
        });
    }
}
LicenseSystray.template = "db_license_manage.LicenseSystray";

export const systrayItem = {
    Component: LicenseSystray,
};

registry.category("systray").add("LicenseSystray", systrayItem, { sequence: 1 });
