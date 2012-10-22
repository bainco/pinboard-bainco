
//function updateView() {
	//if myBoard.private {
		//$('#private').attr('checked',"");
//	}
//}

function getTheBoard() {
	var board;
	$.ajax('/board/' + boardID, {
		type: 'GET',
		data: {
			fmt: 'json'
		},
		success: function(data) {
			myBoard = data;
			console.log(myBoard);
			console.log('Board loaded.');
		},
		error: function() {
			console.log('Error at server:');
		}
	});
}

function getThePins() {
	$.ajax('/pin', {
		type: 'GET',
		data: {
			fmt: 'json'
		},
		success: function(data){			
			console.log('Pins loaded.');
			thePins = data;
		},
		error: function() {
			console.log('Error at server:');
		}
	});
}

function handleCheckClick(e) {
	console.log("Hello?");
	var boardID = document.getElementById("boardID").value;
	
	$.ajax('/board/' + boardID, {
		type: 'POST',
		data: {
			privOpt: this.checked
		},
		success: function(data){			
			console.log('Update posted.');
		},
		error: function() {
			console.log('Error at server:');
			
			alert("There was an error at the server, changes reverted!")
		}
	});
}

var boardPins;
var thePins;
var boardID;
var myBoard;

$(document).ready(function() {
	console.log("ready");
	boardID = document.getElementById("boardID").value;
	getTheBoard();
	$('#private').on("click", handleCheckClick);
	//Get the board!
	getTheBoard();
	getThePins();
	//updateView();
});


