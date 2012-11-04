var PIN_WIDTH = 200;
var PIN_HEIGHT = 200;
var CANVAS_HEIGHT = 480;
var CANVAS_WIDTH = 854;

var theCanvas;
var ctx;
var boardID;
var theBoard;
var dragPin;
var thePinImages = new Array();

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

		theBoard.pins[i].x = (i * 200)
		theBoard.pins[i].y = 0;
		loopPin = theBoard.pins[i];
		drawPin(loopPin);
	}
}

function drawPin(thePin) {

	var img = new Image();
	img.onload = function(){
		ctx.drawImage(img, thePin.x, thePin.y, PIN_WIDTH, PIN_HEIGHT);
	};
	img.src = thePin.imgUrl;
	img.setAttribute("pinid", thePin.id);
	img.setAttribute("x", thePin.x);
	img.setAttribute("y", thePin.y);
	thePinImages.push(img);
}

function handleMouseDown(event) {

	console.log("Mouse down.");
	if (validClick(event.offsetX, event.offsetY) == true) {
		theCanvas.addEventListener('mousemove', handleDrag);
	}
}

function validClick(mouseX, mouseY) {

	var loopPin;
	var loadX;
	var loadY;

	for (var i = 0; i < thePinImages.length; i++) {

		loopPin = thePinImages[i];
		loadX = eval(thePinImages[i].getAttribute('x'));
		loadY = eval(thePinImages[i].getAttribute('y'));

		if ((mouseX < ((loadX + 200))) && (mouseX > loadX)) {
			if ((mouseY > loadY) && (mouseY < (loadY + 200))) {
				console.log("Valid click");
				dragPin = loopPin;
				return true;
			}
		}
	}
	return false;
}
function handleMouseUp(event) {
	console.log("Mouse released.");
	//STUB: send to server
	dragPin = null;
	theCanvas.removeEventListener('mousemove', handleDrag);
}

function handleDrag(event) {

	console.log("Dragging!");
	ctx.clearRect(0,0, CANVAS_WIDTH, CANVAS_HEIGHT);
	var loopImage;
	for (var i = 0; i < thePinImages.length; i++) {
		if (dragPin.getAttribute("pinid") == thePinImages[i].getAttribute("pinid")) {
			thePinImages[i].setAttribute('x', event.offsetX);
			thePinImages[i].setAttribute('y', event.offsetY);;
		}
	}
	updateCanvas();
}

function updateCanvas() {

	var loopImage;
	for (var i = 0; i < thePinImages.length; i++) {

		loopImage = thePinImages[i];
		ctx.drawImage(loopImage, loopImage.getAttribute('x'), loopImage.getAttribute('y'), PIN_WIDTH, PIN_HEIGHT);
	}
}