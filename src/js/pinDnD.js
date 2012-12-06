function handleFileSelect(evt) {
	evt.stopPropagation();
	evt.preventDefault();

	var files = evt.dataTransfer.files; // FileList object.

	var output = [];
	theFile = files[0];
	/*	output.push('<li><strong>', escape(f.name), '</strong> (', f.type || 'n/a', ') - ',
			f.size, ' bytes, last modified: ',f.lastModifiedDate ? f.lastModifiedDate.toLocaleDateString() : 'n/a', '</li>');*/

	var reader = new FileReader();
	reader.readAsDataURL(theFile);
	
	reader.onload = function () {
		var img = new Image();
		img.style.maxWidth = "200px";
		img.style.maxHeight = "200px";
		img.file = theFile;
		img.src = this.result;
		document.getElementById("imageArea").innerHTML = "";
		document.getElementById("imageArea").appendChild(img);
	}
}

function handleDragOver(evt) {
	evt.stopPropagation();
	evt.preventDefault();
	evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
}

var theFile;
var dropZone;

$(document).ready(function() {
	console.log("ready");
	dropZone = document.getElementById('drop_zone');
	dropZone.addEventListener('dragover', handleDragOver, false);
	dropZone.addEventListener('drop', handleFileSelect, false);
	console.log("hello!?");
});