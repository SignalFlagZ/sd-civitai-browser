"use strict";

function select_model(model_name) {
	console.log(model_name);
	//let flag = model_name.split(':');
	const regex1 = /(^Index)(\d):/;
	let match = regex1.exec(model_name);
	//console.log(match);
	if (match[1] == 'Index') {
		let selector = '#eventtext' + match[2] + ' textarea';
		let model_dropdown = gradioApp().querySelector(selector);
		if (model_dropdown && model_name) {
			model_dropdown.value = model_name;
			updateInput(model_dropdown);
		}
	}
}

function trigger_event(element, event) {
	let e = new Event(event);
	Object.defineProperty(e, "target", { value: element });
	//element.focus();
	element.dispatchEvent(e);
}
function trigger_key_down(element, key){
	let e = new KeyboardEvent("keydown", { key: key });
	//element.focus();
	element.dispatchEvent(e);
}

function copyInnerText(node) {
	if (node.nextSibling != null) {
		//let ret = navigator.clipboard.writeText(node.nextSibling.innerText;
		//alert("Copied infotext");
		let response = confirm("Send to txt2img?");
		if (response) {
			let prompt = gradioApp().querySelector('#txt2img_prompt textarea');
			let paste = gradioApp().querySelector('#paste');
			prompt.value = node.nextSibling.innerText;
			trigger_event(prompt, 'input');
			trigger_event(paste, 'click');
			//trigger_key_down(prompt, 'Escape');
		}
	}
}

function overwriteProperties(propertiesText) {
	//console.log(c);
	let p = propertiesText.split(';');
	querySelectSetProperty('.civmodelcard', '--civsfz-figcaption-background-color', p[0] + 'd9');
	querySelectSetProperty('.civmodelcard', '--civsfz-default-shadow-color', p[1] + 'f0');
	querySelectSetProperty('.civmodelcard', '--civsfz-alreadyhave-shadow-color', p[2] + 'f0');
	querySelectSetProperty('.civmodelcard', '--civsfz-hover-scale', p[3]); 
	querySelectSetProperty('.civmodelcard', '--civsfz-card-width', p[4]); 
	querySelectSetProperty('.civmodelcard', '--civsfz-card-height', p[5]); 

}

function querySelectSetProperty(q, p, c) {
	let elements = gradioApp().querySelectorAll(q);
	elements.forEach((elem) => {
		elem.style.setProperty(p, c);
	});

}