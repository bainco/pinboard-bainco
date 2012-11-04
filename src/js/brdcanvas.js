var theCanvas;
var ctx;
var boardID;
var theBoard;
var PIN_WIDTH = 200;
var PIN_HEIGHT = 200;
var CANVAS_HEIGHT = 480;
var CANVAS_WIDTH = 854;

$(document).ready(function() {
	console.log("ready");
	theCanvas = document.getElementById("canvas");
	boardID = theCanvas.getAttribute("boardid");

	initialize();
});

function initialize() {
	$.ajax('/board/' + boardID, {
		type: 'GET',
		data: {
			fmt: 'json'
		},
		success: function(data) {
			theBoard = data;
			console.log('Board Loaded:');
			console.log(theBoard);
		},
		error: function() {
			console.log('Error at server:');
		},
		complete: setupCanvas
	});
}

function setupCanvas() {

	console.log("Setting up the canvas.")
	ctx = theCanvas.getContext('2d');
	theCanvas.addEventListener('mousedown', handleMouseDown);
	theCanvas.addEventListener('mouseup', handleMouseUp)
	
	var loopPin;
	for (var i = 0; i < theBoard.pins.length; i++) {
		
		loopPin = theBoard.pins[i];
		drawPin(loopPin);
	}
}

function drawPin(thePin) {
	var img = new Image();
	img.onload = function(){
		ctx.drawImage(img, 0, 0, PIN_WIDTH, PIN_HEIGHT);
	};
	img.src = thePin.imgUrl;
	img.alt = thePin.id;
}

function handleMouseDown(event) {

	console.log("Mouse down.");
	theCanvas.addEventListener('mousemove', handleDrag);
}

function handleMouseUp(event) {
	console.log("Mouse released.");
	theCanvas.removeEventListener('mousemove', handleDrag);
}

function handleDrag(event) {
	
	console.log("Dragging!");
}