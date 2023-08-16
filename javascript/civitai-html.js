"use strict";

function select_model(model_name) {
	console.log(model_name);
	let flag = model_name.split(':');
	switch (flag[0]) {
		case 'Index':
			let model_dropdown = gradioApp().querySelector('#eventtext1 textarea');
			if (model_dropdown && model_name) {
				model_dropdown.value = model_name;
				updateInput(model_dropdown);
			}
			break;
	}
}
