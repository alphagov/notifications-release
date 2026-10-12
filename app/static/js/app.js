import { initAll } from "../govuk/govuk-frontend.min.js";

const addJsEnabledClass = () => {
    document.body.className += ' js-enabled' + ('noModule' in HTMLScriptElement.prototype ? ' govuk-frontend-supported' : '');
};

addJsEnabledClass();
initAll();
