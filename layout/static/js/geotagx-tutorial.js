/*
 * The GeoTag-X tutorial helper.
 */
(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The tutorial API.
	var shortName_; // The project's short name.

	/**
	 * Begins the project tutorial.
	 * @param shortName the project's short name.
	 * @param getNextQuestion a user-defined function that returns the id of the next question to present to the user.
	 * @param assertions a graph that dictates the expected results and the messages displayed to a user.
	 */
	api_.start = function(shortName, getNextQuestion, assertions){
		if ($.type(shortName) !== "string"){
	        console.log("[geotagx::project::start] Error! Invalid project slug.");
	        return;
	    }
		shortName_ = shortName;

		assertions = {
			1:{
				expects:"yes",
				default_message:"Try again. If you are not sure what to look for, check out the help for more information.",
				messages:{
					"yes":"Well done! There is an animal in this photo.",
					"no":"Try again. Are you sure there is no animal? Check out the help for information on what you should be looking for."
				}
			}
		};


		geotagx.questionnaire.onGetNextQuestion(getNextQuestion);
		geotagx.questionnaire.onAnswerSubmitted(function(answer, $submitter, question){
			answer = answer.toLowerCase(); // toLowerCase for case-insensitive comparisons.

			var assertion = assertions[1];
			var message = assertion.messages[answer] ? assertion.messages[answer] : assertion.default_message;
			var isExpectedAnswer = answer === assertion.expects;

			showMessageBox(message, isExpectedAnswer);
		});

		$(".show-on-task-loaded").removeClass("show-on-task-loaded").hide().fadeIn(200);
		$(".hide-on-task-loaded").hide();

		geotagx.questionnaire.start(1);
	};


	function showMessageBox(message, isExpected){
		var $box = $("#tutorial-message-box");

		$box.removeClass("hide").hide();
		if (isExpected){
			$box.addClass("expected");
			$("#tutorial-success-message").html(message);
		}
		else {
			$box.removeClass("expected");
			$("#tutorial-failure-message").html(message);
		}
		$box.fadeIn(300);
	}

	function hideMessageBox(){
		$("#tutorial-message-box").fadeOut(300, function(){
			$(this).addClass("hide");
		})
	}







	$(document).ready(function(){



		function reset_answer_popup(){
			$(".answer_yes_popup").hide();
			$(".answer_no_popup").hide();
			$(".answer_unknown_popup").hide();
		}

		$(".answer_yes").click(function(){
			reset_answer_popup();
			$(".answer_yes_popup",$current).show();
		});
		$(".answer_no").click(function(){
			reset_answer_popup();
			$(".answer_no_popup",$current).show();
		});
		$(".answer_unknown").click(function(){
			reset_answer_popup();
			$(".answer_unknown_popup",$current).show();
		});

		reset_answer_popup();
	});


















	// Expose the API.
	geotagx.tutorial = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
