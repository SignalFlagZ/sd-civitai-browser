"use strict";

function select_model(model_name) {
	console.log(model_name)
	let model_dropdown = gradioApp().querySelector('#quicksettings1 input');
	if (model_dropdown && model_name) {
		model_dropdown.value = JSON.stringify(model_name);
		model_dropdown.dispatchEvent(new Event("select"));
	}
}
