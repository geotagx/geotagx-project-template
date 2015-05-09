/*
 * The GeoTag-X tutorial helper.
 */
(function(geotagx, $, undefined){
	"use strict";

	var api_ = {}; // The tutorial API.

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

		// The next question's identifier. This value is determined each time
		// a correct answer is input by the user.
		var nextQuestion = 0;

		// Override the showNextQuestion function so that instead of automatically
		// displaying the next question, a notification is displayed to the user.
		// A notification may contain a "NEXT" button which allows a user to
		// advance to the next question.
		geotagx.questionnaire.onShowNextQuestion(function(question, answer, $submitter){
			answer = $.type(answer) === "string" ? answer.toLowerCase() : answer; // toLowerCase for case-insensitive comparisons.

			var assertion = assertions[1]; //TODO Replace 1 with question when you've found a way to generate assertions.
			var message = assertion.messages[answer] ? assertion.messages[answer] : assertion.default_message;
			var isExpectedAnswer = answer === assertion.expects;
			if (isExpectedAnswer)
				nextQuestion = getNextQuestion(question, answer);

			showNotification(message, isExpectedAnswer);
		});

		$(".show-on-task-loaded").removeClass("show-on-task-loaded").hide().fadeIn(200);
		$(".hide-on-task-loaded").hide();
		$("#tutorial-next").on("click", function(){
			hideNotification();
			geotagx.questionnaire.showQuestion(nextQuestion);
		});

		geotagx.questionnaire.start(1);
		geotagx.analytics.start(shortName);
	};

	function showNotification(message, isExpected){
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

	function hideNotification(){
		$("#tutorial-message-box").fadeOut(300, function(){
			$(this).addClass("hide");
		})
	}

	// Expose the API.
	geotagx.tutorial = api_;
})(window.geotagx = window.geotagx || {}, jQuery);
