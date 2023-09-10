"use strict";

function select_model(model_name) {
	console.log(model_name);
	//let flag = model_name.split(':');
	const regex1 = /(^Index)(\d):/;
	let match = regex1.exec(model_name)
	console.log(match)
	if (match[1] == 'Index') {
		let selector = '#eventtext' + match[2] + ' textarea'
		let model_dropdown = gradioApp().querySelector(selector);
		if (model_dropdown && model_name) {
			model_dropdown.value = model_name;
			updateInput(model_dropdown);
		}
	}
}

function trigger_event(element, event) {
	let myEvent = new Event(event);
	Object.defineProperty(myEvent, "target", { value: element });
	element.dispatchEvent(myEvent);
}

function copyInnerText(node) {
	if (node.nextSibling != null) {
		//let ret = navigator.clipboard.writeText(node.nextSibling.innerText;
		//alert("Copied infotext");
		let response = confirm("Send txt2img?");
		if (response) {
			let prompt = gradioApp().querySelector('#txt2img_prompt textarea');
			let paste = gradioApp().querySelector('#paste');
			prompt.value = node.nextSibling.innerText;
			trigger_event(prompt, "input");
			trigger_event(paste, "click");
		}
	}
}