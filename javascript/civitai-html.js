"use strict";

function select_model(model_name) {
	console.log(model_name);
	//let flag = model_name.split(':');
	const regex1 = /(^Index)(\d):/;
	var match = regex1.exec(model_name)
	//console.log(match)
	if (match[1] == 'Index') {
		var selector = '#eventtext' + match[2] +' textarea'
		var model_dropdown = gradioApp().querySelector(selector);
		if (model_dropdown && model_name) {
			model_dropdown.value = model_name;
			updateInput(model_dropdown);
		}
	}
}

function copyInnerText(node) {
	if (node.nextSibling != null) {
		return navigator.clipboard.writeText(node.nextSibling.innerText).then(
			function () {
				alert("Copied infotext");
			}
		).catch(
			function (error) {
				alert((error && error.message) || "Failed to copy infotext");
			}
		)
	}
}