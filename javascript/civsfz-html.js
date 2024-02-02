"use strict";

onUiLoaded(civbrowser_start_it_up)
function civbrowser_start_it_up() {
	//make tab sticky
	let elem = gradioApp().querySelector('#civsfz_tab-element').firstChild;
	elem.classList.add("civsfz-sticky-element");
	elem.classList.add("civsfz-tabbar");
}

function civsfz_select_model(model_name) {
	console.log(model_name);
	// model_name-> selector:tab_id:
	const regex1 = /(^.+?)(\d):/;
	let match = regex1.exec(model_name);
	//console.log(match);
	if (match[1] == 'Index') {
		civsfz_scroll_to('#civsfz_model-data' + match[2]);
		let selector = '#civsfz_eventtext' + match[2] + ' textarea';
		let model_dropdown = gradioApp().querySelector(selector);
		if (model_dropdown && model_name) {
			/*Force card click event*/
			model_dropdown.value = model_name + ':' + civsfz_getRandomIntInclusive(0, 9999);
			updateInput(model_dropdown);
		}
	}
}

/*https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Math/random#%E5%8C%85%E6%8B%AC%E7%9A%84%E3%81%AB_2_%E3%81%A4%E3%81%AE%E5%80%A4%E3%81%AE%E9%96%93%E3%81%AE%E3%83%A9%E3%83%B3%E3%83%80%E3%83%A0%E3%81%AA%E6%95%B4%E6%95%B0%E3%82%92%E5%BE%97%E3%82%8B*/
function civsfz_getRandomIntInclusive(min, max) {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(Math.random() * (max - min + 1) + min); //The maximum is inclusive and the minimum is inclusive
}

function civsfz_trigger_event(element, event) {
	let e = new Event(event);
	Object.defineProperty(e, "target", { value: element });
	//element.focus();
	element.dispatchEvent(e);
}
function civsfz_trigger_key_down(element, key){
	let e = new KeyboardEvent("keydown", { key: key });
	//element.focus();
	element.dispatchEvent(e);
}

function civsfz_copyInnerText(node) {
	if (node.nextSibling != null) {
		//let ret = navigator.clipboard.writeText(node.nextSibling.innerText;
		//alert("Copied infotext");
		let response = confirm("Send to txt2img?");
		if (response) {
			let prompt = gradioApp().querySelector('#txt2img_prompt textarea');
			let paste = gradioApp().querySelector('#paste');
			if (paste == null) {
				//SD.Next
				paste = gradioApp().querySelector('#txt2img_paste');
			}
			prompt.value = node.nextSibling.innerText;
			civsfz_trigger_event(prompt, 'input');
			civsfz_trigger_event(paste, 'click');
			//trigger_key_down(prompt, 'Escape');
		}
	}
}

function civsfz_overwriteProperties(propertiesText) {
	//let propertiesText = gradioApp().querySelector('#' + elem_id + ' textarea').value;
	//console.log(elem_id, propertiesText)
	let p = propertiesText.split(';');
	civsfz_querySelectSetProperty('.civsfz-modelcardshtml', '--civsfz-figcaption-background-color', p[0] + 'd9');
	civsfz_querySelectSetProperty('.civsfz-modelcardshtml', '--civsfz-figcaption-sd2-background-color', p[1] + 'd9');
	civsfz_querySelectSetProperty('.civsfz-modelcardshtml', '--civsfz-figcaption-sdxl-background-color', p[2] + 'd9');
	civsfz_querySelectSetProperty('.civsfz-modelcardshtml', '--civsfz-default-shadow-color', p[3] + 'f0');
	civsfz_querySelectSetProperty('.civsfz-modelcardshtml', '--civsfz-alreadyhave-shadow-color', p[4] + 'f0');
	civsfz_querySelectSetProperty('.civsfz-modelcardshtml', '--civsfz-hover-scale', p[5]);
	civsfz_querySelectSetProperty('.civsfz-modelcardshtml', '--civsfz-card-width', p[6]);
	civsfz_querySelectSetProperty('.civsfz-modelcardshtml', '--civsfz-card-height', p[7]);

}

function civsfz_querySelectSetProperty(q, p, c) {
	let elements = gradioApp().querySelectorAll(q);
	elements.forEach((elem) => {
		elem.style.setProperty(p, c);
	});
}

function civsfz_scroll_to(q) {
	const elem = gradioApp().querySelector(q);
	elem.scrollIntoView({
		behavior: 'smooth',
		block: 'start',
		inline: 'nearest'
	});
}