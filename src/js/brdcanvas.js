var PIN_WIDTH = 200;
var PIN_HEIGHT = 200;
var CANVAS_HEIGHT = 480;
var CANVAS_WIDTH = 854;

var theCanvas;
var ctx;
var boardID;
var theBoard;
var dragPin;
var selectedCorners = new Array();
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

	if (theBoard.xValues.length == 0) {
		for (var i = 0; i < theBoard.pins.length; i++) {

			theBoard.pins[i].x = ((i * 200) + "")
			theBoard.pins[i].y = "0";

			loopPin = theBoard.pins[i];

			theBoard.xValues[i] = loopPin.x;
			theBoard.yValues[i] = loopPin.y;
			drawPin(loopPin);
		} 
	}

	else {
		for (var i = 0; i < theBoard.pins.length; i++) {

			theBoard.pins[i].x = theBoard.xValues[i];
			theBoard.pins[i].y = theBoard.yValues[i];

			loopPin = theBoard.pins[i];
			drawPin(loopPin);
		} 
	}
}

function drawPin(thePin) {

	var img = new Image();
	img.onload = function(){
		ctx.drawImage(img, eval(thePin.x), eval(thePin.y), thePin.width, thePin.height);
	};
	img.src = thePin.imgUrl;
	img.setAttribute("pinid", thePin.id);
	img.setAttribute("x", thePin.x);
	img.setAttribute("y", thePin.y);
	thePinImages.push(img);
}

function handleMouseDown(event) {

	console.log("Mouse down.");
	if (dragPin != null) {
		var click = new Vector(event.offsetX, event.offsetY);
		checkResizeCorners(click)
	}
	dragPin = null;
	if (validClick(event.offsetX, event.offsetY) == true) {
		theCanvas.addEventListener('mousemove', handleDrag);
	}
}

function checkResizeCorners(mouseClick) {
	
	for(var i = 0; i < selectedCorners.length; i++) {
		
		
	}
}

var dragOffset;
function validClick(mouseX, mouseY) {

	var loopPin;
	var loadCoord;

	for (var i = 0; i < thePinImages.length; i++) {

		loopPin = thePinImages[i];
		loadCoord = new Vector(eval(thePinImages[i].getAttribute('x')),eval(thePinImages[i].getAttribute('y')));

		if ((mouseX < ((loadCoord.x + loopPin.width))) && (mouseX > loadCoord.x)) {
			if ((mouseY > loadCoord.y) && (mouseY < (loadCoord.y + loopPin.height))) {
				console.log("Valid click");

				dragOffset = new Vector(mouseX, mouseY);
				dragOffset = dragOffset.subtract(loadCoord);
				dragPin = loopPin;
				setupResize();
				return true;
			}
		}
	}
	return false;
}

// Where the image is  0******1
//					   2******3
function setupResize() {
	
	var topLeft = new Vector(eval(dragPin.getAttribute('x')), eval(dragPin.getAttribute('y')));
	var topRight = topLeft.add(new Vector(dragPin.width, 0));
	var bottomLeft = topLeft.add(new Vector(0, dragPin.height));
	var bottomRight = topLeft.add(new Vector(dragPin.width, dragPin.height));
	
	selectedCorners[0] = topLeft;
	selectedCorners[1] = topRight;
	selectedCorners[2] = bottomLeft;
	selectedCorners[3] = bottomRight;
}

function handleDrag(event) {

	console.log("Dragging!");

	var mouseCoord = new Vector(event.offsetX, event.offsetY);
	var imageCoord = new Vector(0, 0);

	var loopImage;
	for (var i = 0; i < thePinImages.length; i++) {
		if (dragPin.getAttribute("pinid") == thePinImages[i].getAttribute("pinid")) {

			imageCoord = mouseCoord.subtract(dragOffset);
			thePinImages[i].setAttribute('x', imageCoord.x);
			thePinImages[i].setAttribute('y', imageCoord.y);
			dragPin = thePinImages[i];
		}
	}
	updateCanvas();
}

function handleMouseUp(event) {
	console.log("Mouse released.");

	if (dragPin != null) {
		for (var i = 0; i < theBoard.pins.length; i++) {

			if (dragPin.getAttribute("pinid") == theBoard.pins[i].id) {

				theBoard.xValues[i] = dragPin.getAttribute('x');
				theBoard.yValues[i] = dragPin.getAttribute('y');

				updateDatastore();
			}
		}
		theCanvas.removeEventListener('mousemove', handleDrag);
	}
}

function updateCanvas() {
	ctx.clearRect(0,0, CANVAS_WIDTH, CANVAS_HEIGHT);
	
	var loopImage;
	for (var i = 0; i < thePinImages.length; i++) {
		loopImage = thePinImages[i];
		ctx.drawImage(loopImage, loopImage.getAttribute('x'), loopImage.getAttribute('y'), loopImage.width, loopImage.height);
		setupResize();
		drawSelectors();
	}
}

function drawSelectors() {
	for (var i = 0; i < selectedCorners.length; i++) {
		ctx.beginPath();
		ctx.arc(selectedCorners[i].x, selectedCorners[i].y, 10, 0, 2 * Math.PI, false);
		ctx.fillStyle = 'grey';
		ctx.fill();
	}
}

function updateDatastore() {

	$.ajax('/board/' + boardID, {
		type: 'POST',
		data: {
			updateX: JSON.stringify(theBoard.xValues),
			updateY: JSON.stringify(theBoard.yValues)
		},
		success: function() {
			console.log("Updated board datastore.")
		},
		error: function() {
			console.log('Error at server:');
		},
	});
}