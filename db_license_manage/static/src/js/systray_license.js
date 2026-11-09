/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class LicenseSystray extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            show: false,
            status: "valid",
            message: "",
            days: 0,
            expiration_date: "",
        });

        onWillStart(async () => {
            try {
                const result = await this.rpc("/db_license_manage/status");
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
