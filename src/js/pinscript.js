$(document).ready(function() {
	console.log("ready");

	$('.editable').on("click", handleEditClick);	
	$('.editable').hover(hoverOver, hoverOut);
	$('#private').on("click", handleCheckClick);
	$('#test').on("click", handleTestClick);
});

function hoverOver(e) {

	$(this).addClass("hover");
}

function hoverOut(e) {

	$(this).removeClass("hover");
}

function handleTestClick(e) {
	var pinID = document.getElementById("pinID").value;
	$.ajax('/pin', {
		type: 'GET',
		data: {
			fmt: 'json'
		},
		success: function(pins){		
			for(i = 0; i < pins.length; i++) {
				pin = pins[i];
				console.log("Pin Id:" + pin.id)
			}
			console.log('Update posted.');
		},
		error: function() {
			console.log('Error at server:');
		}
	});
}

function handleCheckClick(e) {
	var pinID = document.getElementById("pinID").value;
	$.ajax('/pin/' + pinID, {
		type: 'POST',
		data: {
			privOpt: this.checked
		},
		success: function(){			
			console.log('Update posted.');
		},
		error: function() {
			console.log('Error at server:');
		}
	});
}

function handleSubmit(e) {
	var keypressed = event.keyCode || event.which;
	if (keypressed == 13) {

		noEdit = document.createElement("span");
		noEdit.id = this.id;
		noEdit.innerText = this.value;
		$(noEdit).addClass("editable");
		$(this).replaceWith(noEdit); 
		
		$('.editable').on("click", handleEditClick);	
		$('.editable').hover(hoverOver, hoverOut);
		
		var pinID = document.getElementById("pinID").value;

		$.ajax('/pin/' + pinID, {
			type: 'POST',
			data: {
				caption: this.value
			},
			success: function(){			
				console.log('Update posted.');
			},
			error: function() {
				console.log('Error at server:');
			}
		});
	}
}

function handleEditClick(e) {

	edit = document.createElement("input");
	edit.id = this.id;
	edit.type = "text";
	edit.value = this.innerText;
	$(this).replaceWith(edit);

	$('#' + edit.id).on("keydown", handleSubmit)
}
